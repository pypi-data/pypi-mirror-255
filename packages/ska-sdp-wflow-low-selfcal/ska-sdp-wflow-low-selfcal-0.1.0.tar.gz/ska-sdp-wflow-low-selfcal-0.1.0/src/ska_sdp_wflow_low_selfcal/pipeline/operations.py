#  SPDX-License-Identifier: GPL-3.0-or-later
""" This module contains all operations to run in the pipeline """

import logging
import os
import pathlib

from ska_sdp_wflow_low_selfcal.pipeline.support.blank_image import blank_image
from ska_sdp_wflow_low_selfcal.pipeline.support.combine_h5parms import (
    combine_h5parms,
)
from ska_sdp_wflow_low_selfcal.pipeline.support.filter_skymodel import (
    filter_skymodel,
)
from ska_sdp_wflow_low_selfcal.pipeline.support.H5parm_collector import (
    collect_h5parms,
)
from ska_sdp_wflow_low_selfcal.pipeline.support.make_region_file import (
    make_region_file,
)
from ska_sdp_wflow_low_selfcal.pipeline.support.read_data import get_patches
from ska_sdp_wflow_low_selfcal.pipeline.support.subtract_sector_models import (
    subtract_sector_models,
)

# These are the start times in the midbands.ms dataset which allow a split of
# the dataset in 10 time chunks
# AST-1269: read START_TIMES from the MS and make the split configurable
# (for example: each chunk should be 40 minutes long)
START_TIMES = [
    "21Dec2017/07:11:03.906",
    "21Dec2017/07:59:07.909",
    "21Dec2017/08:47:03.901",
    "21Dec2017/09:35:07.905",
    "21Dec2017/10:23:03.897",
    "21Dec2017/11:10:59.889",
    "21Dec2017/11:59:03.893",
    "21Dec2017/12:46:59.885",
    "21Dec2017/13:35:03.889",
    "21Dec2017/14:22:59.881",
]
TIMES_MJD = [
    "mjd5020557063",
    "mjd5020559947",
    "mjd5020562823",
    "mjd5020565707",
    "mjd5020568583",
    "mjd5020571459",
    "mjd5020574343",
    "mjd5020577219",
    "mjd5020580103",
    "mjd5020582979",
]

REFERENCE_RA_DEG = "258.845708333"
REFERENCE_DEC_DEG = "57.4111944444"

logger = logging.getLogger("ska-sdp-wflow-low-selfcal")


def calibrate_1(dp3_runner, msin, skymodel, work_dir):
    """Define calibrate operation"""
    # ------------------------ Calibrate_1 0:52:21
    logger.info("Start calibrate_1")

    # AST-1270: get outlier_1_predict_skymodel

    output_solutions_filenames = []
    for i, start_time in enumerate(START_TIMES):
        logger.info("Running calibrate_scalarphase for time %s", start_time)
        output_solution_filename = (
            f"{work_dir}/out_calibration_1_fast_phase_" + str(i) + ".h5parm"
        )
        dp3_runner.calibrate_scalarphase(
            msin,
            start_time,
            skymodel,
            False,
            output_solution_filename,
        )
        output_solutions_filenames.append(output_solution_filename)

    # Stitch all solutions together
    logger.info("Start collect_h5parms")
    combined_solutions = f"{work_dir}/in_predict_1_field-solutions.h5"
    collect_h5parms(
        output_solutions_filenames,
        combined_solutions,
        clobber=True,
    )

    logger.info("Done collect_h5parms")
    return combined_solutions


def calibrate_2(dp3_runner, msin_after_predict, inputs_dir, work_dir):
    """Define calibrate operation"""

    output_solutions_filenames = []
    for i, start_time in enumerate(START_TIMES):
        logger.info("Running calibrate_scalarphase for time %s", start_time)
        output_solution_filename = (
            f"{work_dir}/out_calibration_2_fast_phase_" + str(i) + ".h5parm"
        )
        dp3_runner.calibrate_scalarphase(
            msin_after_predict[i],
            start_time,
            f"{inputs_dir}/in_calibration_2.skymodel",
            False,
            output_solution_filename,
        )
        output_solutions_filenames.append(output_solution_filename)

    # Stitch all solutions together
    logger.info("Start collect_h5parms")
    combined_solutions = f"{work_dir}/in_predict_2_field-solutions.h5"
    collect_h5parms(
        output_solutions_filenames,
        combined_solutions,
        clobber=True,
    )

    logger.info("Done collect_h5parms")

    return combined_solutions


def calibrate_3(dp3_runner, msin_list, inputs_dir, work_dir, combine=False):
    """Define calibrate operation"""

    output_solutions_filenames_scalarphase = []
    output_solutions_filenames_complexgain = []

    for i, start_time in enumerate(START_TIMES):
        single_solution_scalarphase = (
            f"{work_dir}/out_calibration_3_fast_phase_" + str(i) + ".h5parm"
        )
        single_solution_complexgain = (
            f"{work_dir}/out_calibration_3_slow_gain_separate_"
            + str(i)
            + ".h5parm"
        )
        output_solutions_filenames_scalarphase.append(
            single_solution_scalarphase
        )
        output_solutions_filenames_complexgain.append(
            single_solution_complexgain
        )

        if not combine:
            logger.info(
                "Running calibrate_scalarphase for time %s", start_time
            )
            dp3_runner.calibrate_scalarphase(
                msin_list[i],
                start_time,
                f"{inputs_dir}/in_calibration_3.skymodel",
                True,
                single_solution_scalarphase,
            )
            logger.info(
                "Running calibrate_complexgain for time %s", start_time
            )
            dp3_runner.calibrate_complexgain(
                msin_list[i],
                start_time,
                f"{inputs_dir}/in_calibration_3.skymodel",
                single_solution_scalarphase,
                single_solution_complexgain,
            )
        else:
            logger.info(
                "Running calibrate_scalarphase+complexgain for time %s",
                start_time,
            )
            dp3_runner.calibrate_scalarphase_and_complexgain(
                msin_list[i],
                start_time,
                f"{inputs_dir}/in_calibration_3.skymodel",
                True,
                single_solution_scalarphase,
                single_solution_complexgain,
            )

    # Stitch all solutions together
    logger.info("Start collect_h5parms scalarphase")
    combined_solutions_fast_phase = (
        f"{work_dir}/out-cal3-fastphase-solutions.h5"
    )
    collect_h5parms(
        output_solutions_filenames_scalarphase,
        combined_solutions_fast_phase,
        clobber=True,
    )
    logger.info("Done collect_h5parms scalarphase")

    logger.info("Start collect_h5parms complexgain")
    combined_solutions_complex_gain = (
        f"{work_dir}/out-cal3-complexgain-solutions.h5"
    )
    collect_h5parms(
        output_solutions_filenames_complexgain,
        combined_solutions_complex_gain,
        clobber=True,
    )
    logger.info("Done collect_h5parms complexgain")

    logger.info("Start combine_h5parms")
    combined_filename = f"{work_dir}/combined.h5parm"
    combine_h5parms(
        combined_solutions_fast_phase,
        combined_solutions_complex_gain,
        combined_filename,
        "p1p2a2_scalar",
        solset1="sol000",
        solset2="sol000",
        reweight=False,
        cal_names="Patch_1022,Patch_1042,Patch_1075,Patch_136,Patch_151,\
        Patch_152,Patch_231,Patch_235,Patch_313,Patch_34,Patch_341,Patch_375,\
        Patch_423,Patch_456,Patch_47,Patch_479,Patch_51,Patch_809,Patch_865,\
        Patch_900",
        cal_fluxes="1.1334742100000001,1.70710925,3.2476566,5.00693068,\
        1.122316848,3.2364227,0.656659973,4.06428878,1.96108164,1.32103399,\
        1.5094014900000001,0.9435658,0.88880649,0.812606685,\
        6.2081472699999996,1.89063376,1.1275013843000001,13.01872833,\
        3.0365853,1.9651040569999998",
    )

    logger.info("Done combine_h5parms")
    return combined_filename


def predict_1(
    dp3_runner, msin, inputs_dir, work_dir, combined_solutions
):  # pylint: disable= R0914
    """Define predict operation"""

    # Read directions from skymodel file
    directions_list = get_patches(
        f"{inputs_dir}/outlier_1_predict_skymodel.txt"
    )[0]
    directions_str = "],[".join(directions_list)
    directions_str = f"[[{directions_str}]]"

    out_predict = []

    extra_args_applycal = []
    extra_args_applycal.append("predict.applycal.steps=[fastphase]")
    extra_args_applycal.append(
        "predict.applycal.fastphase.correction=phase000"
    )

    msin_filename = os.path.basename(msin)
    for i, start_time in enumerate(START_TIMES):
        logger.info("Running predict for time %s", start_time)
        msout = f"{work_dir}/{msin_filename}.{i}.outlier_1_modeldata"
        dp3_runner.predict(
            msin,
            msout,
            start_time,
            directions_str,
            f"{inputs_dir}/outlier_1_predict_skymodel.txt",
            combined_solutions,
            extra_args_applycal,
        )
        out_predict.append(msout)

    logger.info("Start subtract_sector_models")

    in_imaging = []
    for i, ms_model_time in enumerate(TIMES_MJD):
        logger.info(
            "Running subtract_sector_models for time %s", START_TIMES[i]
        )
        subtract_sector_models(
            msin,
            ",".join(out_predict),
            nr_outliers=1,
            nr_bright=0,
            peel_outliers=True,
            peel_bright=False,
            reweight=False,
            starttime=START_TIMES[i],
            solint_sec=8.01112064,
            solint_hz=976562.5,
            weights_colname="WEIGHT_SPECTRUM",
            uvcut_min=0.0,
            uvcut_max=1000000.0,
            phaseonly=True,
            infix=f".{ms_model_time}",
        )

        path = pathlib.PurePath(msin)

        in_imaging.append(f"{work_dir}/{path.name}.{ms_model_time}_field")

    logger.info("Done subtract_sector_models")
    return in_imaging


def predict_3(dp3_runner, msin, inputs_dir, work_dir, combined_solutions):
    """Define predict operation"""

    directions_str = []
    for i in [1, 2]:
        directions_list = get_patches(
            f"{inputs_dir}/bright_source_{i}_predict_skymodel.txt"
        )[0]
        directions = "],[".join(directions_list)
        directions_str.append(f"[[{directions}]]")

    out_predict = []

    extra_args_applycal = []
    extra_args_applycal.append("predict.applycal.steps=[slowamp,totalphase]")
    extra_args_applycal.append(
        "predict.applycal.slowamp.correction=amplitude000"
    )
    extra_args_applycal.append(
        "predict.applycal.totalphase.correction=phase000"
    )

    logger.info("Start predict directions_1")
    for i, start_time in enumerate(START_TIMES):
        logger.info("Running predict for time %s", start_time)
        msout = f"{msin[i]}.bright_source_1_modeldata"
        dp3_runner.predict(
            msin[i],
            msout,
            start_time,
            directions_str[0],
            f"{inputs_dir}/bright_source_1_predict_skymodel.txt",
            combined_solutions,
            extra_args_applycal,
        )
        out_predict.append(msout)

    logger.info("Start predict directions_2")
    for i, start_time in enumerate(START_TIMES):
        logger.info("Running predict for time %s", start_time)
        msout = f"{msin[i]}.bright_source_2_modeldata"
        dp3_runner.predict(
            msin[i],
            msout,
            start_time,
            directions_str[1],
            f"{inputs_dir}/bright_source_2_predict_skymodel.txt",
            combined_solutions,
            extra_args_applycal,
        )
        out_predict.append(msout)

    logger.info("Start subtract_sector_models")

    in_imaging = []
    for i, start_time in enumerate(START_TIMES):
        logger.info("Running subtract_sector_models for time %s", start_time)
        subtract_sector_models(
            msin[i],
            ",".join(out_predict),
            nr_outliers=0,
            nr_bright=2,
            peel_outliers=False,
            peel_bright=True,
            reweight=False,
            starttime=start_time,
            solint_sec=8.01112064,
            solint_hz=976562.5,
            weights_colname="WEIGHT_SPECTRUM",
            uvcut_min=0.0,
            uvcut_max=1000000.0,
            phaseonly=True,
            infix="",
        )

        path = pathlib.PurePath(msin[i])

        in_imaging.append(f"{work_dir}/{path.name}.sector_1")

    logger.info("Done subtract_sector_models")
    return in_imaging


def image_1(  # pylint: disable=R0913,R0914
    dp3_runner,
    wsclean_runner,
    solutions_to_apply,
    skymodel,
    inputs_dir,
    work_dir,
    input_ms_list,
    mask_filename,
    disable_filter_skymodel,
):  # pylint: disable=W0613
    """Define imaging operation"""
    # ------------------------ Image_1 7:06:40

    input_imaging_ms_list = []
    for i, start_time in enumerate(START_TIMES):
        logger.info("Running applybeam_shift_average for time %s", start_time)
        msout = f"{input_ms_list[i]}.sector_1.prep"
        dp3_runner.applybeam_shift_average(
            input_ms_list[i],
            msout,
            start_time,
        )
        input_imaging_ms_list.append(msout)

    # Create imaging mask
    logger.info("Start blank_image")
    blank_image(
        mask_filename,
        input_image=None,
        vertices_file=f"{inputs_dir}/sector_1_vertices.pkl",
        reference_ra_deg=REFERENCE_RA_DEG,
        reference_dec_deg=REFERENCE_DEC_DEG,
        cellsize_deg=wsclean_runner.imaging_scale,
        imsize=f"{wsclean_runner.imaging_size},\
        {wsclean_runner.imaging_size}",
    )

    logger.info("Start make_region_file")
    facets_file = "regions.ds9"
    make_region_file(
        skymodel,
        float(REFERENCE_RA_DEG),
        float(REFERENCE_DEC_DEG),
        10.0,
        10.0,
        facets_file,
    )

    logger.info("Start run_wsclean")
    tmp_dir = f"{work_dir}/tmp_imaging"
    if not os.path.exists(tmp_dir):
        os.makedirs(tmp_dir)
    wsclean_runner.run_wsclean(
        input_imaging_ms_list,
        facets_file,
        solutions_to_apply,
        mask_filename,
        tmp_dir,
    )

    logger.info("Done run_wsclean")

    logger.info("Start filter_skymodel.py")
    if disable_filter_skymodel:
        logger.info("filter_skymodel is disabled")
    else:
        beam_ms = ", ".join(input_imaging_ms_list)
        print(beam_ms)
        filter_skymodel(
            f"{work_dir}/sector_1-MFS-image.fits",
            f"{work_dir}/sector_1-sources-pb.txt",
            "sector_1",
            f"{inputs_dir}/sector_1_vertices.pkl",
            beam_ms=beam_ms,
            threshisl=4.0,
            threshpix=5.0,
        )
    logger.info("Done filter_skymodel.py")


def image_3(  # pylint: disable=R0913,R0914
    dp3_runner,
    wsclean_runner,
    solutions_to_apply,
    skymodel,
    inputs_dir,
    work_dir,
    input_ms_list,
    mask_filename,
    disable_filter_skymodel,
):
    """Define imaging operation"""

    input_imaging_ms_list = []
    for i, start_time in enumerate(START_TIMES):
        logger.info("Running applybeam_shift_average for time %s", start_time)
        msout = f"{input_ms_list[i]}.prep"
        dp3_runner.applybeam_shift_average(
            input_ms_list[i],
            msout,
            start_time,
        )
        input_imaging_ms_list.append(msout)

    # Create imaging mask
    logger.info("Start blank_image")
    blank_image(
        mask_filename,
        input_image=None,
        vertices_file=f"{inputs_dir}/sector_1_vertices.pkl",
        reference_ra_deg=REFERENCE_RA_DEG,
        reference_dec_deg=REFERENCE_DEC_DEG,
        cellsize_deg=wsclean_runner.imaging_scale,
        imsize=f"{wsclean_runner.imaging_size},\
        {wsclean_runner.imaging_size}",
    )

    logger.info("Start make_region_file")
    facets_file = "regions.ds9"
    make_region_file(
        skymodel,
        float(REFERENCE_RA_DEG),
        float(REFERENCE_DEC_DEG),
        10.0,
        10.0,
        facets_file,
    )

    logger.info("Start run_wsclean")
    tmp_dir = f"{work_dir}/tmp_imaging"
    if not os.path.exists(tmp_dir):
        os.makedirs(tmp_dir)
    wsclean_runner.run_wsclean(
        input_imaging_ms_list,
        facets_file,
        solutions_to_apply,
        mask_filename,
        tmp_dir,
    )

    logger.info("Done run_wsclean")

    logger.info("Start wsclean restore")
    wsclean_runner.restore(
        f"{work_dir}/sector_1-MFS-image",
        f"{inputs_dir}/bright_source_skymodel.txt",
    )
    logger.info("Done  wsclean restore")

    logger.info("Start filter_skymodel.py")
    if disable_filter_skymodel:
        logger.info("filter_skymodel is disabled")
    else:
        beam_ms = ", ".join(input_imaging_ms_list)
        filter_skymodel(
            f"{work_dir}/sector_1-MFS-image.fits",
            f"{work_dir}/sector_1-sources-pb.txt",
            "sector_1",
            f"{inputs_dir}/sector_1_vertices.pkl",
            beam_ms=beam_ms,
            threshisl=3.0,
            threshpix=5.0,
        )
    logger.info("Done filter_skymodel.py")
