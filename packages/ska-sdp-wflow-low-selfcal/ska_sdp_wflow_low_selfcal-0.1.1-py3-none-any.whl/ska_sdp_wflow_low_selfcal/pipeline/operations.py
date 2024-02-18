#  SPDX-License-Identifier: BSD-3-Clause

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
from ska_sdp_wflow_low_selfcal.pipeline.support.miscellaneous import (
    concatenate_ms,
)
from ska_sdp_wflow_low_selfcal.pipeline.support.read_data import (
    calculate_n_chunks,
    calculate_n_times,
    compute_observation_width,
    get_channel_width,
    get_imaging_n_iterations,
    get_observation_params,
    get_patches,
    get_phase_center,
    get_start_times,
    get_time_interval,
)
from ska_sdp_wflow_low_selfcal.pipeline.support.skymodel_utils import (
    get_flux_per_patch,
)
from ska_sdp_wflow_low_selfcal.pipeline.support.subtract_sector_models import (
    subtract_sector_models,
)
from ska_sdp_wflow_low_selfcal.pipeline.support.time import human_readable_time

logger = logging.getLogger("ska-sdp-wflow-low-selfcal")


def calibrate_1(dp3_runner, msin, skymodel, work_dir, settings):
    """Define calibrate operation"""

    # ------------------------ Calibrate_1 0:52:21
    logger.info("Start calibrate_1")

    # split the MS in chunks covering 20% of the total time
    n_chunks = calculate_n_chunks(
        msin, settings.data_fraction, settings.minimum_time
    )
    logger.info("Splitting the measurmenet set in %s time chunks", n_chunks)

    # Get the start times for the data-time range splitted in chunks.
    time_list = get_start_times(msin, n_chunks)

    # Convert each value to iso-time format.
    start_times = [human_readable_time(one_time) for one_time in time_list]

    output_solutions_filenames = []
    for i, start_time in enumerate(start_times):
        logger.info("Running calibrate_scalarphase for time %s", start_time)
        output_solution_filename = (
            f"{work_dir}/out_calibration_1_fast_phase_" + str(i) + ".h5parm"
        )
        dp3_runner.calibrate_scalarphase(
            msin,
            start_time,
            calculate_n_times(msin),
            os.path.join(work_dir, skymodel),
            False,
            output_solution_filename,
        )
        output_solutions_filenames.append(output_solution_filename)
    dp3_runner.join()

    # Stitch all solutions together
    logger.info("Start collect_h5parms")
    combined_solutions = f"{work_dir}/in_predict_1_field-solutions.h5"
    collect_h5parms(
        output_solutions_filenames,
        combined_solutions,
    )

    logger.info("Done collect_h5parms")
    return combined_solutions


def calibrate_2(dp3_runner, msin_after_predict, skymodel, work_dir):
    """Define calibrate operation"""

    output_solutions_filenames = []
    for i, measurement_set in enumerate(msin_after_predict):
        logger.info(
            "Running calibrate_scalarphase for measurement set %s",
            measurement_set,
        )
        output_solution_filename = (
            f"{work_dir}/out_calibration_2_fast_phase_" + str(i) + ".h5parm"
        )
        dp3_runner.calibrate_scalarphase(
            measurement_set,
            None,
            calculate_n_times(measurement_set),
            skymodel,
            False,
            output_solution_filename,
        )
        output_solutions_filenames.append(output_solution_filename)
    dp3_runner.join()

    # Stitch all solutions together
    logger.info("Start collect_h5parms")
    combined_solutions = f"{work_dir}/in_predict_2_field-solutions.h5"
    collect_h5parms(
        output_solutions_filenames,
        combined_solutions,
    )

    logger.info("Done collect_h5parms")

    return combined_solutions


def calibrate_3(
    dp3_runner,
    msin_list,
    skymodels,
    work_dir,
    combine=False,
):  # pylint: disable=too-many-locals
    """Define calibrate operation in third major iteration
    Parameters
    ----------
    dp3_runner : DP3Runner object
    msin_list: list
        Contains the paths to input measurement sets
    skymodels: Python dictionary containing two skymodel's filenames
        "grouped" is the input skymodel for the calibration operation
        "calibrators" contains only calibrator sources, and is used to
        calculate the flux per each facet
    work_dir: string
        Path to working directory
    combine: bool
        Option to combine scalarphase and complexgain calibration in a single
        DP3 operation

    Returns
    -------
    combined_filename : string
        Path to the calibration solution
    """

    output_solutions_filenames_scalarphase = []
    output_solutions_filenames_complexgain = []
    for i, measurement_set in enumerate(msin_list):
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
                "Running calibrate_scalarphase for measurement set %s",
                measurement_set,
            )
            calibrate_scalarphase_result = dp3_runner.calibrate_scalarphase(
                measurement_set,
                None,
                calculate_n_times(measurement_set),
                skymodels["grouped"],
                True,
                single_solution_scalarphase,
            )
            logger.info(
                "Running calibrate_complexgain for measurement set %s",
                measurement_set,
            )
            dp3_runner.calibrate_complexgain(
                measurement_set,
                None,
                calculate_n_times(measurement_set),
                skymodels["grouped"],
                single_solution_scalarphase,
                single_solution_complexgain,
                depends_on=calibrate_scalarphase_result,
            )
        else:
            logger.info(
                "Running calibrate_scalarphase+complexgain "
                "for measurement set %s",
                measurement_set,
            )
            dp3_runner.calibrate_scalarphase_and_complexgain(
                measurement_set,
                None,
                calculate_n_times(measurement_set),
                skymodels["grouped"],
                True,
                single_solution_scalarphase,
                single_solution_complexgain,
            )
    dp3_runner.join()

    # Stitch all solutions together
    logger.info("Start collect_h5parms scalarphase")
    combined_solutions_fast_phase = (
        f"{work_dir}/out-cal3-fastphase-solutions.h5"
    )
    collect_h5parms(
        output_solutions_filenames_scalarphase,
        combined_solutions_fast_phase,
    )
    logger.info("Done collect_h5parms scalarphase")

    logger.info("Start collect_h5parms complexgain")
    combined_solutions_complex_gain = (
        f"{work_dir}/out-cal3-complexgain-solutions.h5"
    )
    collect_h5parms(
        output_solutions_filenames_complexgain,
        combined_solutions_complex_gain,
    )
    logger.info("Done collect_h5parms complexgain")

    logger.info("Start combine_h5parms")
    combined_filename = f"{work_dir}/combined.h5parm"

    directions_list, flux_per_facet = get_flux_per_patch(
        skymodels["calibrators"]
    )

    combine_h5parms(
        combined_solutions_fast_phase,
        combined_solutions_complex_gain,
        combined_filename,
        "p1p2a2_scalar",
        solset1="sol000",
        solset2="sol000",
        reweight=False,
        cal_names=",".join(directions_list),
        cal_fluxes=",".join(str(num) for num in flux_per_facet),
    )

    logger.info("Done combine_h5parms")
    return combined_filename


def predict_1(
    dp3_runner,
    msin,
    outliers_skymodel_filename,
    work_dir,
    combined_solutions,
    settings,
):  # pylint: disable= too-many-locals, too-many-arguments
    """Define predict operation"""

    # Read directions from skymodel file
    directions_list = get_patches(outliers_skymodel_filename)[0]
    directions_str = "],[".join(directions_list)
    directions_str = f"[[{directions_str}]]"

    out_predict = []

    extra_args_applycal = []
    extra_args_applycal.append("predict.applycal.steps=[fastphase]")
    extra_args_applycal.append(
        "predict.applycal.fastphase.correction=phase000"
    )

    # Get the start times for the data-time range splitted
    # in ten intervals.
    time_list = get_start_times(
        msin,
        calculate_n_chunks(
            msin,
            settings.data_fraction,
            settings.minimum_time,
        ),
    )

    # Convert each value to iso-time format.
    start_times = [human_readable_time(one_time) for one_time in time_list]

    msin_filename = os.path.basename(msin)
    for i, start_time in enumerate(start_times):
        logger.info("Running predict for time %s", start_time)
        msout = f"{work_dir}/{msin_filename}.{i}.outlier_1_modeldata"
        dp3_runner.predict(
            msin,
            msout,
            start_time,
            calculate_n_times(msin),
            directions_str,
            outliers_skymodel_filename,
            combined_solutions,
            extra_args_applycal,
        )
        out_predict.append(msout)
    dp3_runner.join()

    logger.info("Start subtract_sector_models")

    # Truncates each value in time_list to the integer
    # towards zero, convet to string and prefix it with "mjd".
    mjd_times = ["mjd" + str(int(one_time)) for one_time in time_list]

    in_imaging = []
    for i, ms_model_time in enumerate(mjd_times):
        logger.info(
            "Running subtract_sector_models for time %s", start_times[i]
        )
        subtract_sector_models(
            msin,
            ",".join(out_predict),
            nr_outliers=1,
            nr_bright=0,
            peel_outliers=True,
            peel_bright=False,
            reweight=False,
            starttime=start_times[i],
            solint_sec=get_time_interval(msin),
            solint_hz=get_channel_width(msin),
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


def predict_3(
    dp3_runner, msin, bright_sources_list, work_dir, combined_solutions
):
    """Define predict operation"""

    # pylint: disable=too-many-locals

    directions_str = []
    for i in [0, 1]:
        directions_list = get_patches(bright_sources_list[i])[0]
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
    for measurement_set in msin:
        logger.info("Running predict for measurement set %s", measurement_set)
        msout = f"{measurement_set}.bright_source_1_modeldata"
        dp3_runner.predict(
            measurement_set,
            msout,
            None,
            calculate_n_times(msin),
            directions_str[0],
            bright_sources_list[0],
            combined_solutions,
            extra_args_applycal,
        )
        out_predict.append(msout)

    logger.info("Start predict directions_2")
    for measurement_set in msin:
        logger.info("Running predict for measurement set %s", measurement_set)
        msout = f"{measurement_set}.bright_source_2_modeldata"
        dp3_runner.predict(
            measurement_set,
            msout,
            None,
            calculate_n_times(msin),
            directions_str[1],
            bright_sources_list[1],
            combined_solutions,
            extra_args_applycal,
        )
        out_predict.append(msout)

    dp3_runner.join()

    logger.info("Start subtract_sector_models")

    in_imaging = []
    for measurement_set in msin:
        logger.info(
            "Running subtract_sector_models for measurement set %s",
            measurement_set,
        )
        hr_time = human_readable_time(get_start_times(measurement_set)[0])
        subtract_sector_models(
            measurement_set,
            ",".join(out_predict),
            nr_outliers=0,
            nr_bright=2,
            peel_outliers=False,
            peel_bright=True,
            reweight=False,
            starttime=hr_time,
            solint_sec=get_time_interval(msin[i]),
            solint_hz=get_channel_width(msin[i]),
            weights_colname="WEIGHT_SPECTRUM",
            uvcut_min=0.0,
            uvcut_max=1000000.0,
            phaseonly=True,
            infix="",
        )

        path = pathlib.PurePath(measurement_set)

        in_imaging.append(f"{work_dir}/{path.name}.sector_1")

    logger.info("Done subtract_sector_models")
    return in_imaging


def image_1(  # pylint: disable=R0913,R0914
    dp3_runner,
    wsclean_runner,
    solutions_to_apply,
    skymodel,
    vertices_filename,
    work_dir,
    input_ms_list,
    mask_filename,
):
    """Define imaging operation"""
    # ------------------------ Image_1 7:06:40

    input_imaging_ms_list = []
    for measurement_set in input_ms_list:
        logger.info(
            "Running applybeam_shift_average for measurement set %s",
            measurement_set,
        )
        msout = f"{measurement_set}.sector_1.prep"
        dp3_runner.applybeam(
            measurement_set,
            msout,
            calculate_n_times(measurement_set),
        )
        input_imaging_ms_list.append(msout)
    dp3_runner.join()

    reference_ra_deg, reference_dec_deg = get_phase_center(input_ms_list[0])

    # Create imaging mask
    logger.info("Start blank_image")
    blank_image(
        mask_filename,
        input_image=None,
        vertices_file=vertices_filename,
        reference_ra_deg=reference_ra_deg,
        reference_dec_deg=reference_dec_deg,
        cellsize_deg=wsclean_runner.settings.imaging_scale,
        imsize=f"{wsclean_runner.settings.imaging_size},\
        {wsclean_runner.settings.imaging_size}",
    )

    logger.info("Start make_region_file")
    # Observation parameters should be equal for all MS's.
    observation = get_observation_params(input_ms_list[0])
    width = compute_observation_width(observation)
    facets_file = "regions.ds9"
    make_region_file(
        skymodel,
        float(reference_ra_deg),
        float(reference_dec_deg),
        # Note: WSClean requires that all sources in the solution file
        # must have corresponding regions in the facets region file.
        # We ensure this by applying a 20% padding to the width.
        # The value of 20 % was determined experimentally. See
        # https://git.astron.nl/RD/rapthor/-/merge_requests/103#note_71941
        width["ra"] * 1.2,
        width["dec"] * 1.2,
        facets_file,
    )

    # This is the value used in Rapthor for the 1st iteration
    max_nmiter = 8
    nmiter = max_nmiter
    peel_bright_sources = False

    logger.info(
        "Calculate WSClean nmiter with a maximum value of %s", max_nmiter
    )
    nmiter = get_imaging_n_iterations(
        input_imaging_ms_list,
        max_nmiter,
        peel_bright_sources,
    )
    logger.info("Number of major iterations for imaging is %s", nmiter)

    logger.info("Start WSClean. Logging to %s", wsclean_runner.log_filename)
    tmp_dir = f"{work_dir}/tmp_imaging"
    if not os.path.exists(tmp_dir):
        os.makedirs(tmp_dir)

    concatenated_ms_filename = "concat_msout.ms"
    concatenate_ms(input_imaging_ms_list, concatenated_ms_filename)

    wsclean_runner.run(
        concatenated_ms_filename,
        facets_file,
        solutions_to_apply,
        mask_filename,
        tmp_dir,
        n_major_iterations=nmiter,
    )

    logger.info("Done WSClean")

    logger.info("Start filter_skymodel.py")
    beam_ms = ", ".join(input_imaging_ms_list)
    filter_skymodel(
        f"{work_dir}/sector_1-MFS-image.fits",
        f"{work_dir}/sector_1-sources-pb.txt",
        "sector_1",
        vertices_filename,
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
    vertices_filename,
    work_dir,
    input_ms_list,
    mask_filename,
    bright_sources_skymodel,
):
    """Define imaging operation"""

    input_imaging_ms_list = []
    for measurement_set in input_ms_list:
        logger.info(
            "Running applybeam_shift_average for measurement set %s",
            measurement_set,
        )
        msout = f"{measurement_set}.prep"
        dp3_runner.applybeam(
            measurement_set,
            msout,
            calculate_n_times(measurement_set),
        )
        input_imaging_ms_list.append(msout)
    dp3_runner.join()

    reference_ra_deg, reference_dec_deg = get_phase_center(input_ms_list[0])

    # Create imaging mask
    logger.info("Start blank_image")
    blank_image(
        mask_filename,
        input_image=None,
        vertices_file=vertices_filename,
        reference_ra_deg=reference_ra_deg,
        reference_dec_deg=reference_dec_deg,
        cellsize_deg=wsclean_runner.settings.imaging_scale,
        imsize=f"{wsclean_runner.settings.imaging_size},\
        {wsclean_runner.settings.imaging_size}",
    )

    logger.info("Start make_region_file")
    # Observation parameters should be equal for all MS's.
    observation = get_observation_params(input_ms_list[0])
    width = compute_observation_width(observation)
    facets_file = "regions.ds9"
    make_region_file(
        skymodel,
        float(reference_ra_deg),
        float(reference_dec_deg),
        # Note: WSClean requires that all sources in the solution file
        # must have corresponding regions in the facets region file.
        # We ensure this by applying a 20% padding to the width.
        # The value of 20 % was determined experimentally. See
        # https://git.astron.nl/RD/rapthor/-/merge_requests/103#note_71941
        width["ra"] * 1.2,
        width["dec"] * 1.2,
        facets_file,
    )

    # This is the value used in Rapthor for the 3rd iteration
    max_nmiter = 10
    nmiter = max_nmiter
    peel_bright_sources = False

    logger.info(
        "Calculate WSClean nmiter with a maximum value of %s", max_nmiter
    )
    nmiter = get_imaging_n_iterations(
        input_imaging_ms_list,
        max_nmiter,
        peel_bright_sources,
    )
    logger.info("Number of major iterations for imaging is %s", nmiter)

    logger.info("Start WSClean. Logging to %s", wsclean_runner.log_filename)
    tmp_dir = f"{work_dir}/tmp_imaging"
    if not os.path.exists(tmp_dir):
        os.makedirs(tmp_dir)

    concatenated_ms_filename = "concat_msout.ms"
    concatenate_ms(input_imaging_ms_list, concatenated_ms_filename)

    wsclean_runner.run(
        concatenated_ms_filename,
        facets_file,
        solutions_to_apply,
        mask_filename,
        tmp_dir,
        n_major_iterations=nmiter,
        auto_mask=4.0,
    )

    logger.info("Done WSClean")

    logger.info(
        "Start wsclean restore. Logging to %s", wsclean_runner.log_filename
    )
    wsclean_runner.restore(
        f"{work_dir}/sector_1-MFS-image",
        bright_sources_skymodel,
    )
    logger.info("Done wsclean restore")

    logger.info("Start filter_skymodel.py")

    beam_ms = ", ".join(input_imaging_ms_list)
    filter_skymodel(
        f"{work_dir}/sector_1-MFS-image.fits",
        f"{work_dir}/sector_1-sources-pb.txt",
        "sector_1",
        vertices_filename,
        beam_ms=beam_ms,
        threshisl=3.0,
        threshpix=5.0,
    )
    logger.info("Done filter_skymodel.py")
