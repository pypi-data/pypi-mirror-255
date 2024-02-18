#  SPDX-License-Identifier: GPL-3.0-or-later
# Rapthor: LOFAR DDE Pipeline
# Copyright (C) 2023, Team Rapthor
# https://git.astron.nl/RD/rapthor/-/blob/master/LICENSE

"""
Script to make a ds9 region file for use with WSClean and faceting
"""

# This file is copied from the Rapthor repository (with minor changes):
# https://git.astron.nl/RD/rapthor/-/tree/master/rapthor/scripts/make_region_file.py

import lsmtool

from ska_sdp_wflow_low_selfcal.pipeline.support.facet import (
    make_ds9_region_file,
    make_facet_polygons,
)
from ska_sdp_wflow_low_selfcal.pipeline.support.miscellaneous import (
    approx_equal,
    normalize_dec,
    normalize_ra,
)


def make_region_file(  # pylint: disable=R0913, R0914
    skymodel,
    ra_mid,
    dec_mid,
    width_ra,
    width_dec,
    region_file,
):
    """
    Make a ds9 region file

    Parameters
    ----------
    skymodel : str
        Filename of calibration sky model
    ra_mid : float
        RA in degrees of bounding box center
    dec_mid : float
        Dec in degrees of bounding box center
    width_ra : float
        Width of bounding box in RA in degrees, corrected to Dec = 0
    width_dec : float
        Width of bounding box in Dec in degrees
    region_file : str
        Filename of output ds9 region file
    """
    # Set the position of the calibration patches to those of
    # the input sky model
    skymod = lsmtool.load(skymodel)
    source_dict = skymod.getPatchPositions()
    name_cal = []
    ra_cal = []
    dec_cal = []
    for k, v in source_dict.items():  # pylint: disable=C0103
        name_cal.append(k)
        # Make sure RA is between [0, 360) deg and Dec between [-90, 90]
        ra = normalize_ra(v[0].value)
        dec = normalize_dec(v[1].value)
        ra_cal.append(ra)
        dec_cal.append(dec)

    # Do the tessellation
    facet_points, facet_polys = make_facet_polygons(
        ra_cal, dec_cal, ra_mid, dec_mid, width_ra, width_dec
    )
    facet_names = []
    for facet_point in facet_points:
        # For each facet, match the correct name. Some patches in the sky
        # model may have been filtered out if they lie outside the bounding box
        for ra, dec, name in zip(  # pylint: disable=C0103
            ra_cal, dec_cal, name_cal
        ):
            if approx_equal(ra, facet_point[0], tol=1e-6) and approx_equal(
                dec, facet_point[1], tol=1e-6
            ):
                # Note: some versions of ds9 have problems when there are
                # certain characters ('_' and '-' are the two known so far)
                # in any of the names, so remove them
                facet_names.append(name.replace("_", "").replace("-", ""))
                break

    # Make the ds9 region file
    make_ds9_region_file(
        facet_points, facet_polys, region_file, names=facet_names
    )
