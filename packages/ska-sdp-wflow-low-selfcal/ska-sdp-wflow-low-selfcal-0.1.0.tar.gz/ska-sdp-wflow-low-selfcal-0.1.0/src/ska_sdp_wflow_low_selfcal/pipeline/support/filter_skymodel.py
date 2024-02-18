#!/usr/bin/env python3

#  SPDX-License-Identifier: GPL-3.0-or-later

"""
Script to filter and group a sky model with an image
"""

# This file is originally copied from the Rapthor repository:
# https://git.astron.nl/RD/rapthor/-/tree/master/rapthor/scripts/filter_skymodel.py
import os
from ast import literal_eval

import astropy.io.ascii
import bdsf
import casacore.tables as pt
import lsmtool
import numpy as np
from astropy import wcs
from astropy.io import fits as pyfits

from ska_sdp_wflow_low_selfcal.pipeline.support.miscellaneous import (
    dec2ddmmss,
    ra2hhmmss,
    rasterize,
    read_vertices,
    string2bool,
    string2list,
)


def filter_skymodel(  # pylint: disable=R0913,R0914, R0912, R0915
    input_image,
    input_skymodel_pb,
    output_root,
    vertices_file,
    beam_ms,
    input_bright_skymodel_pb=None,
    threshisl=5.0,
    threshpix=7.5,
    rmsbox=(150, 50),
    rmsbox_bright=(35, 7),
    adaptive_rmsbox=True,
    use_adaptive_threshold=False,
    adaptive_thresh=75.0,
    comparison_skymodel=None,
    filter_by_mask=True,
    remove_negative=False,
):
    """
    Filter the input sky model

    Note: If no islands of emission are detected in the input image, a
    blank sky model is made. If any islands are detected in the input image,
    filtered true-sky and apparent-sky models are made, as well as a FITS clean
    mask (with the filename input_image+'.mask'). Various diagnostics are also
    derived and saved in JSON format.

    Parameters
    ----------
    input_image : str
        Filename of input image to use to detect sources for filtering.
        Ideally, this should be a flat-noise image (i.e., without primary-beam
        correction)
    input_skymodel_pb : str
        Filename of input makesourcedb sky model, with primary-beam correction
    output_root : str
        Root of filenames of output makesourcedb sky models and image
        diagnostics files. Output filenames will be
        output_root+'.apparent_sky.txt', output_root+'.true_sky.txt',
        and output_root+'.image_diagnostics.json'
    vertices_file : str
        Filename of file with vertices
    beam_ms : list of str
        The list of MS files to use to derive the beam attenuation and
        theorectical image noise
    input_bright_skymodel_pb : str, optional
        Filename of input makesourcedb sky model of bright sources only,
        with primary-beam correction
    threshisl : float, optional
        Value of thresh_isl PyBDSF parameter
    threshpix : float, optional
        Value of thresh_pix PyBDSF parameter
    rmsbox : tuple of floats, optional
        Value of rms_box PyBDSF parameter
    rmsbox_bright : tuple of floats, optional
        Value of rms_box_bright PyBDSF parameter
    adaptive_rmsbox : tuple of floats, optional
        Value of adaptive_rms_box PyBDSF parameter
    use_adaptive_threshold : bool, optional
        If True, use an adaptive threshold estimated from the negative values
        in the image
    adaptive_thresh : float, optional
        If adaptive_rmsbox is True, this value sets the threshold above
        which a source will use the small rms box
    comparison_skymodel : str, optional
        The filename of the sky model to use for flux scale and astrometry
        comparisons
    filter_by_mask : bool, optional
        If True, filter the input sky model by the PyBDSF-derived mask,
        removing sources that lie in unmasked regions
    remove_negative : bool, optional
        If True, remove negative sky model components
    """
    if rmsbox is not None and isinstance(rmsbox, str):
        rmsbox = literal_eval(rmsbox)
    if isinstance(rmsbox_bright, str):
        rmsbox_bright = literal_eval(rmsbox_bright)
    adaptive_rmsbox = string2bool(adaptive_rmsbox)
    use_adaptive_threshold = string2bool(use_adaptive_threshold)
    if isinstance(beam_ms, str):
        beam_ms = string2list(beam_ms)

    # Try to set the TMPDIR evn var to a short path, to ensure we do not hit
    # the length limits for socket paths (used by the mulitprocessing module).
    # We try a number of standard paths (the same ones used in the tempfile
    # Python library)
    try:
        old_tmpdir = os.environ["TMPDIR"]
    except KeyError:
        old_tmpdir = None
    for tmpdir in ["/tmp", "/var/tmp", "/usr/tmp"]:
        if os.path.exists(tmpdir):
            os.environ["TMPDIR"] = tmpdir
            break

    # Run PyBDSF to make a mask for grouping
    if use_adaptive_threshold:
        # Get an estimate of the rms by running PyBDSF to make an rms map
        img = bdsf.process_image(
            input_image,
            mean_map="zero",
            rms_box=rmsbox,
            thresh_pix=threshpix,
            thresh_isl=threshisl,
            thresh="hard",
            adaptive_rms_box=adaptive_rmsbox,
            adaptive_thresh=adaptive_thresh,
            rms_box_bright=rmsbox_bright,
            rms_map=True,
            quiet=True,
            stop_at="isl",
        )

        # Find min and max pixels
        max_neg_val = abs(np.min(img.ch0_arr))
        max_neg_pos = np.where(img.ch0_arr == np.min(img.ch0_arr))
        max_pos_val = abs(np.max(img.ch0_arr))
        max_pos_pos = np.where(img.ch0_arr == np.max(img.ch0_arr))

        # Estimate new thresh_isl from min pixel value's sigma, but don't let
        # it get higher than 1/2 of the peak's sigma
        threshisl_neg = 2.0 * max_neg_val / img.rms_arr[max_neg_pos][0]
        max_sigma = max_pos_val / img.rms_arr[max_pos_pos][0]
        if threshisl_neg > max_sigma / 2.0:
            threshisl_neg = max_sigma / 2.0

        # Use the new threshold only if it is larger than the user-specified
        # one
        if threshisl_neg > threshisl:
            threshisl = threshisl_neg

    img = bdsf.process_image(
        input_image,
        mean_map="zero",
        rms_box=rmsbox,
        thresh_pix=threshpix,
        thresh_isl=threshisl,
        thresh="hard",
        adaptive_rms_box=adaptive_rmsbox,
        adaptive_thresh=adaptive_thresh,
        rms_box_bright=rmsbox_bright,
        atrous_do=True,
        atrous_jmax=3,
        rms_map=True,
        quiet=True,
    )

    emptysky = False
    if img.nisl > 0:
        maskfile = input_image + ".mask"
        img.export_image(
            outfile=maskfile, clobber=True, img_type="island_mask"
        )

        # Construct polygon needed to trim the mask to the sector
        header = pyfits.getheader(maskfile, 0)
        w = wcs.WCS(header)  # pylint: disable=C0103
        ra_ind = w.axis_type_names.index("RA")
        dec_ind = w.axis_type_names.index("DEC")
        vertices = read_vertices(vertices_file)
        ra_verts = vertices[0]
        dec_verts = vertices[1]
        verts = []
        for ra_vert, dec_vert in zip(ra_verts, dec_verts):
            ra_dec = np.array([[0.0, 0.0, 0.0, 0.0]])
            ra_dec[0][ra_ind] = ra_vert
            ra_dec[0][dec_ind] = dec_vert
            verts.append(
                (
                    w.wcs_world2pix(ra_dec, 0)[0][ra_ind],
                    w.wcs_world2pix(ra_dec, 0)[0][dec_ind],
                )
            )

        hdu = pyfits.open(maskfile, memmap=False)
        data = hdu[0].data

        # Rasterize the poly
        data_rasertize = data[0, 0, :, :]
        data_rasertize = rasterize(verts, data_rasertize)
        data[0, 0, :, :] = data_rasertize

        hdu[0].data = data
        hdu.writeto(maskfile, overwrite=True)

        # Now filter the sky model using the mask made above
        if len(beam_ms) > 1:
            # Select the best MS for the beam attenuation
            ms_times = []
            for current_ms in beam_ms:
                tab = pt.table(current_ms, ack=False)
                ms_times.append(np.mean(tab.getcol("TIME")))
                tab.close()
            ms_times_sorted = sorted(ms_times)
            mid_time = ms_times_sorted[int(len(ms_times) / 2)]
            beam_ind = ms_times.index(mid_time)
        else:
            beam_ind = 0
        try:
            s_in = lsmtool.load(input_skymodel_pb, beamMS=beam_ms[beam_ind])
        except astropy.io.ascii.InconsistentTableError:
            emptysky = True
        if input_bright_skymodel_pb is not None:
            try:
                # If bright sources were peeled before imaging, add them back
                s_bright = lsmtool.load(
                    input_bright_skymodel_pb, beamMS=beam_ms[beam_ind]
                )

                # Rename the bright sources, removing the '_sector_*' added
                # previously (otherwise the '_sector_*' text will be added
                # every iteration, eventually making for very long source
                # names)
                new_names = [
                    name.split("_sector")[0]
                    for name in s_bright.getColValues("Name")
                ]
                s_bright.setColValues("Name", new_names)
                if not emptysky:
                    s_in.concatenate(s_bright)
                else:
                    s_in = s_bright
                    emptysky = False
            except astropy.io.ascii.InconsistentTableError:
                pass
        if not emptysky:
            # Keep only those sources with positive flux densities
            if remove_negative:
                s_in.select("I > 0.0")
            if s_in and filter_by_mask:
                # Keep only those sources in PyBDSF masked regions
                s_in.select(f"{maskfile} == True")
            if s_in:
                # Write out apparent- and true-sky models
                del img  # helps reduce memory usage
                s_in.group(maskfile)  # group the sky model by mask islands
                s_in.write(output_root + ".true_sky.txt", clobber=True)
                s_in.write(
                    output_root + ".apparent_sky.txt",
                    clobber=True,
                    applyBeam=True,
                )
            else:
                emptysky = True
    else:
        emptysky = True

    # Get the flux scale and astrometry diagnostics if possible and save all
    # the image diagnostics to the output JSON file
    if not emptysky:
        if comparison_skymodel is None:
            # Download a TGSS sky model around the midpoint of the input sky
            # model, using a 5-deg radius to ensure the field is fully covered
            _, _, mid_ra, mid_dec = s_in._getXY()  # pylint: disable=W0212
            try:
                s_comp = lsmtool.load(
                    "tgss", VOPosition=[mid_ra, mid_dec], VORadius=5.0
                )
            except OSError:
                # Problem encountered when downloading model from the TGSS
                # server, so skip the comparison
                s_comp = None
        else:
            s_comp = lsmtool.load(comparison_skymodel)

        # Group the comparison sky model into sources and select only those
        # sources that are composed entirely of type "POINT", as the
        # comparison method in LSMTool works reliably only for this type
        if s_comp is not None:
            # Group using FWHM of 40 arcsec, the approximate TGSS resolution
            s_comp.group("threshold", FWHM="40.0 arcsec", threshold=0.05)

            # Keep POINT-only sources
            source_type = s_comp.getColValues("Type")
            patch_names = s_comp.getColValues("Patch")
            non_point_patch_names = set(
                patch_names[np.where(source_type != "POINT")]
            )
            ind = []
            for patch_name in non_point_patch_names:
                ind.extend(s_comp.getRowIndex(patch_name))
            s_comp.remove(np.array(ind))

    if emptysky:
        # No sources cleaned/found in image, so just make a dummy sky model
        # with single, very faint source at center
        dummylines = [
            "Format = Name, Type, Patch, Ra, Dec, I, SpectralIndex, "
            "LogarithmicSI, ReferenceFrequency='100000000.0', MajorAxis, "
            "MinorAxis, Orientation\n"
        ]
        ra, dec = img.pix2sky(  # pylint: disable=C0103
            (img.shape[-2] / 2.0, img.shape[-1] / 2.0)
        )
        if ra < 0.0:
            ra += 360.0  # pylint: disable=C0103
        ra = ra2hhmmss(ra)  # pylint: disable=C0103
        sra = f"{ra[0]:02}:{ra[1]:02}:{ra[2]:.6f}"
        dec = dec2ddmmss(dec)
        decsign = "-" if dec[3] < 0 else "+"
        sdec = f"{decsign}{dec[0]:02}.{dec[1]:02}.{dec[2]:.6f}"

        dummylines.append(f",,p1,{sra},{sdec}\n")
        dummylines.append(
            f"s0c0,POINT,p1,{sra},{sdec},0.00000001,[0.0,0.0],false,"
            f"100000000.0,,,\n"
        )

        with open(
            output_root + ".apparent_sky.txt", "w", encoding="utf-8"
        ) as current_file:
            current_file.writelines(dummylines)
        with open(
            output_root + ".true_sky.txt", "w", encoding="utf-8"
        ) as current_file:
            current_file.writelines(dummylines)

    # Set the TMPDIR env var back to its original value
    if old_tmpdir is not None:
        os.environ["TMPDIR"] = old_tmpdir
