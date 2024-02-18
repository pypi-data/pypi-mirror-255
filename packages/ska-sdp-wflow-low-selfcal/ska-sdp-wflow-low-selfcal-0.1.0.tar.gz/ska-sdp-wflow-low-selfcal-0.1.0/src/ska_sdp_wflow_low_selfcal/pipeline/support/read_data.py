#  SPDX-License-Identifier: GPL-3.0-or-later

""" This module contains functions to read data from a measurement set
and skymodels """

import lsmtool
import numpy as np
from astropy import units
from astropy.coordinates import Angle
from casacore.tables import taql


def get_phase_center(measurement_set):
    """Read phase center from given MS. Returns the ra, dec values
    in degrees"""
    phase_center = taql(f"select PHASE_DIR deg from {measurement_set}::FIELD")
    ra = (  # pylint: disable=C0103
        Angle(phase_center[0]["Col_1"][0][0] * units.deg)
        .wrap_at(360 * units.deg)
        .degree
    )
    dec = (
        Angle(phase_center[0]["Col_1"][0][1] * units.deg)
        .wrap_at(360 * units.deg)
        .degree
    )
    return [ra, dec]


def get_patches(skymodel_filename):
    """Get patches from skymodel.
    Returns a list of numpy arrays, one array per patch."""
    skymodel = lsmtool.load(skymodel_filename)
    patch_names = skymodel.getColValues(["Patch"])
    ra_coordinate = skymodel.getColValues(["Ra"])
    dec_coordinate = skymodel.getColValues(["Dec"])
    data = np.column_stack((patch_names, ra_coordinate, dec_coordinate))

    groups = []
    for patch in set(patch_names):
        sources_in_patch = data[data[:, 0] == patch]
        groups.append(sources_in_patch[:, 1::])

    return [list(set(patch_names)), groups]
