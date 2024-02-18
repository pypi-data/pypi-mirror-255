#  SPDX-License-Identifier: BSD-3-Clause

# -*- coding: utf-8 -*-
"""
This files checks that the DP3 and WSClean binaries used are the expected
ones for the current version. It also verifies that everybeam and casacore are
using the same binaries throughout the pipeline execution.
The checks do not raise an exception (the pipeline can work also with
different versions), but add an ERROR message in the logs.
The reference to a specific commit is added to enable results reproducibility.
"""

import logging
import os
import shutil
import subprocess
from glob import glob

import casacore
import everybeam  # pylint: disable=import-error
import pkg_resources

logger = logging.getLogger("ska-sdp-wflow-low-selfcal")


def check_version(dp3_path, wsclean_path):
    """
    This function checks if there are multiple versions of the same library
    loaded, and if the current package version is compliant with the expected
    commit hashes of DP3 and WSClean
    """
    dp3_exe = shutil.which(dp3_path)
    wsclean_exe = shutil.which(wsclean_path)

    check_version_successful = True
    try:
        check_version_successful = verify_single_casacore(dp3_exe, wsclean_exe)
    except subprocess.CalledProcessError as command_exception:
        logger.error(
            "check_version:: error while checking single casacore. Error "
            "message: %s",
            command_exception,
        )

    try:
        check_version_successful = verify_single_everybeam(
            dp3_exe, wsclean_exe
        )
    except subprocess.CalledProcessError as command_exception:
        logger.error(
            "check_version:: error while checking single everybeam. Error "
            "message: %s",
            command_exception,
        )

    my_version = pkg_resources.get_distribution(
        "ska-sdp-wflow-low-selfcal"
    ).version

    if my_version == "0.1.0":
        logger.info(
            "check_version:: Version 0.1.0 of ska-sdp-wflow-low-selfcal is "
            "not based on a specific DP3 or WSClean commit"
        )
        return check_version_successful

    expected_dp3_commit, expected_wsclean_commit = get_commit_hashes(
        my_version
    )

    # The command 'DP3 -v' returns a string containing the version and the
    # commit hash. The commit hash is in the 3rd element of the output string.
    dp3_version_output = subprocess.check_output([dp3_exe, "-v"]).decode()
    if len(dp3_version_output.split()) > 2:
        installed_dp3_commit = dp3_version_output.split()[2]
    else:
        installed_dp3_commit = "DP3 commit hash not available"

    # The command 'wsclean -version' returns a string containing the version,
    # author, date, the commit hash and other info.  The commit hash is in
    # the 8th element of the output string.
    wsclean_version_output = subprocess.check_output(
        [wsclean_exe, "-version"]
    ).decode()
    if len(wsclean_version_output.split()) > 50:
        installed_wsclean_commit = wsclean_version_output.split()[7]
    else:
        installed_wsclean_commit = "WSClean commit hash not available"

    if (
        expected_dp3_commit in installed_dp3_commit
        and expected_wsclean_commit in installed_wsclean_commit
    ):
        logger.info("check_version:: Successful")
        return check_version_successful

    logger.error(
        "check_version:: Failed. Current version of "
        "ska-sdp-wflow-low-selfcal (%s) is released based on DP3 git "
        "commit %s (detected %s) and wsclean commit %s (detected %s).\n"
        "If you want to run the pipeline ignoring this error, you can run it "
        "with --ignore_version_errors True",
        my_version,
        expected_dp3_commit,
        installed_dp3_commit,
        expected_wsclean_commit,
        installed_wsclean_commit,
    )
    check_version_successful = False

    return check_version_successful


def get_commit_hashes(ska_sdp_wflow_low_selfcal_version):
    """
    This function maps the version of the package with the expected
    commits in DP3 and WSClean.
    When releasing a new version, a new line should be added for the relevant
    commits.
    """

    dp3_commit = ""
    wsclean_commit = ""

    if ska_sdp_wflow_low_selfcal_version == "0.1.1":
        dp3_commit = "6.0.1-46-g1b792f26"
        wsclean_commit = "v3.3-86-gdfb984b"

    return dp3_commit, wsclean_commit


def verify_single_everybeam(dp3_exe, wsclean_exe):
    """Verify that both Python and DP3 point to the same everybeam binary"""

    everybeam_python = everybeam.__file__
    path_to_everybeam_binary_via_python = everybeam_python[
        : everybeam_python.index("/lib")
    ]

    path_to_everybeam_binary_via_dp3 = get_path_to_dependency(
        dp3_exe, "libeverybeam.so"
    )
    path_to_everybeam_binary_via_wsclean = get_path_to_dependency(
        wsclean_exe, "libeverybeam.so"
    )

    # set everybeam data if empty
    if (
        "EVERYBEAM_DATADIR" not in os.environ
        or os.environ["EVERYBEAM_DATADIR"].empty()
    ):
        os.environ["EVERYBEAM_DATADIR"] = (
            path_to_everybeam_binary_via_dp3 + "/share/everybeam"
        )

    if (
        path_to_everybeam_binary_via_python
        == path_to_everybeam_binary_via_dp3
        == path_to_everybeam_binary_via_wsclean
    ):
        return True

    logger.error(
        "check_version:: verify_single_everybeam failed. When multiple "
        "versions of everybeam are loaded, unexpected behaviour can occur.\n"
        "Python points to  %s\nDP3 points to     %s\nWSClean points to %s.\n"
        "If you want to run the pipeline ignoring this error, you can run it "
        "with --ignore_version_errors True",
        path_to_everybeam_binary_via_python,
        path_to_everybeam_binary_via_dp3,
        path_to_everybeam_binary_via_wsclean,
    )
    return False


def verify_single_casacore(dp3_exe, wsclean_exe):
    """
    Verify that both Python, DP3 and WSClean point to the same casacore binary
    """

    casacore_python = casacore.__file__
    casacore_python_exe = glob(
        casacore_python.rstrip("/_int.py") + "/tables/_tables.cpy*so"
    )[0]

    path_to_python_casacore_binary_via_python = get_path_to_dependency(
        casacore_python_exe, "libcasa_tables.so"
    )

    path_to_python_casacore_binary_via_dp3 = get_path_to_dependency(
        dp3_exe, "libcasa_tables.so"
    )
    path_to_python_casacore_binary_via_wsclean = get_path_to_dependency(
        wsclean_exe, "libcasa_tables.so"
    )

    if (
        path_to_python_casacore_binary_via_python
        == path_to_python_casacore_binary_via_dp3
        == path_to_python_casacore_binary_via_wsclean
    ):
        return True

    logger.error(
        "check_version:: verify_single_casacore failed. When multiple "
        "versions of casacore are loaded, unexpected behaviour can occur.\n"
        "Python points to  %s\nDP3 points to     %s\nWSClean points to %s.\n"
        "If you want to run the pipeline ignoring this error, you can run it "
        "with --ignore_version_errors True",
        path_to_python_casacore_binary_via_python,
        path_to_python_casacore_binary_via_dp3,
        path_to_python_casacore_binary_via_wsclean,
    )
    return False


def get_path_to_dependency(executable, target_dependency):
    """
    This function returns the path to a specific shared library that
    is used by an executable
    """

    all_dependencies = [
        i.decode()
        for i in subprocess.check_output(["ldd", executable]).split()
    ]

    paths_to_target_dependency_lib = [
        x for x in all_dependencies if "lib/" + target_dependency in x
    ]
    paths_to_target_dependency_lib64 = [
        x for x in all_dependencies if "lib64/" + target_dependency in x
    ]
    paths_to_target_dependency_libs = [
        x for x in all_dependencies if ".libs/" + target_dependency in x
    ]

    path_to_library = ""
    if paths_to_target_dependency_lib:
        path_to_library = paths_to_target_dependency_lib[0][
            : paths_to_target_dependency_lib[0].index("/lib")
        ]
    elif paths_to_target_dependency_lib64:
        path_to_library = paths_to_target_dependency_lib64[0][
            : paths_to_target_dependency_lib64[0].index("/lib")
        ]
    elif paths_to_target_dependency_libs:
        path_to_library = paths_to_target_dependency_libs[0][
            : paths_to_target_dependency_libs[0].index(".libs/")
        ]

    return path_to_library
