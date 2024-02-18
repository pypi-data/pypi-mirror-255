#  SPDX-License-Identifier: GPL-3.0-or-later
# Copyright (C) 2023, Francesco De Gasperin
# https://github.com/revoltek/losoto/blob/master/LICENSE

# -*- coding: utf-8 -*-

# This file was originally copied from the LoSoTo repository
# https://github.com/revoltek/losoto/blob/master/bin/H5parm_collector.py
# pylint: skip-file

import logging
import os
from itertools import chain

import numpy as np
from losoto.h5parm import h5parm

_author = "Francesco de Gasperin (astro@voo.it)"

logger = logging.getLogger("LOSOTO")


def collect_h5parms(
    h5parmFiles,
    outh5parm,
):
    SOLSET_NAME = "sol000"

    # read all tables
    # use all soltabs, find out names from first h5parm
    h5 = h5parm(h5parmFiles[0], readonly=True)
    solset = h5.getSolset(SOLSET_NAME)
    insoltabs = solset.getSoltabNames()
    h5.close()
    if len(insoltabs) == 0:
        logger.critical("No soltabs found.")
        raise RuntimeError("No soltabs found.")

    # open input
    h5s = []
    for h5parmFile in h5parmFiles:
        h5 = h5parm(h5parmFile.replace("'", ""), readonly=True)
        h5s.append(h5)

    # open output
    if os.path.exists(outh5parm):
        os.remove(outh5parm)
    h5Out = h5parm(outh5parm, readonly=False)

    for insoltab in insoltabs:
        soltabs = []
        history = ""
        pointingNames = []
        antennaNames = []
        pointingDirections = []
        antennaPositions = []

        for h5 in h5s:
            solset = h5.getSolset(SOLSET_NAME)
            soltab = solset.getSoltab(insoltab)
            soltabs.append(soltab)
            history += soltab.getHistory()

            # collect pointings
            sous = solset.getSou()
            for k, v in list(sous.items()):
                if k not in pointingNames:
                    pointingNames.append(k)
                    pointingDirections.append(v)

            # collect anntennas
            ants = solset.getAnt()
            for k, v in list(ants.items()):
                if k not in antennaNames:
                    antennaNames.append(k)
                    antennaPositions.append(v)

        # create output axes
        logger.debug("Sorting output axes")
        axes = soltabs[0].getAxesNames()
        typ = soltabs[0].getType()
        allAxesVals = {axis: [] for axis in axes}
        allShape = []
        for axis in axes:
            for soltab in soltabs:
                allAxesVals[axis].append(soltab.getAxisValues(axis))
            allAxesVals[axis] = np.array(
                sorted(list(set(chain(*allAxesVals[axis]))))
            )
            allShape.append(len(allAxesVals[axis]))

        # make final arrays
        logger.debug("Allocating space...")
        logger.debug("Shape:" + str(allShape))
        allVals = np.empty(shape=allShape)
        allVals[:] = np.nan
        allWeights = np.zeros(shape=allShape)  # , dtype=np.float16 )

        # fill arrays
        logger.debug("Filling new table...")
        for soltab in soltabs:
            coords = []
            for axis in axes:
                coords.append(
                    np.searchsorted(
                        allAxesVals[axis], soltab.getAxisValues(axis)
                    )
                )
            allVals[np.ix_(*coords)] = soltab.obj.val
            allWeights[np.ix_(*coords)] = soltab.obj.weight

        # TODO: flag nans waiting for DPPP to do it
        allWeights[np.isnan(allVals)] = 0.0

        logger.debug("Writing output...")
        soltabOutName = insoltab

        # create solset (and add all antennas and directions of other solsets)
        if SOLSET_NAME in h5Out.getSolsetNames():
            solsetOut = h5Out.getSolset(SOLSET_NAME)
        else:
            solsetOut = h5Out.makeSolset(SOLSET_NAME)

        # create soltab
        soltabOut = solsetOut.makeSoltab(
            typ,
            soltabOutName,
            axesNames=axes,
            axesVals=[allAxesVals[axis] for axis in axes],
            vals=allVals,
            weights=allWeights,
        )

        # add history table if requested
        if history:
            soltabOut.addHistory(history, date=False)

    sourceTable = solsetOut.obj._f_get_child("source")
    antennaTable = solsetOut.obj._f_get_child("antenna")
    antennaTable.append(list(zip(*(antennaNames, antennaPositions))))
    sourceTable.append(list(zip(*(pointingNames, pointingDirections))))

    for h5 in h5s:
        h5.close()
    logger.debug(str(h5Out))
    h5Out.close()
