#  SPDX-License-Identifier: GPL-3.0-or-later
# Rapthor: LOFAR DDE Pipeline
# Copyright (C) 2023, Team Rapthor
# https://git.astron.nl/RD/rapthor/-/blob/master/LICENSE

"""
Module that holds miscellaneous functions and classes
"""

# This file is copied from the Rapthor repository (with minor changes):
# https://git.astron.nl/RD/rapthor/-/tree/master/rapthor/lib/miscellaneous.py

import logging
import os
import pickle

import lsmtool
import numpy as np
import requests
from shapely.geometry import Polygon

from ska_sdp_wflow_low_selfcal.pipeline.support.facet import radec2xy, xy2radec
from ska_sdp_wflow_low_selfcal.pipeline.support.miscellaneous import make_wcs
from ska_sdp_wflow_low_selfcal.pipeline.support.read_data import (
    compute_observation_width,
    get_observation_params,
    get_phase_center,
)


def download_skymodel(  # pylint: disable=too-many-arguments
    ra,
    dec,
    skymodel_path,
    radius=5.0,
    overwrite=False,
    source="TGSS",
    targetname="Patch",
):
    """
    Download the skymodel for the target field

    Parameters
    ----------
    ra : float
        Right ascension of the skymodel centre.
    dec : float
        Declination of the skymodel centre.
    skymodel_path : str
        Full name (with path) to the skymodel.
    radius : float
        Radius for the TGSS/GSM cone search in degrees.
    source : str
        Source where to obtain a skymodel from. Can be TGSS or GSM. Default is
        TGSS.
    overwrite : bool
        Overwrite the existing skymodel pointed to by skymodel_path.
    target_name : str
        Give the patch a certain name. Default is "Patch".
    """
    sky_servers = {
        "TGSS": "http://tgssadr.strw.leidenuniv.nl/cgi-bin/gsmv4.cgi?coord="
        "{ra:f},{dec:f}&radius={radius:f}&unit=deg&deconv=y",
        "GSM": "https://lcs165.lofar.eu/cgi-bin/gsmv1.cgi?coord="
        "{ra:f},{dec:f}&radius={radius:f}&unit=deg&deconv=y",
    }
    if source.upper() not in sky_servers:
        raise ValueError(
            "Unsupported skymodel source specified! Please use TGSS or GSM."
        )

    logger = logging.getLogger("rapthor:skymodel")

    file_exists = os.path.isfile(skymodel_path)
    if file_exists and not overwrite:
        logger.warning(
            "Skymodel %s exists and overwrite is set to False! Not \
            downloading skymodel. If this is a restart this may be \
            intentional.",
            skymodel_path,
        )
        return

    if (not file_exists) and os.path.exists(skymodel_path):
        msg = f"Path {skymodel_path} exists but is not a file!"
        logger.error(msg)
        raise ValueError(msg)

    # Empty strings are False. Only attempt directory creation if there is a
    # directory path involved.
    if (
        (not file_exists)
        and os.path.dirname(skymodel_path)
        and (not os.path.exists(os.path.dirname(skymodel_path)))
    ):
        os.makedirs(os.path.dirname(skymodel_path))

    if file_exists and overwrite:
        logger.warning(
            "Found existing skymodel %s and overwrite is True. Deleting \
            existing skymodel!",
            skymodel_path,
        )
        os.remove(skymodel_path)

    url = sky_servers[source].format(ra=ra, dec=dec, radius=radius)
    logger.info('Downloading skymodel for the target into "%s"', skymodel_path)
    logger.info("Skymodel URL: %s", url)
    response = requests.get(url, timeout=20)
    with open(skymodel_path, "wb") as skymodel_file:
        skymodel_file.write(response.content)

    if not os.path.isfile(skymodel_path):
        logger.critical(
            "Skymodel %s does not exist after trying to download the \
            skymodel.",
            skymodel_path,
        )
        raise IOError(
            f"Skymodel {skymodel_path} does not exist after trying to \
            download the skymodel."
        )

    # Treat all sources as one group (direction)
    skymodel = lsmtool.load(skymodel_path)
    skymodel.group("single", root=targetname)
    skymodel.write(clobber=True)


def group_sources(  # pylint: disable=too-many-arguments,too-many-locals
    input_ms,
    skymodel_true_sky_filename,
    grouped_skymodel_filename,
    skymodel_apparent_sky_filename=None,
    target_flux=1.0,
    max_directions=10,
    find_sources=True,
    bright_source_apparent_filename="bright_source_apparent.skymodel",
):
    """Group sources based on target_flux and max_directions"""

    source_skymodel = lsmtool.load(
        skymodel_apparent_sky_filename or skymodel_true_sky_filename, input_ms
    )

    if find_sources:
        source_skymodel.group("threshold", FWHM="40.0 arcsec", threshold=0.05)
    source_skymodel.group(
        "meanshift",
        byPatch=True,
        applyBeam=skymodel_apparent_sky_filename is None,
        lookDistance=0.075,
        groupingDistance=0.01,
    )
    source_skymodel.setPatchPositions(method="wmean")

    source_skymodel.write(bright_source_apparent_filename, clobber=True)

    fluxes = source_skymodel.getColValues(
        "I", aggregate="sum", applyBeam=skymodel_apparent_sky_filename is None
    )
    if max_directions >= len(fluxes):
        max_directions = len(fluxes)
        target_flux_for_number = np.min(fluxes)
    else:
        # Weight the fluxes by size to estimate the required target flux
        # The same weighting scheme is used by LSMTool when performing
        # the 'voronoi' grouping later
        sizes = source_skymodel.getPatchSizes(
            units="arcsec",
            weight=True,
            applyBeam=skymodel_apparent_sky_filename is None,
        )

        sizes[sizes < 1.0] = 1.0
        if target_flux is not None:
            trial_target_flux = target_flux
        else:
            trial_target_flux = 0.3

        trial_number = 0
        for _ in range(100):
            if trial_number == max_directions:
                break
            trial_fluxes = fluxes.copy()
            bright_ind = np.where(trial_fluxes >= trial_target_flux)
            median_size = np.median(sizes[bright_ind])
            weights = median_size / sizes
            weights[weights > 1.0] = 1.0
            weights[weights < 0.5] = 0.5
            trial_fluxes *= weights
            trial_fluxes.sort()
            trial_number = len(trial_fluxes[trial_fluxes >= trial_target_flux])
            if trial_number < max_directions:
                # Reduce the trial target flux to next fainter source
                trial_target_flux = trial_fluxes[-(trial_number + 1)]
            elif trial_number > max_directions:
                # Increase the trial flux to next brighter source
                trial_target_flux = trial_fluxes[-(trial_number - 1)]
        target_flux_for_number = trial_target_flux

    if target_flux_for_number > target_flux and max_directions < len(fluxes):
        # Only use the new target flux if the old value might result
        # in more than target_number of calibrators
        target_flux = target_flux_for_number

    source_skymodel.group(
        "voronoi",
        targetFlux=target_flux,
        applyBeam=skymodel_apparent_sky_filename is None,
        weightBySize=True,
    )
    source_skymodel.write(grouped_skymodel_filename, clobber=True)


def discard_sources_outside_polygon(skymodel, wcs, poly):
    """
    Filters input skymodel to select only sources that lie inside the sector

    Parameters
    ----------
    skymodel : LSMTool skymodel object
        Input sky model
    wcs: Current world coordinate system
    poly: Polygon defining the area in which the sources should be kept.
        Outside of these boundaries the sources are filtered.

    Returns
    -------
    filtered_skymodel : LSMTool skymodel object
        Filtered sky model
    """
    # Make list of sources
    ra = skymodel.getColValues("Ra")
    dec = skymodel.getColValues("Dec")

    x, y = radec2xy(wcs, ra, dec)
    x = np.array(x)
    y = np.array(y)

    # Keep only those sources inside the sector bounding box
    inside = np.zeros(len(skymodel), dtype=bool)
    xmin, ymin, xmax, ymax = poly.bounds
    inside_ind = np.where(
        (x >= xmin) & (x <= xmax) & (y >= ymin) & (y <= ymax)
    )
    inside[inside_ind] = True
    skymodel.select(inside)

    return skymodel


def define_sector(  # pylint: disable=too-many-locals,too-many-arguments
    path_to_grouped_skymodel,
    sector_skymodel_filename,
    input_ms,
    vertices_filename="sector_1_vertices.pkl",
):
    """Create a sector skymodel only containing all the sources lying in
    the desired imaging field

    Parameters
    ----------
    path_to_grouped_skymodel : path to LSMTool skymodel object
        Input sky model. This is the skymodel used for calibration.
    sector_skymodel_filename: path to output sector skymodel
    input_ms: path to input measurement set
    vertices_filename: path to file that will contain the vertices

    Returns
    -------
    vertices : np.array
        sector vertices
    """

    calibration_skymodel = lsmtool.load(
        path_to_grouped_skymodel, beamMS=input_ms
    )

    skymodel = calibration_skymodel.copy()

    [phase_center_ra, phase_center_dec] = get_phase_center(input_ms)

    wcs = make_wcs(phase_center_ra, phase_center_dec)

    observation = get_observation_params(input_ms)
    width = compute_observation_width(observation)

    # Determine the vertices of the sector polygon

    # Define initial polygon as a rectangle
    center_x, center_y = radec2xy(wcs, [phase_center_ra], [phase_center_dec])

    ra_width_pix = width["ra"] / abs(wcs.wcs.cdelt[0])
    dec_width_pix = width["dec"] / abs(wcs.wcs.cdelt[1])
    x_0 = center_x[0] - ra_width_pix / 2.0
    y_0 = center_y[0] - dec_width_pix / 2.0
    poly_verts = [
        (x_0, y_0),
        (x_0, y_0 + dec_width_pix),
        (x_0 + ra_width_pix, y_0 + dec_width_pix),
        (x_0 + ra_width_pix, y_0),
        (x_0, y_0),
    ]

    poly = Polygon(poly_verts)

    vertices_x = poly.exterior.coords.xy[0].tolist()
    vertices_y = poly.exterior.coords.xy[1].tolist()
    ra, dec = xy2radec(
        wcs,
        vertices_x,
        vertices_y,
    )
    vertices = [np.array(ra), np.array(dec)]
    with open(vertices_filename, "wb") as filename:
        pickle.dump(vertices, filename)

    skymodel = discard_sources_outside_polygon(skymodel, wcs, poly)
    skymodel.write(sector_skymodel_filename, clobber=True)

    return zip(vertices_x, vertices_y)


def get_outliers(full_sky, sector_skymodel, outliers_sky):
    """
    Make a sky model of all the outlier sources in the full_sky not included
    in the sector_skymodel
    """
    full_skymodel = lsmtool.load(str(full_sky))
    all_source_names = full_skymodel.getColValues("Name").tolist()
    sector_source_names = []

    skymodel = lsmtool.load(str(sector_skymodel))
    sector_source_names.extend(skymodel.getColValues("Name").tolist())

    outlier_ind = np.array(
        [
            all_source_names.index(sn)
            for sn in all_source_names
            if sn not in sector_source_names
        ]
    )
    outlier_skymodel = full_skymodel.copy()
    outlier_skymodel.select(outlier_ind, force=True)

    outlier_skymodel.write(outliers_sky, clobber=True)


def transfer_patches(from_skymodel, to_skymodel, patch_dict=None):
    """
    Transfers the patches defined in from_skymodel to to_skymodel.

    Parameters
    ----------
    from_skymodel : sky model
        Sky model from which to transfer patches
    to_skymodel : sky model
        Sky model to which to transfer patches
    patch_dict : dict, optional
        Dict of patch positions

    Returns
    -------
    to_skymodel : sky model
        Sky model with patches matching those of from_skymodel
    """
    names_from = from_skymodel.getColValues("Name").tolist()
    names_to = to_skymodel.getColValues("Name").tolist()

    if set(names_from) == set(names_to):
        # Both sky models have the same sources, so use indexing
        ind_ss = np.argsort(names_from)
        ind_ts = np.argsort(names_to)
        to_skymodel.table["Patch"][ind_ts] = from_skymodel.table["Patch"][
            ind_ss
        ]
        to_skymodel._updateGroups()  # pylint: disable=protected-access
    elif set(names_to).issubset(set(names_from)):
        # The to_skymodel is a subset of from_skymodel, so use slower matching
        # algorithm
        for ind_ts, name in enumerate(names_to):
            ind_ss = names_from.index(name)
            to_skymodel.table["Patch"][ind_ts] = from_skymodel.table["Patch"][
                ind_ss
            ]
    else:
        # Skymodels don't match, raise error
        raise ValueError(
            "Cannot transfer patches since from_skymodel does not contain "
            "all the sources in to_skymodel"
        )

    if patch_dict is not None:
        to_skymodel.setPatchPositions(patchDict=patch_dict)
    return to_skymodel


def get_bright_sources(
    source_skymodel_filename,
    bright_source_apparent_filename,
    calibrators_skymodel_filename,
    input_ms,
    sector_vertices,
):  # pylint: disable=too-many-locals
    """Get skymodels for bright sources and calibrators"""

    bright_source_skymodel_apparent_sky = lsmtool.load(
        bright_source_apparent_filename, input_ms
    )
    source_skymodel = lsmtool.load(source_skymodel_filename, input_ms)

    patch_dict = bright_source_skymodel_apparent_sky.getPatchPositions()
    skymodel_ref = source_skymodel.copy()
    source_skymodel.setPatchPositions(patchDict=patch_dict)

    bright_patch_names = bright_source_skymodel_apparent_sky.getPatchNames()
    for patch_name in bright_patch_names:
        if patch_name not in source_skymodel.getPatchNames():
            bright_source_skymodel_apparent_sky.remove(
                f"Patch == {patch_name}"
            )

    # Transfer patches to the true-flux sky model (source names are identical
    # in both, but the order may be different)
    transfer_patches(source_skymodel, skymodel_ref, patch_dict=patch_dict)

    # Rapthor field.py 559 - 606
    # For the bright-source true-sky model, duplicate any selections made
    # above to the apparent-sky model
    bright_source_skymodel = skymodel_ref.copy()
    source_names = bright_source_skymodel.getColValues("Name").tolist()
    bright_source_names = bright_source_skymodel_apparent_sky.getColValues(
        "Name"
    ).tolist()
    matching_ind = []
    for source_name in bright_source_names:
        matching_ind.append(source_names.index(source_name))
    bright_source_skymodel.select(np.array(matching_ind))

    # Transfer patches to the bright-source model. At this point, it is now the
    # model of calibrator sources only, so copy and save it and write it out
    # for later use
    regroup = True
    if regroup:
        # Transfer from the apparent-flux sky model (regrouped above)
        transfer_patches(
            bright_source_skymodel_apparent_sky, bright_source_skymodel
        )
    else:
        # Transfer from the true-flux sky model
        patch_dict = skymodel_ref.getPatchPositions()
        transfer_patches(
            skymodel_ref, bright_source_skymodel, patch_dict=patch_dict
        )

    # Save calibrators skymodel from bright_source_skymodel
    bright_source_skymodel.write(
        f"{calibrators_skymodel_filename}", clobber=True
    )

    # Now remove any bright sources that lie outside the imaged area, as they
    # should not be peeled

    [phase_center_ra, phase_center_dec] = get_phase_center(input_ms)
    wcs = make_wcs(phase_center_ra, phase_center_dec)

    poly = Polygon(sector_vertices)

    filtered_skymodel = discard_sources_outside_polygon(
        bright_source_skymodel, wcs, poly
    )

    bright_source_skymodel = filtered_skymodel
    if len(bright_source_skymodel) > 0:
        bright_source_skymodel.setPatchPositions()

    return bright_source_skymodel


def split_skymodel_file(input_skymodel, filename_prefix):
    """
    Splits a skymodel into different files with a minimum of 100 sources each.
    Generates a single file if input_skymodel contains less than 100 sources.
    """
    source_sectors = []
    nsources = len(input_skymodel)
    if nsources > 0:
        # Choose number of sectors to be the no more than ten, but don't
        # allow fewer than 100 sources per sector if possible
        nnodes = max(
            min(10, round(nsources / 100)), 1
        )  # TODO: tune to number of available nodes and/or memory?
        for i in range(nnodes):
            split_skymodel = input_skymodel.copy()
            startind = i * int(nsources / nnodes)
            if i == nnodes - 1:
                endind = nsources
            else:
                endind = startind + int(nsources / nnodes)
            split_skymodel.select(np.array(list(range(startind, endind))))
            split_skymodel.write(
                f"{filename_prefix}_{i}.skymodel", clobber=True
            )
            source_sectors.append(f"{filename_prefix}_{i}.skymodel")

    # Also save the entire skymodel, as it will be used in wsclean restore
    # operation
    input_skymodel.write(f"{filename_prefix}.skymodel", clobber=True)

    return source_sectors


def get_flux_per_patch(skymodel_filename):
    """Read facet list and flux per facet from skymodel"""

    skymodel = lsmtool.load(skymodel_filename)
    skymodel_table = skymodel.table["Patch", "I"]
    previous_facet_name = "none"
    flux_per_facet = []
    total_flux_per_facet = 0.0
    for i, facet_name in enumerate(skymodel_table["Patch"]):
        if facet_name != previous_facet_name:
            if i > 0:
                flux_per_facet.append(total_flux_per_facet)
            previous_facet_name = facet_name
            total_flux_per_facet = 0
        total_flux_per_facet += skymodel_table[i]["I"]

    flux_per_facet.append(total_flux_per_facet)
    directions_list = list(set(skymodel_table["Patch"]))

    return directions_list, flux_per_facet
