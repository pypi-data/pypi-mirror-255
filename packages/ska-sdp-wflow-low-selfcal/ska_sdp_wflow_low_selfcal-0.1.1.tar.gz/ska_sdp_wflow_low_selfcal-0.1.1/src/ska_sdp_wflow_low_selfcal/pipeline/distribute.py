#  SPDX-License-Identifier: BSD-3-Clause

"""
This module provides the following;
- start_dask and stop_dask functions for starting and stopping the Dask
  scheduler and workers using dask-mpi.
- A Distributor class, which wraps existing classes to create a version
  whose methods can be executed asynchronously through Dask.
  See the documentation of Distributor class for futher details.
"""


import atexit
import json
import os
import subprocess
import sys
import time

import dask
import dask.distributed

this = sys.modules[__name__]
this.dask_client = None
this.dask_mpi = None
this.scheduler_file_name = None


def _stop_dask(logger):
    """
    Stop external DASK programs. This function is very fault tolerant, since it
    is intended to be run at python program exit.
    """
    # Check if dask is running
    if not this.dask_mpi:
        return

    # Try shutting down dask-mpi gracefully via _dask_client.
    if this.dask_client:
        this.dask_client.shutdown()

        # Give the mpi processes some time to shut down.
        timeout = time.time() + 15
        while not this.dask_mpi.poll() and time.time() < timeout:
            time.sleep(1)

    # If the main process is still there, kill it.
    if this.dask_mpi and not this.dask_mpi.poll():
        logger.warning("dask-mpi did not shutdown. Terminating manually...")
        this.dask_mpi.terminate()
        this.dask_mpi.kill()

    if this.scheduler_file_name:
        try:
            os.remove(this.scheduler_file_name)
        except FileNotFoundError:
            pass

    this.dask_client = None
    this.dask_mpi = None
    this.scheduler_file_name = None


def stop_dask(logger):
    """Stop the dask scheduler and workers started via start_dask"""
    atexit.unregister(_stop_dask)
    _stop_dask(logger)


def start_dask(logger, logging_tag=os.getpid()):
    """
    Start Dask scheduler and workers in the background.
    Do nothing if this function was called before, and the scheduler and
    workers already run.
    Automatically stop the background processes at program exit.
    Use 'logger' for (short) messages related to starting and stopping the
    dask processes. The output from the dask processes itself goes into a file
    named 'dask.<pid>.log', and is thus not sent to 'logger'.
    """

    if (
        this.dask_client
        and this.dask_client.scheduler
        and this.dask_client.scheduler.address
    ):
        return

    atexit.register(_stop_dask, logger)

    # Ensure that other mpirun calls (e.g., for wsclean) can run together
    # with the dask workers (that are idle then).
    os.environ["SLURM_OVERLAP"] = "yes"

    dask_log_file_name = f"dask.{logging_tag}.log"
    this.scheduler_file_name = f"scheduler.{logging_tag}.json"

    logger.info(f"Starting dask-mpi. Dask logs are in {dask_log_file_name}.")

    # pylint: disable=R1732
    dask_log = open(dask_log_file_name, mode="w", encoding="utf8")

    # Since DP3 processes launched via Dask can use multiple threads:
    # - Use "--bind-to none" with mpirun, otherwise mpirun may use a single
    #   core per process.
    # - Use "--nthreads 1" for the dask workers.
    this.dask_mpi = subprocess.Popen(
        [
            "mpirun",
            "--bind-to",
            "none",
            "dask-mpi",
            "--scheduler-file",
            this.scheduler_file_name,
            "--worker-class",
            "distributed.Worker",
            "--nthreads",
            "1",
        ],
        stdout=dask_log,
        stderr=dask_log,
    )

    timeout = time.time() + 15
    while not this.dask_client:
        if this.dask_mpi.poll():
            raise RuntimeError(
                "dask-mpi unexpectedly stopped with return code "
                f"{this.dask_mpi.returncode}"
            )
        if time.time() > timeout:
            raise RuntimeError("Timeout while starting dask-mpi")
        try:
            with open(
                this.scheduler_file_name, encoding="utf8"
            ) as scheduler_file:
                parsed = json.load(scheduler_file)
                this.dask_client = dask.distributed.Client(parsed["address"])
                this.dask_client.forward_logging()
        # Ignore errors, try again next time
        except (OSError, json.JSONDecodeError):
            pass
        time.sleep(1)

    if not this.dask_client.get_versions()["workers"]:
        raise RuntimeError(
            "No dask workers found. 'mpirun dask-mpi' only started the "
            "dask scheduler. This situation can happen when there is only one "
            "SLURM task."
        )

    logger.info("Dask client: " + str(this.dask_client))


class Distributor:  # pylint: disable=R0903
    """
    Wrapper class factory to create distributed versions of runner classes.
    It executes its methods asynchronously through dask.delayed.
    The return value is then a dask Delayed object.
    To wait for the asynchronous calls to finish call `runner.join()`.
    This returns a tuple of the actual results.
    To indicate a dependence between calls, pass (a tuple of) the delayed
    result(s) as the `depends_on` keyword arguments.

    Usage example:
        runner = Distributor(Runner)(runner_arg1, runner_arg2)

        result1 = runner.method1()
        result2 = runner.method2(method2_arg1, method2_arg2)
        runner.method3(method3_arg1,
            depends_on=(result1, result2))
        runner.join()

        runner.method1()
        runner.join()
    """

    @staticmethod
    def __new__(distributor_cls, runner_cls, run_distributed=True):
        """
        Returns a wrapper class around the class `runner_cls`

        If `run_distributed == False` then this is only a wrapper that
        presents a the interface of a distributed runner, but executes
        synchronously.

        If `run_distributed == True` the calls to the methods are actually
        executed asynchrously through dask.delayed.
        """

        def wrap_method(method_name):
            """
            Function to create a wrapper for the method from the runner_cls
            with the name `method_name`.
            """

            # Extract the method from the runner_cls
            method = getattr(runner_cls, method_name)

            def method_stripped(
                *args, depends_on=(), **kwargs
            ):  # pylint: disable=W0613
                """
                Thin wrapper that strips the `depends_on` argument from the
                keyword arguments and then passes the argument and keyword
                arguments to `method`.
                """
                return method(*args, **kwargs)

            def wrapper(self, *args, **kwargs):
                """
                Wrapper function that either executes the method synchronously
                or asynchronously through dask.delayed.
                """
                if run_distributed:
                    lazy_result = dask.delayed(method_stripped)(
                        self.runner, *args, **kwargs
                    )
                    self.lazy_results.append(lazy_result)
                    return lazy_result
                return method_stripped(self.runner, *args, **kwargs)

            return wrapper

        class WrappedClass:
            """
            Wrapper class for a runner

            """

            def __init__(self, *args, **kwargs):
                """
                Constructor passes all arguments to the constructor of the
                wrapped class.
                """
                self.runner = runner_cls(*args, **kwargs)
                self.lazy_results = []

            def join(self):
                """
                Evaluate all previous method calls, wait for the results and
                return them. If run_distributed is False, this method doesn't
                do anything.
                """
                if run_distributed:
                    results = dask.compute(*self.lazy_results)
                    self.lazy_results = []
                    return results
                return None

        # Iterate over all (public) methods in runner_cls and replace them by a
        # wrapped version
        for method_name in dir(runner_cls):
            if method_name.startswith("_"):
                continue
            setattr(WrappedClass, method_name, wrap_method(method_name))

        return WrappedClass
