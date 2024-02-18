#  SPDX-License-Identifier: GPL-3.0-or-later
# Rapthor: LOFAR DDE Pipeline
# Copyright (C) 2023, Team Rapthor
# https://git.astron.nl/RD/rapthor/-/blob/master/LICENSE

# This file is copied from the Rapthor repository (with minor changes):
# https://git.astron.nl/RD/rapthor/-/tree/master/rapthor/scripts/blank_image.py
"""
Script to blank regions (with zeros or NaNs) in a fits image. Can also be used
to make a clean mask
"""


# pylint: skip-file
import argparse
import sys
from argparse import RawTextHelpFormatter

import numpy as np
from astropy import wcs
from astropy.io import fits as pyfits

from ska_sdp_wflow_low_selfcal.pipeline.support.miscellaneous import (
    rasterize,
    read_vertices_ra_dec,
)


def make_template_image(
    image_name,
    reference_ra_deg,
    reference_dec_deg,
    ximsize=512,
    yimsize=512,
    cellsize_deg=0.000417,
    freqs=None,
    times=None,
    antennas=None,
    aterm_type="tec",
    fill_val=0,
):
    """
    Make a blank FITS image and save it to disk

    Parameters
    ----------
    image_name : str
        Filename of output image
    reference_ra_deg : float, optional
        RA for center of output mask image
    reference_dec_deg : float, optional
        Dec for center of output mask image
    imsize : int, optional
        Size of output image
    cellsize_deg : float, optional
        Size of a pixel in degrees
    freqs : list
        Frequencies to use to construct extra axes (for IDG a-term images)
    times : list
        Times to use to construct extra axes (for IDG a-term images)
    antennas : list
        Antennas to use to construct extra axes (for IDG a-term images)
    aterm_type : str
        One of 'tec' or 'gain'
    fill_val : int
        Value with which to fill the data
    """
    if freqs is not None and times is not None and antennas is not None:
        nants = len(antennas)
        ntimes = len(times)
        nfreqs = len(freqs)
        if aterm_type == "tec":
            # TEC solutions
            # data is [RA, DEC, ANTENNA, FREQ, TIME].T
            shape_out = [ntimes, nfreqs, nants, yimsize, ximsize]
        else:
            # Gain solutions
            # data is [RA, DEC, MATRIX, ANTENNA, FREQ, TIME].T
            shape_out = [ntimes, nfreqs, nants, 4, yimsize, ximsize]
    else:
        # Normal FITS image
        # data is [STOKES, FREQ, DEC, RA]
        shape_out = [1, 1, yimsize, ximsize]
        nfreqs = 1
        freqs = [150e6]

    hdu = pyfits.PrimaryHDU(np.ones(shape_out, dtype=np.float32) * fill_val)
    hdulist = pyfits.HDUList([hdu])
    header = hdulist[0].header

    # Add RA, Dec info
    i = 1
    header["CRVAL{}".format(i)] = reference_ra_deg
    header["CDELT{}".format(i)] = -cellsize_deg
    header["CRPIX{}".format(i)] = ximsize / 2.0
    header["CUNIT{}".format(i)] = "deg"
    header["CTYPE{}".format(i)] = "RA---SIN"
    i += 1
    header["CRVAL{}".format(i)] = reference_dec_deg
    header["CDELT{}".format(i)] = cellsize_deg
    header["CRPIX{}".format(i)] = yimsize / 2.0
    header["CUNIT{}".format(i)] = "deg"
    header["CTYPE{}".format(i)] = "DEC--SIN"
    i += 1

    # Add STOKES info or ANTENNA (+MATRIX) info
    if antennas is None:
        # basic image
        header["CRVAL{}".format(i)] = 1.0
        header["CDELT{}".format(i)] = 1.0
        header["CRPIX{}".format(i)] = 1.0
        header["CUNIT{}".format(i)] = ""
        header["CTYPE{}".format(i)] = "STOKES"
        i += 1
    else:
        if aterm_type == "gain":
            # gain aterm images: add MATRIX info
            header["CRVAL{}".format(i)] = 0.0
            header["CDELT{}".format(i)] = 1.0
            header["CRPIX{}".format(i)] = 1.0
            header["CUNIT{}".format(i)] = ""
            header["CTYPE{}".format(i)] = "MATRIX"
            i += 1

        # dTEC or gain: add ANTENNA info
        header["CRVAL{}".format(i)] = 0.0
        header["CDELT{}".format(i)] = 1.0
        header["CRPIX{}".format(i)] = 1.0
        header["CUNIT{}".format(i)] = ""
        header["CTYPE{}".format(i)] = "ANTENNA"
        i += 1

    # Add frequency info
    ref_freq = freqs[0]
    if nfreqs > 1:
        deltas = freqs[1:] - freqs[:-1]
        del_freq = np.min(deltas)
    else:
        del_freq = 1e8
    header["RESTFRQ"] = ref_freq
    header["CRVAL{}".format(i)] = ref_freq
    header["CDELT{}".format(i)] = del_freq
    header["CRPIX{}".format(i)] = 1.0
    header["CUNIT{}".format(i)] = "Hz"
    header["CTYPE{}".format(i)] = "FREQ"
    i += 1

    # Add time info
    if times is not None:
        ref_time = times[0]
        if ntimes > 1:
            # Find CDELT as the smallest delta time, but ignore last delta, as
            # it may be smaller due to the number of time slots not being a
            # divisor of the solution interval
            deltas = times[1:] - times[:-1]
            if ntimes > 2:
                del_time = np.min(deltas[:-1])
            else:
                del_time = deltas[0]
        else:
            del_time = 1.0
        header["CRVAL{}".format(i)] = ref_time
        header["CDELT{}".format(i)] = del_time
        header["CRPIX{}".format(i)] = 1.0
        header["CUNIT{}".format(i)] = "s"
        header["CTYPE{}".format(i)] = "TIME"
        i += 1

    # Add equinox
    header["EQUINOX"] = 2000.0

    # Add telescope
    header["TELESCOP"] = "LOFAR"

    hdulist[0].header = header
    hdulist.writeto(image_name, overwrite=True)
    hdulist.close()


def blank_image(
    output_image,
    input_image=None,
    vertices_file=None,
    reference_ra_deg=None,
    reference_dec_deg=None,
    cellsize_deg=None,
    imsize=None,
    region_file="[]",
):
    """
    Blank a region in an image

    Parameters
    ----------
    output_image : str
        Filename of output image
    input_image : str, optional
        Filename of input image/mask to blank
    vertices_file : str, optional
        Filename of file with vertices
    reference_ra_deg : float, optional
        RA for center of output mask image
    reference_dec_deg : float, optional
        Dec for center of output mask image
    cellsize_deg : float, optional
        Size of a pixel in degrees
    imsize : int, optional
        Size of image as "xsize ysize"
    region_file : list, optional
        Filenames of region files in CASA format to use as the mask (NYI)
    """
    if input_image is None:
        print("Input image not given. Making empty image...")
        make_blank_image = True
        if reference_ra_deg is not None and reference_dec_deg is not None:
            reference_ra_deg = float(reference_ra_deg)
            reference_dec_deg = float(reference_dec_deg)
            ximsize = int(imsize.split(",")[0])
            yimsize = int(imsize.split(",")[1])
            make_template_image(
                output_image,
                reference_ra_deg,
                reference_dec_deg,
                ximsize=ximsize,
                yimsize=yimsize,
                cellsize_deg=float(cellsize_deg),
                fill_val=1,
            )
        else:
            print(
                "ERROR: a reference position must be given to make an empty \
                template image"
            )
            sys.exit(1)
    else:
        make_blank_image = False

    if vertices_file is not None:
        # Construct polygon
        if make_blank_image:
            header = pyfits.getheader(output_image, 0)
        else:
            header = pyfits.getheader(input_image, 0)
        w = wcs.WCS(header)
        RAind = w.axis_type_names.index("RA")
        Decind = w.axis_type_names.index("DEC")
        vertices = read_vertices_ra_dec(vertices_file)

        verts = []
        for RAvert, Decvert in vertices:
            ra_dec = np.array([[0.0, 0.0, 0.0, 0.0]])
            ra_dec[0][RAind] = RAvert
            ra_dec[0][Decind] = Decvert
            verts.append(
                (
                    w.wcs_world2pix(ra_dec, 0)[0][RAind],
                    w.wcs_world2pix(ra_dec, 0)[0][Decind],
                )
            )

        if make_blank_image:
            hdu = pyfits.open(output_image, memmap=False)
        else:
            hdu = pyfits.open(input_image, memmap=False)
        data = hdu[0].data

        # Rasterize the poly
        data_rasertize = data[0, 0, :, :]
        data_rasertize = rasterize(verts, data_rasertize)
        data[0, 0, :, :] = data_rasertize

        hdu[0].data = data
        hdu.writeto(output_image, overwrite=True)


if __name__ == "__main__":
    descriptiontext = "Blank regions of an image.\n"

    parser = argparse.ArgumentParser(
        description=descriptiontext, formatter_class=RawTextHelpFormatter
    )
    parser.add_argument("output_image_file", help="Filename of output image")
    parser.add_argument(
        "input_image_file",
        help="Filename of input image",
        nargs="?",
        default=None,
    )
    parser.add_argument(
        "--vertices_file",
        help="Filename of vertices file",
        type=str,
        default=None,
    )
    parser.add_argument(
        "--reference_ra_deg", help="Reference RA", type=float, default=None
    )
    parser.add_argument(
        "--reference_dec_deg", help="Reference Dec", type=float, default=None
    )
    parser.add_argument(
        "--cellsize_deg", help="Cellsize", type=float, default=None
    )
    parser.add_argument("--imsize", help="Image size", type=str, default=None)
    parser.add_argument(
        "--region_file", help="Filename of region file", type=str, default=None
    )
    args = parser.parse_args()
    blank_image(
        args.output_image_file,
        args.input_image_file,
        vertices_file=args.vertices_file,
        reference_ra_deg=args.reference_ra_deg,
        reference_dec_deg=args.reference_dec_deg,
        cellsize_deg=args.cellsize_deg,
        imsize=args.imsize,
        region_file=args.region_file,
    )
