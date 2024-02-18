#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# pylint: disable=R0801
" This script defines a SKA LOW self calibration workflow"

import argparse
import logging
import os
from argparse import RawTextHelpFormatter

import numpy as np

from ska_sdp_wflow_low_selfcal.pipeline.dp3_helper import Dp3Runner
from ska_sdp_wflow_low_selfcal.pipeline.operations import (
    calibrate_1,
    calibrate_2,
    calibrate_3,
    image_1,
    image_3,
    predict_1,
    predict_3,
)
from ska_sdp_wflow_low_selfcal.pipeline.support.read_data import (
    get_phase_center,
)
from ska_sdp_wflow_low_selfcal.pipeline.support.skymodel_utils import (
    download_skymodel,
    group_sources,
)
from ska_sdp_wflow_low_selfcal.pipeline.wsclean_helper import WSCleanRunner


def resume_from_operation(given_op, run_single_operation):
    """Define which operations should be skipped based on the operation given
    as input"""

    logger = logging.getLogger("ska-sdp-wflow-low-selfcal")
    # List of operations. Each entry is a tuple of the name of the operation
    # and the expected run time in minutes
    operations = []
    operations.append(("calibrate_1", 100))
    operations.append(("predict_1", 35))
    operations.append(("image_1", 320))
    operations.append(("calibrate_2", 120))
    operations.append(("image_2", 300))
    operations.append(("calibrate_3", 240))
    operations.append(("predict_3", 104))
    operations.append(("image_3", 380))
    skip_vector = np.zeros(len(operations), dtype=bool)

    index = -1
    for i, operation in enumerate(operations):
        if given_op in operation:
            index = i
    if index < 0:
        logger.info(
            "run_pipeline:: can not resume from unknown operation '%s'. "
            "Starting from calibrate_1.",
            given_op,
        )
        return skip_vector
    if run_single_operation:
        skip_vector[0:index] = True
        skip_vector[index + 1 : :] = True  # noqa: E203
    else:
        skip_vector[0:index] = True

    total_time = 0
    for i, operation in enumerate(operations):
        if ~skip_vector[i]:
            total_time += operation[1]

    single_op_time = (
        str(int(operations[index][1] / 60))
        + "h"
        + str(operations[index][1] % 60)
        + "min"
    )
    tot_time = str(int(total_time / 60)) + "h" + str(total_time % 60) + "min"
    logger.info(
        "Start from %s. Single operation runtime %s. Expected total "
        "runtime %s",
        given_op,
        single_op_time,
        tot_time,
    )

    return skip_vector


def run_pipeline(
    dp3_exe,
    wsclean_exe,
    input_ms,
    inputs_folder,
    working_directory,
    resume_from_op,
    run_single_operation,
    imaging_size,
    imaging_scale,
    imaging_taper_gaussian,
    calibration_nchannels,
    disable_filter_skymodel,
    combine_dp3_calls=False,
):  # pylint: disable=W0613, R0914, R0912, R0913, R0915
    """Run pipeline"""

    # Convert relative paths to absolute paths
    input_ms = os.path.abspath(input_ms)
    input_ms_filename = os.path.basename(input_ms)
    inputs_folder = os.path.abspath(inputs_folder)
    working_directory = os.path.abspath(working_directory)
    if not os.path.exists(working_directory):
        os.makedirs(working_directory)

    os.chdir(working_directory)

    if os.getenv("RAPTHOR_LOG_FILE"):
        rapthor_filename = os.getenv("RAPTHOR_LOG_FILE")
    else:
        rapthor_filename = "logging.log"

    handler = logging.FileHandler(f"{working_directory}/{rapthor_filename}")
    handler.setLevel(level=logging.INFO)
    handler.setFormatter(
        logging.Formatter(
            "%(asctime)s,%(msecs)d %(name)s %(levelname)s %(message)s",
            datefmt="%H:%M:%S",
        )
    )

    logger = logging.getLogger("ska-sdp-wflow-low-selfcal")
    logger.addHandler(handler)

    skip = resume_from_operation(resume_from_op, run_single_operation)
    dp3_runner = Dp3Runner(dp3_exe, calibration_nchannels)
    wsclean_runner = WSCleanRunner(
        wsclean_exe, imaging_size, imaging_scale, imaging_taper_gaussian
    )

    logger.info("run_pipeline:: Read phase center")
    [ra, dec] = get_phase_center(input_ms)  # pylint: disable=C0103

    logger.info("phase center coordinates are: RA %s, DEC %s ", ra, dec)

    logger.info("run_pipeline:: Download skymodel")
    download_skymodel(ra, dec, "initial.skymodel")

    if not os.path.isfile("calibrate_1.skymodel"):
        logger.info("run_pipeline:: Group sources in patches")
        group_sources(
            input_ms,
            "initial.skymodel",
            "calibrate_1.skymodel",
        )
    else:
        logger.info(
            "run_pipeline:: "
            "calibrate_1.skymodel already exists. Skipping source grouping "
            ""
        )

    # Calibrate_1 0:52:21

    logger.info("run_pipeline:: Start calibrate_1")
    if skip[0]:
        logger.info("run_pipeline:: SKIP calibrate_1")
        solutions = f"{working_directory}/in_predict_1_field-solutions.h5"
    else:
        solutions = calibrate_1(
            dp3_runner, input_ms, "calibrate_1.skymodel", working_directory
        )
    logger.info("run_pipeline:: Done calibrate_1")

    # Predict_1 0:18:10
    logger.info("run_pipeline:: Start predict_1")
    if skip[1]:
        logger.info("run_pipeline:: SKIP predict_1")
        ms_list_no_outliers = [
            f"{working_directory}/{input_ms_filename}.mjd5020557063_field",
            f"{working_directory}/{input_ms_filename}.mjd5020559947_field",
            f"{working_directory}/{input_ms_filename}.mjd5020562823_field",
            f"{working_directory}/{input_ms_filename}.mjd5020565707_field",
            f"{working_directory}/{input_ms_filename}.mjd5020568583_field",
            f"{working_directory}/{input_ms_filename}.mjd5020571459_field",
            f"{working_directory}/{input_ms_filename}.mjd5020574343_field",
            f"{working_directory}/{input_ms_filename}.mjd5020577219_field",
            f"{working_directory}/{input_ms_filename}.mjd5020580103_field",
            f"{working_directory}/{input_ms_filename}.mjd5020582979_field",
        ]
    else:
        ms_list_no_outliers = predict_1(
            dp3_runner, input_ms, inputs_folder, working_directory, solutions
        )
    logger.info("run_pipeline:: Done predict_1")

    # Image_1 7:06:40
    logger.info("run_pipeline:: Start image_1")
    if skip[2]:
        logger.info("run_pipeline:: SKIP image_1")
    else:
        imaging_1_dir = f"{working_directory}/image_1"
        if not os.path.exists(imaging_1_dir):
            os.makedirs(imaging_1_dir)
        os.chdir(imaging_1_dir)
        image_1(
            dp3_runner,
            wsclean_runner,
            solutions,
            f"{inputs_folder}/in_calibration_1.skymodel",
            inputs_folder,
            imaging_1_dir,
            ms_list_no_outliers,
            f"{imaging_1_dir}/im_1_sector_1_mask.fits",
            disable_filter_skymodel,
        )
        os.chdir(working_directory)
    logger.info("run_pipeline:: Done image_1")

    # Calibrate_2 1:04:16
    logger.info("run_pipeline:: Start calibrate_2")
    if skip[3]:
        logger.info("run_pipeline:: SKIP calibrate_2")
        solutions_2 = f"{working_directory}/in_predict_2_field-solutions.h5"
    else:
        solutions_2 = calibrate_2(
            dp3_runner, ms_list_no_outliers, inputs_folder, working_directory
        )
    logger.info("run_pipeline:: Done calibrate_2")

    # Image_2 07:27:09
    logger.info("run_pipeline:: Start image_2")
    if skip[4]:
        logger.info("run_pipeline:: SKIP image_2")
    else:
        imaging_2_dir = f"{working_directory}/image_2"
        if not os.path.exists(imaging_2_dir):
            os.makedirs(imaging_2_dir)
        os.chdir(imaging_2_dir)
        image_1(
            dp3_runner,
            wsclean_runner,
            solutions_2,
            f"{inputs_folder}/in_calibration_2.skymodel",
            inputs_folder,
            imaging_2_dir,
            ms_list_no_outliers,
            f"{imaging_2_dir}/im_2_sector_1_mask.fits",
            disable_filter_skymodel,
        )
        os.chdir(working_directory)
    logger.info("run_pipeline:: Done image_2")

    # Calibrate_3 02:14:40
    logger.info("run_pipeline:: Start calibrate_3")
    if skip[5]:
        logger.info("run_pipeline:: SKIP calibrate_3")
        solutions_3 = f"{working_directory}/combined.h5parm"
    else:
        solutions_3 = calibrate_3(
            dp3_runner,
            ms_list_no_outliers,
            inputs_folder,
            working_directory,
            combine_dp3_calls,
        )
    logger.info("run_pipeline:: Done calibrate_3")

    # Predict_3 00:53:04
    logger.info("run_pipeline:: Start predict_3")
    if skip[6]:
        logger.info("run_pipeline:: SKIP predict_3")
        suffix = "_field.sector_1"
        ms_list_no_outliers_no_bright_sources = [
            f"{working_directory}/{input_ms_filename}.mjd5020557063{suffix}",
            f"{working_directory}/{input_ms_filename}.mjd5020559947{suffix}",
            f"{working_directory}/{input_ms_filename}.mjd5020562823{suffix}",
            f"{working_directory}/{input_ms_filename}.mjd5020565707{suffix}",
            f"{working_directory}/{input_ms_filename}.mjd5020568583{suffix}",
            f"{working_directory}/{input_ms_filename}.mjd5020571459{suffix}",
            f"{working_directory}/{input_ms_filename}.mjd5020574343{suffix}",
            f"{working_directory}/{input_ms_filename}.mjd5020577219{suffix}",
            f"{working_directory}/{input_ms_filename}.mjd5020580103{suffix}",
            f"{working_directory}/{input_ms_filename}.mjd5020582979{suffix}",
        ]
    else:
        ms_list_no_outliers_no_bright_sources = predict_3(
            dp3_runner,
            ms_list_no_outliers,
            inputs_folder,
            working_directory,
            solutions_3,
        )
    logger.info("run_pipeline:: Done predict_3")

    # Image_3 05:20:55
    logger.info("run_pipeline:: Start image_3")
    if skip[7]:
        logger.info("run_pipeline:: SKIP image_3")
    else:
        imaging_3_dir = f"{working_directory}/image_3"
        if not os.path.exists(imaging_3_dir):
            os.makedirs(imaging_3_dir)
        os.chdir(imaging_3_dir)
        image_3(
            dp3_runner,
            wsclean_runner,
            solutions_3,
            f"{inputs_folder}/in_calibration_3.skymodel",
            inputs_folder,
            imaging_3_dir,
            ms_list_no_outliers_no_bright_sources,
            f"{imaging_3_dir}/im_3_sector_1_mask.fits",
            disable_filter_skymodel,
        )
        os.chdir(working_directory)

    logger.info("run_pipeline:: Done image_3")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Run direction dependent calbration pipeline.\n",
        formatter_class=RawTextHelpFormatter,
    )
    parser.add_argument(
        "--dp3_path",
        help="Path to DP3 executable",
        type=str,
        default="DP3",
    )
    parser.add_argument(
        "--wsclean_path",
        help="Path to WSClean executable",
        type=str,
        default="wsclean",
    )
    parser.add_argument(
        "--input_ms",
        help="Path to input Measurement Set",
        type=str,
        default="midbands.ms",
    )
    parser.add_argument(
        "--extra_inputs_dir",
        help="Path to input files. Those are needed to run the pipeline.",
        type=str,
        default="inputs",
    )
    parser.add_argument(
        "--work_dir",
        help="Path to working directory, where all otput files will be saved",
        type=str,
        default="working_dir",
    )
    parser.add_argument(
        "--resume_from_operation",
        help="Resume from any given operation",
        type=str,
        default="calibrate_1",
    )
    parser.add_argument(
        "--run_single_operation",
        help="Only run the operation given via resume_from_operation",
        type=str,
        default="False",
    )
    parser.add_argument(
        "--combine_dp3_calls",
        help="Combine multiple DDECal runs into a single DP3 command",
        type=str,
        default="False",
    )
    parser.add_argument(
        "--imaging_size",
        help="Image width in pixels. Height will be the same.",
        type=str,
        default="24394",
    )
    parser.add_argument(
        "--imaging_scale",
        help="Angular size of a single pixel",
        type=str,
        default="0.00034722222222222224",
    )
    parser.add_argument(
        "--imaging_taper_gaussian",
        help="A Gaussian taper is selected with imaging_taper_gaussian \
        <beamsize>. The beamsize is by default in arcseconds, but can be \
        given with different units, e.g. “0.04deg”",
        type=str,
        default="0.0",
    )
    parser.add_argument(
        "--calibration_nchannels",
        help="Number of channels to be used per each calibration solution",
        type=str,
        default="10",
    )
    parser.add_argument(
        "--disable_filter_skymodel",
        help='Option to disable the function "filter_skymodel" in the \
        pipeline. If True, the skymodels to start each iteration should be \
        available in the inputs folder.',
        type=str,
        default="False",
    )

    args = parser.parse_args()

    run_pipeline(
        args.dp3_path,
        args.wsclean_path,
        args.input_ms,
        args.extra_inputs_dir,
        args.work_dir,
        args.resume_from_operation,
        args.run_single_operation == "True",
        args.imaging_size,
        args.imaging_scale,
        args.imaging_taper_gaussian,
        args.calibration_nchannels,
        args.disable_filter_skymodel == "True",
        args.combine_dp3_calls == "True",
    )
