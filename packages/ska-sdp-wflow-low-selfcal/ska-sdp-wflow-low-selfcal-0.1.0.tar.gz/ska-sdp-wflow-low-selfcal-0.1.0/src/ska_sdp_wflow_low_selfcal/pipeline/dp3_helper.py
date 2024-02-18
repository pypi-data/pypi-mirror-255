"""This module contains commands to use DP3"""
import os
from subprocess import STDOUT, check_call

from ska_sdp_wflow_low_selfcal.pipeline.support.read_data import get_patches


class Dp3Runner:
    """This class contains commands to use DP3"""

    def __init__(self, dp3_exe, calibration_nchannels):
        self.dp3_exe = dp3_exe
        if os.getenv("DP3_NUM_THREADS"):
            numthreads = os.getenv("DP3_NUM_THREADS")
            self.numthreads_string = "numthreads=" + str(numthreads)
        self.calibration_nchannels = calibration_nchannels

    def predict(  # pylint: disable=R0913
        self,
        msin,
        msout,
        starttime,
        directions,
        input_skymodel,
        solutions_to_apply,
        applycal_params,
        log_filename="DP3_logs.txt",
    ):
        """This workflow performs direction-dependent prediction of sector sky
        models and subracts the resulting model data from the input data,
        reweighting if desired. The resulting data are suitable for imaging."""

        with open(log_filename, "a", encoding="utf-8") as outfile:
            check_call(
                [
                    self.dp3_exe,
                    f"predict.applycal.parmdb={solutions_to_apply}",
                    f"predict.directions={directions}",
                    f"predict.sourcedb={input_skymodel}",
                    f"msout={msout}",
                    "msout.overwrite=true",
                ]
                + applycal_params
                + self.args_predict
                + self.common_args(msin, starttime),
                stderr=STDOUT,
                stdout=outfile,
            )

    def calibrate_scalarphase(  # pylint: disable=R0913
        self,
        msin,
        starttime,
        input_skymodel,
        constraint_antennas,
        output_solutions,
        log_filename="DP3_logs.txt",
    ):
        """(1)  a fast phase-only calibration (with
        core stations constrianed to have the same solutions) to correct for
        ionospheric effects, (2) a joint slow amplitude calibration (with all
        stations constrained to have the same solutions) to correct for beam
        errors"""

        with open(log_filename, "a", encoding="utf-8") as outfile:
            check_call(
                [
                    self.dp3_exe,
                    "steps=[solve]",
                    f"solve.sourcedb={input_skymodel}",
                    f"solve.h5parm={output_solutions}",
                    "msout= ",
                ]
                + self.common_args(msin, starttime)
                + self.calibrate_common_args("solve")
                + self.calibrate_predict_args("solve")
                + self.calibrate_scalarphase_args(
                    "solve", constraint_antennas
                ),
                stderr=STDOUT,
                stdout=outfile,
            )

    def calibrate_complexgain(  # pylint: disable=R0913
        self,
        msin,
        starttime,
        input_skymodel,
        solutions_to_apply,
        output_solutions,
        log_filename="DP3_logs.txt",
    ):
        """(3) a further unconstrained slow gain calibration to correct for "
        "station-to-station differences."""

        with open(log_filename, "a", encoding="utf-8") as outfile:
            check_call(
                [
                    self.dp3_exe,
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
                + self.calibrate_complexgain_args("solve"),
                stderr=STDOUT,
                stdout=outfile,
            )

    def calibrate_scalarphase_and_complexgain(  # pylint: disable=R0913
        self,
        msin,
        starttime,
        input_skymodel,
        constraint_antennas,
        output_solutions_scalarphase,
        output_solutions_complexgain,
        log_filename="DP3_logs.txt",
    ):
        """Performs both calibrate_scalarphase and calibrate_complexgain
        in a single DP3 call, reusing predicted visibilities."""

        directions_list = get_patches(input_skymodel)[0]
        reusemodels = ",".join(
            ["solve_scalarphase." + direction for direction in directions_list]
        )

        with open(log_filename, "a", encoding="utf-8") as outfile:
            check_call(
                [
                    self.dp3_exe,
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
                    "solve_scalarphase", constraint_antennas
                )
                + self.calibrate_common_args("solve_complexgain")
                + self.calibrate_complexgain_args("solve_complexgain"),
                stderr=STDOUT,
                stdout=outfile,
            )

    def applybeam_shift_average(
        self, msin, msout, starttime, log_filename="DP3_logs.txt"
    ):
        """This step uses DP3 to prepare the input data for imaging. This
        involves averaging, phase shifting, and optionally the application of
        the calibration solutions at the center."""

        with open(log_filename, "a", encoding="utf-8") as outfile:
            check_call(
                [
                    self.dp3_exe,
                    f"msout={msout}",
                    "msin.datacolumn=DATA",
                    "msout.overwrite=True",
                    "steps=[applybeam,shift,avg]",
                    "shift.type=phaseshifter",
                    "avg.type=squash",
                    "msout.storagemanager=Dysco",
                    "applybeam.direction=[258.845708333deg,57.4111944444deg]",
                    "avg.freqstep=1",
                    "shift.phasecenter=[258.845708333deg,57.4111944444deg]",
                    # AST-1269:  Make phasecenter configurable
                    "avg.timestep=1",
                ]
                + self.common_args(msin, starttime),
                stderr=STDOUT,
                stdout=outfile,
            )

    def common_args(self, msin, starttime):
        """Creates common DP3 arguments for all DP3 runs"""
        args = [
            "checkparset=1",
            f"msin={msin}",
            f"msin.starttime={starttime}",
            "msin.ntimes=75",
        ]

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

    def calibrate_scalarphase_args(self, name, constraint_antennas):
        """Creates DP3 arguments for scalar phase calibration"""
        # When constraint_antennas is True, all the antennas in the measurement
        # set are contraint to have the same solutions.
        # AST-1269: make antenna list configurable (read from MS)
        antennas = (
            "[CS001HBA0,CS002HBA0,CS003HBA0,\
CS004HBA0,CS005HBA0,CS006HBA0,CS007HBA0,CS011HBA0,CS013HBA0,\
CS017HBA0,CS021HBA0,CS024HBA0,CS026HBA0,CS028HBA0,CS030HBA0,\
CS031HBA0,CS032HBA0,CS101HBA0,CS103HBA0,CS201HBA0,CS301HBA0,\
CS302HBA0,CS401HBA0,CS501HBA0,CS001HBA1,CS002HBA1,CS003HBA1,\
CS004HBA1,CS005HBA1,CS006HBA1,CS007HBA1,CS011HBA1,CS013HBA1,\
CS017HBA1,CS021HBA1,CS024HBA1,CS026HBA1,CS028HBA1,CS030HBA1,\
CS031HBA1,CS032HBA1,CS101HBA1,CS103HBA1,CS201HBA1,CS301HBA1,\
CS302HBA1,CS401HBA1,CS501HBA1]"
            if constraint_antennas
            else ""
        )
        return [
            f"{name}.mode=scalarphase",
            f"{name}.llssolver=qr",
            f"{name}.maxiter=150",
            f"{name}.solint=1",
            f"{name}.smoothnessrefdistance=0.0",
            f"{name}.smoothnessreffrequency=143650817.87109375",  # MS specific
            # AST-1269: make smoothnessreffrequency configurable
            f"{name}.antennaconstraint=[{antennas}]",
        ]

    def calibrate_complexgain_args(self, name):
        """Creates DP3 arguments for complex gain calibration"""
        return [
            f"{name}.mode=complexgain",
            f"{name}.solint=75",
        ]

    args_predict = [
        "msout.overwrite=True",
        "msout.writefullresflag=False",
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
