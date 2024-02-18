"""
Module that holds time related functions and classes
"""

from astropy.time import Time


def human_readable_time(mod_jul_sec):
    """
    Convert the time in modified julian calendar seconds
    to human readable format.
    For instance:
    5187539500.26450 is converted to "06Apr2023/23:11:40.264"
    """

    # Convert the 'seconds' part.
    sec_a_day = 60.0 * 60.0 * 24.0
    mod_jul_day = int(mod_jul_sec) / sec_a_day
    astropy_time = Time(mod_jul_day, format="mjd")
    str_time = astropy_time.strftime("%d%b%Y/%H:%M:%S")

    # Convert the fraction of seconds, and round down to three digits.
    # Rounding down is needed since DP3 skips the first time step if
    # the start time is just above the first time step in the MS.
    fraction = int((mod_jul_sec % 1) * 1000)

    return f"{str_time}.{fraction:03d}"
