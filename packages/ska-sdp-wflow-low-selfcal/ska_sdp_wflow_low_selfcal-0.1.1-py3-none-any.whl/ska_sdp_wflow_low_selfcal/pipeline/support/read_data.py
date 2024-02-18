#  SPDX-License-Identifier:  BSD-3-Clause

""" This module contains functions to read data from a measurement set
and skymodels """

import lsmtool
import numpy as np
from astropy import units
from astropy.coordinates import Angle
from casacore.tables import taql
from scipy.constants import speed_of_light


def get_phase_center(measurement_set):
    """Read phase center from given MS. Returns the ra, dec values
    in degrees"""
    phase_center = taql(f"select PHASE_DIR deg from {measurement_set}::FIELD")
    ra = (
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


def get_antennas(measurement_set):
    """Read antennas from given MS."""
    antennas = taql(f"select NAME from {measurement_set}::ANTENNA").getcol(
        "NAME"
    )
    return antennas


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


def get_observation_params(measurement_set):
    """Read observation info from given MS"""

    observation = {}
    # Calculate mean elevation
    query_elevation = f"SELECT gmean(mscal.azel()[1]) from {measurement_set}"
    observation["mean_el_rad"] = taql(query_elevation).getcol("Col_1")[0]

    # Read reference frequency
    query_ref_frequency = (
        f"select REF_FREQUENCY from {measurement_set}::SPECTRAL_WINDOW"
    )
    observation["ref_freq"] = taql(query_ref_frequency).getcol(
        "REF_FREQUENCY"
    )[0]

    # Read dish diameter
    query_antenna_diameter = (
        f"select DISH_DIAMETER from {measurement_set}::ANTENNA"
    )
    observation["diam"] = float(
        taql(query_antenna_diameter).getcol("DISH_DIAMETER")[0]
    )

    # Read telescope name
    query_telescope_name = (
        f"select TELESCOPE_NAME from {measurement_set}::OBSERVATION"
    )
    observation["telescope_name"] = taql(query_telescope_name).getcol(
        "TELESCOPE_NAME"
    )[0]

    return observation


def get_imaging_spectral_params(measurement_set):
    """Calculate WSClean parameters for imaging: channels-out,
    fit-spectral-pol, deconvolution-channels"""

    min_frequency = taql(
        f"select min(CHAN_FREQ) from {measurement_set}::SPECTRAL_WINDOW"
    ).getcol("Col_1")[0]

    # Set number of output channels to get ~ 4 MHz per channel equivalent at
    # 120 MHz (the maximum averaging allowed for typical dTEC values of
    # -0.5 < dTEC < 0.5)
    target_bandwidth = 4e6 * min_frequency / 120e6
    min_nchannels = 1
    total_bandwidth, n_channels = get_total_bandwidth(measurement_set)

    channels_out = max(
        min_nchannels,
        min(n_channels, int(np.ceil(total_bandwidth / target_bandwidth))),
    )

    # Set number of channels to use in spectral fitting. We set this to the
    # number of channels, up to a maximum of 4 (and the fit spectral order to
    # one less)
    deconvolution_channels = min(4, channels_out)
    spectral_poly_order = max(1, deconvolution_channels - 1)

    return channels_out, deconvolution_channels, spectral_poly_order


def get_total_bandwidth(measurement_set):
    """Extract the total bandwidth and number of channels from the
    measurement set"""

    n_channels = taql(
        f"select NUM_CHAN from {measurement_set}::SPECTRAL_WINDOW"
    ).getcol("NUM_CHAN")[0]

    total_bandwidth = n_channels * get_channel_width(measurement_set)

    return total_bandwidth, n_channels


def get_channel_width(measurement_set):
    """Read channel width from measurement set"""
    channel_width = taql(
        f"select CHAN_WIDTH from {measurement_set}::SPECTRAL_WINDOW"
    ).getcol("CHAN_WIDTH")[0][0]
    return channel_width


def get_time_interval(measurement_set):
    """Read time interval from MS. This function reads the first time interval,
    assuming all intervals are the same (not true for baseline dependent
    averaging)"""
    time_interval = taql(f"select INTERVAL from {measurement_set}").getcol(
        "INTERVAL"
    )[0]
    return time_interval


def get_total_time(measurement_set_list):
    """Returns the total time of the list of MS given, in hours"""
    total_time_hours = 0.0
    for measurement_set in measurement_set_list:
        start_time = taql(f"select TIME from {measurement_set}").getcol(
            "TIME"
        )[0]
        end_time = taql(f"select TIME from {measurement_set}").getcol("TIME")[
            -1
        ]
        total_time_hours += (end_time - start_time) / 3600.0

    return total_time_hours


def get_imaging_n_iterations(
    measurement_set_list,
    max_nmiter,
    peel_bright_sources,
):
    """Calculate the number of major iterations needed in WSClean.
    This calculation is done based on the integration time and the distance
    of the sector vertices to the phase center. The number of iterations is
    also reduced if bright sources are peeled"""

    # Find total observation time in hours
    total_time_hr = get_total_time(measurement_set_list)

    total_bandwidth, _ = get_total_bandwidth(measurement_set_list[0])
    scaling_factor = np.sqrt(
        float(total_bandwidth / 2e6) * total_time_hr / 16.0
    )

    wsclean_nmiter = min(max_nmiter, max(2, int(round(8 * scaling_factor))))

    if peel_bright_sources:
        # If bright sources are peeled, reduce nmiter by 25% (since they
        # no longer
        # need to be cleaned)
        wsclean_nmiter = max(2, int(round(wsclean_nmiter * 0.75)))

    return wsclean_nmiter


def calculate_n_chunks(measurement_set, data_fraction=1.0, mintime=600.0):
    """
    Calculate the max number of chunks a measurement set can be split into,
    where each (fraction of) chunk should be at least mintime seconds .

    Parameters:
    - measurement_set (str): Path to the measurement set file.
    - data_fraction (float): Fraction of the total data to be processed.
    Default is 1.0 (all data is processed)
    - mintime (float): Minimum time duration for each chunk, in seconds.
    Default is 600.0.

    Returns:
    - n_chunks (int): Number of chunks required to process the measurement set.
    """
    # Read the total time of the measurement set, in seconds.
    total_time = get_total_time([measurement_set]) * 3600.0

    # The minimum time cannot be smaller than the time interval of the ms.
    mintime = max(mintime, get_time_interval(measurement_set))
    minimum_data_fraction = min(1.0, mintime / float(total_time))
    data_fraction = max(data_fraction, minimum_data_fraction)

    # Add a small number to avoid rounding errors
    n_chunks = max(
        1, int(np.floor(data_fraction * total_time / mintime + 0.00001))
    )
    return n_chunks


def calculate_n_times(measurement_set, interval=600.0):
    """
    Calculates the number of time slots which cover a specified interval.

    Parameters:
    - measurement_set (str): The name of the measurement set.
    - interval (float): The time interval in seconds. Default is 600.0
    (default value from Rapthor, which allows enough data for calibration)

    Returns:
    - n_intervals_per_chunk (int): The number of intervals per chunk.
    """

    n_intervals_per_chunk = int(
        np.ceil(interval / get_time_interval(measurement_set))
    )

    return n_intervals_per_chunk


def get_start_times(ms_path, n_intervals=1):
    """
    Reads the values from the column TIME of main table of
    a measurement set, split the values in n_intervals
    and returns a list with the first time of each interval.
    """

    # Verify that number_of_intervals is an equal or
    # larger than one.
    if n_intervals < 1:
        raise RuntimeError(
            "number_of_intervals must be a positive "
            "integer equal or larger than 1, but it "
            "is:" + str(n_intervals)
        )

    # Read the unique values of column TIME.
    times = taql(f"SELECT UNIQUE(TIME) FROM {ms_path}").getcol("TIME")

    mod_jul_sec_list = []
    for i in range(n_intervals):
        index = int((i * len(times)) / n_intervals)
        mod_jul_sec_list.append(times[index])

    return mod_jul_sec_list


def compute_observation_width(observation):
    """
    Computes the width of an observation, using its
    reference frequency, data and elevation values.

    Returns: A dictionary containing "ra" and "dec" values, in degrees.
    """

    # Compute Full Width at Half Maximum (FWHM) value.
    fwhm_degrees = np.rad2deg(
        1.1 * speed_of_light / observation["ref_freq"] / observation["diam"]
    )

    # Derive observation widths from the FWHM.
    # 1.7 is an instrument-specific multiplier for the FWHM.
    # 1.7 is the value applicable to LOFAR.
    return {
        "ra": 1.7 * fwhm_degrees,
        "dec": 1.7 * fwhm_degrees / np.sin(observation["mean_el_rad"]),
    }
