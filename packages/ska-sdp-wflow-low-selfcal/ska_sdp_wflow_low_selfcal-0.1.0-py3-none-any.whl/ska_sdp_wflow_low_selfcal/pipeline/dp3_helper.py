#  SPDX-License-Identifier: BSD-3-Clause

"""This module contains commands to use DP3"""
import logging
import os
from subprocess import STDOUT, check_call

from ska_sdp_wflow_low_selfcal.pipeline.support.read_data import (
    calculate_num_intervals,
    get_antennas,
    get_observation_params,
    get_patches,
)

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


class Dp3Runner:
    """This class contains commands to use DP3"""

    def __init__(self, args):
        self.dp3_exe = args.dp3_path
        if os.getenv("DP3_NUM_THREADS"):
            numthreads = os.getenv("DP3_NUM_THREADS")
            self.numthreads_string = "numthreads=" + str(numthreads)
        self.calibration_nchannels = args.calibration_nchannels
        self.log_filename = f"DP3.{args.logging_tag}.log"

        # Calculate number of samples per DP3 run
        self.n_chunks, self.n_times = calculate_num_intervals(
            args.input_ms, 0.2
        )

        self.environment = None
        if args.dp3_environment:
            # There are extra environmental variables provided. Make sure that
            # check_call() is provided with all other env. vars it needs too.
            self.environment = os.environ.copy()
            self.environment.update(args.dp3_environment)

    def run_dp3(self, arguments):
        """
        Runs DP3 with the given arguments.
        Writes the DP3 command and its output to the log file.
        """
        command = [self.dp3_exe] + arguments
        with open(self.log_filename, "a", encoding="utf-8") as outfile:
            outfile.write(f"Running: {' '.join(command)}\n")
        # Closing 'outfile' before starting DP3 ensures that the command is
        # always printed above the DP3 output.

        with open(self.log_filename, "a", encoding="utf-8") as outfile:
            check_call(
                command,
                stderr=STDOUT,
                stdout=outfile,
                env=self.environment,
            )

    def get_n_chunks(self):
        """
        Returns the number of chunks.
        """
        return self.n_chunks

    def predict(  # pylint: disable=R0913
        self,
        msin,
        msout,
        starttime,
        directions,
        input_skymodel,
        solutions_to_apply,
        applycal_params,
    ):
        """This workflow performs direction-dependent prediction of sector sky
        models and subtracts the resulting model data from the input data,
        reweighting if desired. The resulting data are suitable for imaging."""

        self.run_dp3(
            [
                f"predict.applycal.parmdb={solutions_to_apply}",
                f"predict.directions={directions}",
                f"predict.sourcedb={input_skymodel}",
                f"msout={msout}",
                "msout.overwrite=true",
            ]
            + applycal_params
            + self.args_predict
            + self.common_args(msin, starttime)
        )

    def calibrate_scalarphase(  # pylint: disable=R0913
        self,
        msin,
        starttime,
        input_skymodel,
        constrain_antennas,
        output_solutions,
    ):
        """(1)  a fast phase-only calibration (with
        core stations constrained to have the same solutions) to correct for
        ionospheric effects, (2) a joint slow amplitude calibration (with all
        stations constrained to have the same solutions) to correct for beam
        errors"""

        if constrain_antennas:
            antenna_constraint = self.get_default_antenna_constraint(msin)
        else:
            antenna_constraint = ""

        observation_params = get_observation_params(msin)

        self.run_dp3(
            [
                "steps=[solve]",
                f"solve.sourcedb={input_skymodel}",
                f"solve.h5parm={output_solutions}",
                "msout= ",
            ]
            + self.common_args(msin, starttime)
            + self.calibrate_common_args("solve")
            + self.calibrate_predict_args("solve")
            + self.calibrate_scalarphase_args(
                "solve", antenna_constraint, observation_params["ref_freq"]
            )
        )

    def calibrate_complexgain(  # pylint: disable=R0913
        self,
        msin,
        starttime,
        input_skymodel,
        solutions_to_apply,
        output_solutions,
    ):
        """(3) a further unconstrained slow gain calibration to correct for "
        "station-to-station differences."""

        self.run_dp3(
            [
                "steps=[solve]",
                f"solve.applycal.parmdb={solutions_to_apply}",
                "solve.applycal.steps=[fastphase]",
                "solve.applycal.fastphase.correction=phase000",
                f"solve.h5parm={output_solutions}",
                f"solve.sourcedb={input_skymodel}",
                "msout= ",
            ]
            + self.common_args(msin, starttime)
            + self.calibrate_common_args("solve")
            + self.calibrate_predict_args("solve")
            + self.calibrate_complexgain_args("solve")
        )

    def calibrate_scalarphase_and_complexgain(  # pylint: disable=R0913
        self,
        msin,
        starttime,
        input_skymodel,
        constrain_antennas,
        output_solutions_scalarphase,
        output_solutions_complexgain,
    ):
        """Performs both calibrate_scalarphase and calibrate_complexgain
        in a single DP3 call, reusing predicted visibilities."""

        directions_list = get_patches(input_skymodel)[0]
        reusemodels = ",".join(
            ["solve_scalarphase." + direction for direction in directions_list]
        )

        if constrain_antennas:
            antenna_constraint = self.get_default_antenna_constraint(msin)
        else:
            antenna_constraint = ""
        observation_params = get_observation_params(msin)

        self.run_dp3(
            [
                "steps=[solve_scalarphase,solve_complexgain]",
                f"solve_scalarphase.sourcedb={input_skymodel}",
                "solve_scalarphase.keepmodel=true",
                f"solve_scalarphase.h5parm={output_solutions_scalarphase}",
                f"solve_complexgain.reusemodel=[{reusemodels}]",
                f"solve_complexgain.h5parm={output_solutions_complexgain}",
                "msout= ",
            ]
            + self.common_args(msin, starttime)
            + self.calibrate_common_args("solve_scalarphase")
            + self.calibrate_predict_args("solve_scalarphase")
            + self.calibrate_scalarphase_args(
                "solve_scalarphase",
                antenna_constraint,
                observation_params["ref_freq"],
            )
            + self.calibrate_common_args("solve_complexgain")
            + self.calibrate_complexgain_args("solve_complexgain")
        )

    def applybeam(self, msin, msout):
        """This step uses DP3 to prepare the input data for imaging."""

        self.run_dp3(
            [
                f"msout={msout}",
                "msin.datacolumn=DATA",
                "msout.overwrite=True",
                "steps=[applybeam]",
                "msout.storagemanager=Dysco",
            ]
            + self.common_args(msin)
        )

    def common_args(self, msin, starttime=None):
        """Creates common DP3 arguments for all DP3 runs"""
        args = [
            "checkparset=1",
            f"msin={msin}",
            f"msin.ntimes={self.n_times}",
        ]
        if starttime:
            args.append(f"msin.starttime={starttime}")
        if hasattr(self, "numthreads_string"):
            args.append(self.numthreads_string)
        return args

    def calibrate_common_args(self, name):
        """Creates common DP3 arguments for calibration(DDECal)"""
        return [
            f"{name}.type=ddecal",
            f"{name}.llssolver=qr",
            f"{name}.maxiter=150",
            f"{name}.nchan={self.calibration_nchannels}",
            f"{name}.propagatesolutions=True",
            f"{name}.smoothnessconstraint=3000000.0",
            f"{name}.solveralgorithm=hybrid",
            f"{name}.stepsize=0.02",
            f"{name}.tolerance=0.005",
            f"{name}.uvlambdamin=2000.0",
        ]

    def calibrate_predict_args(self, name):
        """Creates DP3 arguments for prediction"""
        return [
            f"{name}.beammode=array_factor",
            f"{name}.onebeamperpatch=False",
            f"{name}.parallelbaselines=False",
            f"{name}.usebeammodel=True",
        ]

    def calibrate_scalarphase_args(
        self, name, antenna_constraint, reference_frequency
    ):
        """Creates DP3 arguments for scalar phase calibration"""

        return [
            f"{name}.mode=scalarphase",
            f"{name}.llssolver=qr",
            f"{name}.maxiter=150",
            f"{name}.solint=1",
            f"{name}.smoothnessrefdistance=0.0",
            f"{name}.smoothnessreffrequency={reference_frequency}",
            f"{name}.antennaconstraint={antenna_constraint}",
        ]

    def calibrate_complexgain_args(self, name):
        """Creates DP3 arguments for complex gain calibration"""
        return [
            f"{name}.mode=complexgain",
            f"{name}.solint=75",
        ]

    args_predict = [
        "msout.overwrite=True",
        "steps=[predict]",
        "predict.type=h5parmpredict",
        "predict.operation=replace",
        "predict.applycal.correction=phase000",
        "predict.usebeammodel=True",
        "predict.beammode=array_factor",
        "msout.storagemanager=Dysco",
        "msout.storagemanager.databitrate=0",
        "predict.onebeamperpatch=False",
    ]

    @staticmethod
    def get_default_antenna_constraint(measurement_set):
        """Get the default antenna_constraint for the measurement_set.
        This function is only implemented for the LOFAR telescope,
        in which case it selects the core stations."""
        observation_parms = get_observation_params(measurement_set)
        if observation_parms["telescope_name"] == "LOFAR":
            core_stations = [
                ant
                for ant in get_antennas(measurement_set)
                if ant.startswith("CS")
            ]
            return f"[{core_stations}]"
        return "[]"
