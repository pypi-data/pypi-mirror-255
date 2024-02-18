#!/usr/bin/env python3

#  SPDX-License-Identifier: BSD-3-Clause

# -*- coding: utf-8 -*-
" This script defines a SKA LOW self calibration workflow"

import argparse
import logging
import os
from glob import glob

import numpy as np

from ska_sdp_wflow_low_selfcal.pipeline.distribute import (
    Distributor,
    start_dask,
)
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
from ska_sdp_wflow_low_selfcal.pipeline.support.miscellaneous import (
    make_wcs,
    read_vertices_pixel_coordinates,
)
from ska_sdp_wflow_low_selfcal.pipeline.support.read_data import (
    calculate_n_chunks,
    get_phase_center,
    get_start_times,
)
from ska_sdp_wflow_low_selfcal.pipeline.support.skymodel_utils import (
    define_sector,
    download_skymodel,
    get_bright_sources,
    get_outliers,
    group_sources,
    split_skymodel_file,
)
from ska_sdp_wflow_low_selfcal.pipeline.version import check_version
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


def file_exists(filename, function):
    """Check if a given file exists and generate logs"""

    logger = logging.getLogger("ska-sdp-wflow-low-selfcal")
    if not os.path.isfile(filename):
        logger.info("run_pipeline:: %s", function)
        return False

    logger.info(
        "run_pipeline:: %s already exists. Skipping %s ",
        filename,
        function,
    )
    return True


def get_filenames(
    working_dir,
    input_ms_path,
    data_fraction,
    minimum_time,
    suffix,
):
    """
    Get a list of filenames based on the input parameters.

    Args:
        working_dir (str): Path to the working directory.
        input_ms_path (str): Path to the input measurement set.
        data_fraction (float): Fraction of data to be processed.
        minimum_time (float): Minimum time interval for splitting the data.
        suffix (str): Suffix to be appended to the generated filenames.

    Returns:
        list: A list of filenames generated based on the input parameters.
    """

    logger = logging.getLogger("ska-sdp-wflow-low-selfcal")

    input_ms_filename = os.path.basename(input_ms_path)
    n_chunks = calculate_n_chunks(
        input_ms_path,
        data_fraction,
        minimum_time,
    )
    mjd_times = [
        "mjd" + str(int(one_time))
        for one_time in get_start_times(input_ms_path, n_chunks)
    ]

    ms_list = []
    for mjd_time in mjd_times:
        file_name = f"{working_dir}/{input_ms_filename}.{mjd_time}_{suffix}"

        if not os.path.exists(file_name):
            logger.error(
                "run_pipeline:: File does not exist: %s. Run calibrate "
                "operation first.",
                file_name,
            )
        ms_list.append(file_name)
        logger.info("run_pipeline:: File collected:%s", file_name)

    return ms_list


def run_pipeline(
    settings,
    input_ms,
    working_directory,
    resume_from_op,
    run_single_operation,
    combine_dp3_calls=False,
    run_distributed=False,
    ignore_version_errors=False,
):  # pylint: disable=R0914, R0912, R0913, R0915
    """Run pipeline"""

    if not settings.logging_tag:
        settings.logging_tag = str(os.getpid())

    # Convert relative paths to absolute paths
    input_ms = os.path.abspath(input_ms)
    working_directory = os.path.abspath(working_directory)
    if not os.path.exists(working_directory):
        os.makedirs(working_directory)

    os.chdir(working_directory)

    log_filename = (
        f"{working_directory}/wflow-low-selfcal.{settings.logging_tag}.log"
    )
    handler = logging.FileHandler(log_filename)
    handler.setLevel(level=logging.INFO)
    handler.setFormatter(
        logging.Formatter(
            "%(asctime)s,%(msecs)d %(name)s %(levelname)s %(message)s",
            datefmt="%H:%M:%S",
        )
    )

    logger = logging.getLogger("ska-sdp-wflow-low-selfcal")
    logger.addHandler(handler)

    if run_distributed:
        start_dask(logger, settings.logging_tag)

    skip = resume_from_operation(resume_from_op, run_single_operation)

    # Check version
    check_successful = check_version(settings.dp3_path, settings.wsclean_path)
    if not check_successful:
        if not ignore_version_errors:
            raise RuntimeError(
                "Version check failed. See log file "
                f"{log_filename} for more info"
            )

    dp3_runner = Distributor(  # pylint: disable=E1102
        Dp3Runner, run_distributed
    )(settings)
    wsclean_runner = WSCleanRunner(
        settings,
        run_distributed,
    )

    logger.info("run_pipeline:: Read phase center")
    [ra, dec] = get_phase_center(input_ms)

    logger.info("phase center coordinates are: RA %s, DEC %s ", ra, dec)

    initial_skymodel_filename = "initial.skymodel"
    if not file_exists(initial_skymodel_filename, "Download skymodel"):
        download_skymodel(ra, dec, initial_skymodel_filename)

    calibrate_skymodel_filename = [
        f"{working_directory}/calibrate_1.skymodel",
        f"{working_directory}/calibrate_2.skymodel",
        f"{working_directory}/calibrate_3.skymodel",
    ]

    if not file_exists(
        calibrate_skymodel_filename[0], "group sources in patches"
    ):
        group_sources(
            input_ms,
            f"{working_directory}/{initial_skymodel_filename}",
            calibrate_skymodel_filename[0],
        )

    vertices_filename = f"{working_directory}/sector_1_vertices.pkl"
    sector_skymodel_filename = f"{working_directory}/sector.skymodel"
    sector_vertices = []

    if not file_exists(vertices_filename, "define vertices file"):
        sector_vertices = define_sector(
            calibrate_skymodel_filename[0],
            sector_skymodel_filename,
            input_ms,
        )
    else:
        wcs = make_wcs(ra, dec)
        sector_vertices = read_vertices_pixel_coordinates(
            vertices_filename, wcs
        )

    # Calibrate_1 0:52:21

    logger.info("run_pipeline:: Start calibrate_1")
    if skip[0]:
        logger.info("run_pipeline:: SKIP calibrate_1")
        solutions = f"{working_directory}/in_predict_1_field-solutions.h5"
    else:
        solutions = calibrate_1(
            dp3_runner,
            input_ms,
            calibrate_skymodel_filename[0],
            working_directory,
            settings,
        )
    logger.info("run_pipeline:: Done calibrate_1")

    # Predict_1 0:18:10

    logger.info("run_pipeline:: Start predict_1")
    outliers_skymodel_filename = (
        f"{working_directory}/outlier_1_predict.skymodel"
    )
    if skip[1]:
        logger.info("run_pipeline:: SKIP predict_1")
        ms_list_no_outliers = get_filenames(
            working_directory,
            input_ms,
            settings.data_fraction,
            settings.minimum_time,
            "field",
        )

    else:
        get_outliers(
            calibrate_skymodel_filename[0],
            sector_skymodel_filename,
            outliers_skymodel_filename,
        )
        ms_list_no_outliers = predict_1(
            dp3_runner,
            input_ms,
            outliers_skymodel_filename,
            working_directory,
            solutions,
            settings,
        )
    logger.info("run_pipeline:: Done predict_1")

    # Image_1 7:06:40
    logger.info("run_pipeline:: Start image_1")
    imaging_1_dir = f"{working_directory}/image_1"
    if skip[2]:
        logger.info("run_pipeline:: SKIP image_1")
    else:
        if not os.path.exists(imaging_1_dir):
            os.makedirs(imaging_1_dir)
        os.chdir(imaging_1_dir)

        image_1(
            dp3_runner,
            wsclean_runner,
            solutions,
            calibrate_skymodel_filename[0],
            vertices_filename,
            imaging_1_dir,
            ms_list_no_outliers,
            f"{imaging_1_dir}/im_1_sector_1_mask.fits",
        )
        os.chdir(working_directory)
    logger.info("run_pipeline:: Done image_1")

    # Calibrate_2 1:04:16
    logger.info("run_pipeline:: Start calibrate_2")

    if skip[3]:
        logger.info("run_pipeline:: SKIP calibrate_2")
        solutions_2 = f"{working_directory}/in_predict_2_field-solutions.h5"
    else:
        if not file_exists(
            calibrate_skymodel_filename[1], "group sources in patches"
        ):
            group_sources(
                input_ms,
                f"{imaging_1_dir}/sector_1.true_sky.txt",
                calibrate_skymodel_filename[1],
                f"{imaging_1_dir}/sector_1.apparent_sky.txt",
                target_flux=0.4,
                max_directions=30,
                find_sources=False,
            )

        solutions_2 = calibrate_2(
            dp3_runner,
            ms_list_no_outliers,
            calibrate_skymodel_filename[1],
            working_directory,
        )
    logger.info("run_pipeline:: Done calibrate_2")

    # Image_2 07:27:09
    logger.info("run_pipeline:: Start image_2")
    imaging_2_dir = f"{working_directory}/image_2"
    if skip[4]:
        logger.info("run_pipeline:: SKIP image_2")
    else:
        if not os.path.exists(imaging_2_dir):
            os.makedirs(imaging_2_dir)
        os.chdir(imaging_2_dir)
        image_1(
            dp3_runner,
            wsclean_runner,
            solutions_2,
            calibrate_skymodel_filename[1],
            vertices_filename,
            imaging_2_dir,
            ms_list_no_outliers,
            f"{imaging_2_dir}/im_2_sector_1_mask.fits",
        )
        os.chdir(working_directory)
    logger.info("run_pipeline:: Done image_2")

    # Calibrate_3 02:14:40
    logger.info("run_pipeline:: Start calibrate_3")

    calibrators_skymodel_filename = "calibrators.skymodel"
    bright_sources_apparent_sky = "bs_apparent.skymodel"
    bright_sources_skymodel_prefix = "bright_sources"
    bright_sources_list = glob(f"{bright_sources_skymodel_prefix}*")
    if skip[5]:
        logger.info("run_pipeline:: SKIP calibrate_3")
        solutions_3 = f"{working_directory}/combined.h5parm"
    else:
        if (
            not file_exists(
                calibrate_skymodel_filename[2], "group sources in patches"
            )
            or not file_exists(
                calibrators_skymodel_filename, "Create calibrators skymodel"
            )
            or not bright_sources_list
        ):
            group_sources(
                input_ms,
                f"{imaging_2_dir}/sector_1.true_sky.txt",
                calibrate_skymodel_filename[2],
                f"{imaging_2_dir}/sector_1.apparent_sky.txt",
                target_flux=0.3,
                max_directions=40,
                find_sources=False,
                bright_source_apparent_filename=bright_sources_apparent_sky,
            )
            logger.info("run_pipeline:: Create bright sources skymodel")
            bright_sources_skymodel = get_bright_sources(
                calibrate_skymodel_filename[2],
                bright_sources_apparent_sky,
                calibrators_skymodel_filename,
                input_ms,
                sector_vertices,
            )
            logger.info("run_pipeline:: Split bright sources skymodel file")
            bright_sources_list = split_skymodel_file(
                bright_sources_skymodel, bright_sources_skymodel_prefix
            )
        skymodels = {
            "grouped": calibrate_skymodel_filename[2],
            "calibrators": calibrators_skymodel_filename,
        }
        solutions_3 = calibrate_3(
            dp3_runner,
            ms_list_no_outliers,
            skymodels,
            working_directory,
            combine_dp3_calls,
        )
    logger.info("run_pipeline:: Done calibrate_3")

    # Predict_3 00:53:04
    logger.info("run_pipeline:: Start predict_3")
    if skip[6]:
        logger.info("run_pipeline:: SKIP predict_3")
        # When skipping predict_3, we need to collect the ms files available
        # in the working directory. It is important that the files in the list
        # are sorted in time, otherwise the imaging operation on the
        # concatenated MS will fail.

        ms_list_no_outliers_no_bright_sources = get_filenames(
            working_directory,
            input_ms,
            settings.data_fraction,
            settings.minimum_time,
            "field.sector_1",
        )

    else:
        if not bright_sources_list:
            logger.error(
                "run_pipeline:: bright sources skymodels are not "
                "available. Run calibrate_3 operation to generate them."
            )
        ms_list_no_outliers_no_bright_sources = predict_3(
            dp3_runner,
            ms_list_no_outliers,
            bright_sources_list,
            working_directory,
            solutions_3,
        )
    logger.info("run_pipeline:: Done predict_3")

    # Image_3 05:20:55
    logger.info("run_pipeline:: Start image_3")
    imaging_3_dir = f"{working_directory}/image_3"
    if skip[7]:
        logger.info("run_pipeline:: SKIP image_3")
    else:
        if not os.path.exists(imaging_3_dir):
            os.makedirs(imaging_3_dir)
        os.chdir(imaging_3_dir)
        image_3(
            dp3_runner,
            wsclean_runner,
            solutions_3,
            calibrate_skymodel_filename[2],
            vertices_filename,
            imaging_3_dir,
            ms_list_no_outliers_no_bright_sources,
            f"{imaging_3_dir}/im_3_sector_1_mask.fits",
            f"{working_directory}/{bright_sources_skymodel_prefix}.skymodel",
        )
        os.chdir(working_directory)

    logger.info("run_pipeline:: Done image_3")


def main():
    """
    This method parses the arguments passed via command line and passes them
    to the run_pipeline function
    """
    parser = argparse.ArgumentParser(
        description="Run direction dependent calibration pipeline.\n",
        formatter_class=argparse.RawTextHelpFormatter,
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
        "--work_dir",
        help="Path to working directory, where all output files will be saved",
        type=str,
        default="working_dir",
    )
    parser.add_argument(
        "--logging_tag",
        help="Tag for log files. Defaults to the process id.",
        type=str,
        default="",
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
        "--data_fraction",
        help="Fraction of data to process. Default is 0.2",
        type=float,
        default=0.2,
    )
    parser.add_argument(
        "--minimum_time",
        help="Minimum time to process consecutively, in seconds.",
        type=float,
        default=600.0,
    )
    parser.add_argument(
        # TODO Use dashes to separate words.
        # Other options contain both dashes and underscores
        # Generally dashes only in command line options is preferred,
        # but it should be applied consistently then.
        "--run_distributed",
        help="Distribute over SLURM cluster using Dask and MPI",
        type=str,
        default="False",
    )
    parser.add_argument(
        "--parallel_gridding",
        help="Number of parallel gridding tasks in WSClean",
        type=str,
        default="16",
    )
    parser.add_argument(
        "--ignore_version_errors",
        help="If True, the pipeline will run also if there is a mismatch in \
        the expected DP3 and WSClean commits, or if multiple binaries are \
        found for casacore and everybeam",
        type=str,
        default="False",
    )

    args = parser.parse_args()

    # DP3 only needs custom environmental variables on the CI.
    args.dp3_environment = None

    run_pipeline(
        args,
        args.input_ms,
        args.work_dir,
        args.resume_from_operation,
        args.run_single_operation == "True",
        args.combine_dp3_calls == "True",
        args.run_distributed == "True",
        args.ignore_version_errors == "True",
    )


if __name__ == "__main__":
    main()
