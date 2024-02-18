#  SPDX-License-Identifier: BSD-3-Clause

""" This module contains commands to use WSClean """
import os
import shutil
from subprocess import STDOUT, check_call

import h5py

from ska_sdp_wflow_low_selfcal.pipeline.support.read_data import (
    get_imaging_spectral_params,
)


def get_wsclean_commands(settings, run_distributed):
    """
    Determines the command(s) for running wsclean
    Returns a list of strings that should be used for running wsclean,
    which can be used as the first item in check_call, for example.
    Throws FileNotFoundError if an executable cannot be found.
    """
    wsclean_exe = settings.wsclean_path
    if run_distributed:
        wsclean_exe += "-mp"
        if not shutil.which("mpirun"):
            raise FileNotFoundError(
                "mpirun not found, which is needed for distributed "
                "wsclean runs"
            )
        if not shutil.which(wsclean_exe):
            raise FileNotFoundError(
                f"WSClean MPI executable '{wsclean_exe}' not found"
            )
        # Do not bind wsclean-mp processes to specific cores, otherwise
        # non-MPI parts that use multithreading cannot use all cores.
        commands = ["mpirun", "--bind-to", "none", wsclean_exe]
    else:
        if not shutil.which(wsclean_exe):
            raise FileNotFoundError(
                f"WSClean executable '{wsclean_exe}' not found"
            )
        commands = [wsclean_exe]
    return commands


class WSCleanRunner:  # pylint: disable=R0902
    """This class contains commands to use WSClean"""

    def __init__(
        self,
        settings,
        run_distributed=False,
    ):
        """
        Constructor.
        The 'settings' argument holds the parsed workflow arguments.
        """
        self.settings = settings
        self.wsclean_exe = get_wsclean_commands(settings, run_distributed)
        self.log_filename = f"wsclean.{settings.logging_tag}.log"

        if os.getenv("WSCLEAN_NUM_THREADS"):
            numthreads_wsclean = os.getenv("WSCLEAN_NUM_THREADS")
            self.numthreads_wsclean_string = str(numthreads_wsclean)

        if os.getenv("WSCLEAN_DECONVOLUTION_NUM_THREADS"):
            numthreads_wsclean_deconvolution = os.getenv(
                "WSCLEAN_DECONVOLUTION_NUM_THREADS"
            )
            self.numthreads_wsclean_deconvolution_string = str(
                numthreads_wsclean_deconvolution
            )

        if os.getenv("WSCLEAN_RESTORE_NUM_THREADS"):
            numthreads_wsclean_restore = os.getenv(
                "WSCLEAN_RESTORE_NUM_THREADS"
            )
            self.numthreads_wsclean_restore_string = str(
                numthreads_wsclean_restore
            )

        (
            self.channels_out,
            self.deconvolution_channels,
            self.spectral_poly_order,
        ) = get_imaging_spectral_params(settings.input_ms)

        self.common_args = [
            "-no-update-model-required",
            "-save-source-list",
            "-local-rms",
            "-join-channels",
            "-apply-facet-beam",
            "-log-time",
            "-gridder",
            "wgridder",
            # The value of 2048 is Rapthor default value. We can change this
            # to achieve optimized thread parallelisation during deconvolution
            "-parallel-deconvolution",
            "2048",
            "-pol",
            "I",
            "-mgain",
            "0.85",
            "-multiscale-scale-bias",
            "0.8",
            "-auto-threshold",
            "1.0",
            "-local-rms-window",
            "50",
            "-local-rms-method",
            "rms-with-min",
            "-facet-beam-update",
            "120",
            # These values of min/maxuv-l are filtering baselines longer
            # than 2000km
            "-maxuv-l",
            "1000000.0",
            "-minuv-l",
            "0.0",
            "-multiscale",
            "-name",
            "sector_1",
            "-mem",
            "90.0",
            # Set niter to high value and just use nmiter to limit clean
            "-niter",
            "6666666",
            "-weight",
            "briggs",
            # The value for briggs should be in the range [-2;2], where lower
            # value ensure higher resolutions (keeping longer baselines),
            # and higher values give a higher SNR. The value of -0.5 is a
            # good compromise and it s the default used in Rapthor for LOFAR.
            # It can be changed for SKA if needed.
            "-0.5",
            "-channels-out",
            f"{self.channels_out}",
            "-deconvolution-channels",
            f"{self.deconvolution_channels}",
            "-fit-spectral-pol",
            f"{self.spectral_poly_order}",
        ]
        if not run_distributed and hasattr(settings, "parallel_gridding"):
            self.common_args.append("-parallel-gridding")
            self.common_args.append(settings.parallel_gridding)

        if hasattr(self, "numthreads_wsclean_deconvolution_string"):
            self.common_args.append("-deconvolution-threads")
            self.common_args.append(
                self.numthreads_wsclean_deconvolution_string
            )

        if hasattr(self, "numthreads_wsclean_string"):
            self.common_args.append("-j")
            self.common_args.append(self.numthreads_wsclean_string)

        self.restore_args = []

        if hasattr(self, "numthreads_wsclean_restore_string"):
            self.restore_args.append("-j")
            self.restore_args.append(self.numthreads_wsclean_restore_string)

    def run_wsclean(self, arguments):
        """
        Runs WSClean with the given arguments.
        Writes the WSClean command and its output to the log file.
        """
        command = self.wsclean_exe + arguments
        with open(self.log_filename, "a", encoding="utf-8") as outfile:
            outfile.write(f"Running: {' '.join(command)}\n")
        # Closing 'outfile' before starting WSClean ensures that the command is
        # always above the WSClean output.

        with open(self.log_filename, "a", encoding="utf-8") as outfile:
            check_call(command, stderr=STDOUT, stdout=outfile)

    def run(  # pylint: disable=R0913
        self,
        msin,
        facets_file,
        solutions_file,
        fits_mask,
        temp_dir,
        n_major_iterations=6,
        auto_mask=5.0,
    ):
        """Run WSClean"""

        # The calibration solutions always contain the 'phase000' field.
        # Check if 'amplitude000' is also present
        solution_fields = "phase000"
        with h5py.File(solutions_file, "r") as h5_solutions:
            if "amplitude000" in list(
                h5_solutions[list(h5_solutions.keys())[0]].keys()
            ):
                solution_fields = "amplitude000,phase000"

        self.run_wsclean(
            [
                "-facet-regions",
                facets_file,
                "-apply-facet-solutions",
                solutions_file,
                f"{solution_fields}",
                "-fits-mask",
                fits_mask,
                "-temp-dir",
                temp_dir,
                "-size",
                self.settings.imaging_size,
                self.settings.imaging_size,
                "-scale",
                self.settings.imaging_scale,
                "-taper-gaussian",
                self.settings.imaging_taper_gaussian,
                "-nmiter",
                f"{n_major_iterations}",
                "-auto-mask",
                f"{auto_mask}",
            ]
            + self.common_args
            + [msin],
        )

    def restore(
        self,
        image_name,
        bright_source_skymodel="bright_source_skymodel.txt",
    ):
        """Run WSClean restore operation"""
        self.run_wsclean(
            self.restore_args
            + [
                "-restore-list",
                f"{image_name}.fits",
                bright_source_skymodel,
                f"{image_name}.fits",
            ],
        )

        self.run_wsclean(
            self.restore_args
            + [
                "-restore-list",
                f"{image_name}-pb.fits",
                bright_source_skymodel,
                f"{image_name}-pb.fits",
            ],
        )
