#  SPDX-License-Identifier: GPL-3.0-or-later

"""
Module that holds miscellaneous functions and classes
"""

# This file is copied from the Rapthor repository (with minor changes):
# https://git.astron.nl/RD/rapthor/-/tree/master/rapthor/lib/miscellaneous.py
# pylint: skip-file
import logging
import os

import lsmtool
import numpy as np
import requests


def download_skymodel(
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
    SKY_SERVERS = {
        "TGSS": "http://tgssadr.strw.leidenuniv.nl/cgi-bin/gsmv4.cgi?coord=\
        {ra:f},{dec:f}&radius={radius:f}&unit=deg&deconv=y",
        "GSM": "https://lcs165.lofar.eu/cgi-bin/gsmv1.cgi?coord={ra:f},{dec:f}\
        &radius={radius:f}&unit=deg&deconv=y",
    }
    if source.upper() not in SKY_SERVERS.keys():
        raise ValueError(
            "Unsupported skymodel source specified! Please use TGSS or GSM."
        )

    logger = logging.getLogger("rapthor:skymodel")

    file_exists = os.path.isfile(skymodel_path)
    if file_exists and not overwrite:
        logger.warning(
            'Skymodel "%s" exists and overwrite is set to False! Not \
            downloading skymodel. If this is a restart this may be \
            intentional.'
            % skymodel_path
        )
        return

    if (not file_exists) and os.path.exists(skymodel_path):
        logger.error('Path "%s" exists but is not a file!' % skymodel_path)
        raise ValueError('Path "%s" exists but is not a file!' % skymodel_path)

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
            'Found existing skymodel "%s" and overwrite is True. Deleting \
            existing skymodel!'
            % skymodel_path
        )
        os.remove(skymodel_path)

    logger.info("Downloading skymodel for the target into " + skymodel_path)

    url = SKY_SERVERS[source].format(ra=ra, dec=dec, radius=radius)
    response = requests.get(url)
    open(skymodel_path, "wb").write(response.content)

    if not os.path.isfile(skymodel_path):
        logger.critical(
            'Skymodel "%s" does not exist after trying to download the \
            skymodel.'
            % skymodel_path
        )
        raise IOError(
            'Skymodel "%s" does not exist after trying to download the \
            skymodel.'
            % skymodel_path
        )

    # Treat all sources as one group (direction)
    skymodel = lsmtool.load(skymodel_path)
    skymodel.group("single", root=targetname)
    skymodel.write(clobber=True)


def group_sources(
    input_ms,
    skymodel_true_sky,
    grouped_skymodel_filename,
    skymodel_apparent_sky=None,
    target_flux=1.0,
    max_directions=10,
):
    
    #cmd = os.popen('module load everybeam')
    #exec('module load everybeam')
    """Group sources based on target_flux and max_directions"""
    source_skymodel = lsmtool.load(skymodel_true_sky, beamMS=input_ms)

    source_skymodel.group("threshold", FWHM="40.0 arcsec", threshold=0.05)
    source_skymodel.group(
        "meanshift",
        byPatch=True,
        applyBeam=True,
        lookDistance=0.075,
        groupingDistance=0.01,
    )
    source_skymodel.setPatchPositions(method="wmean")

    fluxes = source_skymodel.getColValues("I", aggregate="sum", applyBeam=True)
    if max_directions >= len(fluxes):
        max_directions = len(fluxes)
        target_flux_for_number = np.min(fluxes)
    else:
        # Weight the fluxes by size to estimate the required target flux
        # The same weighting scheme is used by LSMTool when performing
        # the 'voronoi' grouping later
        sizes = source_skymodel.getPatchSizes(
            units="arcsec", weight=True, applyBeam=True
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
            medianSize = np.median(sizes[bright_ind])
            weights = medianSize / sizes
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

    target_flux = target_flux_for_number
    source_skymodel.group(
        "voronoi",
        targetFlux=target_flux,
        applyBeam=True,
        weightBySize=True,
    )
    source_skymodel.write(grouped_skymodel_filename, clobber=True)
