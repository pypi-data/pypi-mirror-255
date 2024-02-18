""" This module contains commands to use WSClean """
import os
from subprocess import STDOUT, check_call


class WSCleanRunner:  # pylint: disable=R0902
    """This class contains commands to use WSClean"""

    def __init__(
        self, wsclean_exe, imaging_size, imaging_scale, imaging_taper_gaussian
    ):
        self.wsclean_exe = wsclean_exe
        self.imaging_size = imaging_size
        self.imaging_scale = imaging_scale
        self.taper_gaussian = imaging_taper_gaussian

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

        self.common_args = [
            "-no-update-model-required",
            "-save-source-list",
            "-local-rms",
            "-join-channels",
            "-apply-facet-beam",
            "-log-time",
            "-gridder",
            "wgridder",
            "-parallel-deconvolution",
            "2048",
            "-pol",
            "I",
            "-mgain",
            "0.85",
            "-multiscale-scale-bias",
            "0.8",
            "-fit-spectral-pol",
            "3",
            "-auto-threshold",
            "1.0",
            "-local-rms-window",
            "50",
            "-local-rms-method",
            "rms-with-min",
            "-facet-beam-update",
            "120",
            "-auto-mask",
            "5.0",
            "-channels-out",
            "4",
            "-deconvolution-channels",
            "4",
            "-idg-mode",
            "cpu",
            "-maxuv-l",
            "1000000.0",
            "-minuv-l",
            "0.0",
            "-multiscale",
            "-name",
            "sector_1",
            "-parallel-gridding",
            "16",
            "-mem",
            "90.0",
            "-niter",
            "6666666",
            "-nmiter",
            "6",
            "-weight",
            "briggs",
            "-0.5",
        ]

        if hasattr(self, "numthreads_wsclean_deconvolution_string"):
            self.common_args.append("-deconvolution-threads")
            self.common_args.append(
                self.numthreads_wsclean_deconvolution_string
            )

        if hasattr(self, "numthreads_wsclean_string"):
            self.common_args.append("-j")
            self.common_args.append(self.numthreads_wsclean_string)

        self.restore_args = [
            "-restore-list",
        ]

        if hasattr(self, "numthreads_wsclean_restore_string"):
            self.restore_args.append("-j")
            self.restore_args.append(self.numthreads_wsclean_restore_string)

    def run_wsclean(  # pylint: disable=R0913
        self,
        msin_list,
        facets_file,
        solutions_file,
        fits_mask,
        temp_dir,
        log_filename="wsclean_logs.txt",
    ):
        """Run WSClean"""
        with open(log_filename, "a", encoding="utf-8") as outfile:
            check_call(
                [
                    self.wsclean_exe,
                    "-facet-regions",
                    facets_file,
                    "-apply-facet-solutions",
                    solutions_file,
                    "phase000",
                    "-fits-mask",
                    fits_mask,
                    "-temp-dir",
                    temp_dir,
                    "-size",
                    self.imaging_size,
                    self.imaging_size,
                    "-scale",
                    self.imaging_scale,
                    "-taper-gaussian",
                    self.taper_gaussian,
                ]
                + self.common_args
                + msin_list,
                stderr=STDOUT,
                stdout=outfile,
            )

    def restore(
        self,
        image_name,
        bright_source_skymodel="bright_source_skymodel.txt",
        log_filename="wsclean_logs.txt",
    ):
        """Run WSClean restore operation"""
        with open(log_filename, "a", encoding="utf-8") as outfile:
            check_call(
                [
                    self.wsclean_exe,
                ]
                + self.restore_args
                + [
                    f"{image_name}.fits",
                    f"{bright_source_skymodel}",
                    f"{image_name}.fits",
                ],
                stderr=STDOUT,
                stdout=outfile,
            )

        with open(log_filename, "a", encoding="utf-8") as outfile:
            check_call(
                [
                    self.wsclean_exe,
                ]
                + self.restore_args
                + [
                    f"{image_name}-pb.fits",
                    f"{bright_source_skymodel}",
                    f"{image_name}-pb.fits",
                ],
                stderr=STDOUT,
                stdout=outfile,
            )
