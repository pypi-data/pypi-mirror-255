"""Contains the entry point for the application.

The function `bob` is called by the CLI script and is the function to call
when integrating bob into custom scripting.
"""
import contextlib
import logging
import pathlib
import subprocess
import time
import types
import typing

from bob.api import Command
from bob.common import parse_options
from bob.modules import get_task
from bob.typehints import OptionsMapT


class ExecutionTimer(contextlib.AbstractContextManager):
    """High resolution timer to capture the execution time of a block.

    Attributes:
        duration (float): elapsed time in seconds.
        duration_ns (int): elapsed time in whole nanoseconds.
        duration_ms (float): elapsed time in miliseconds.
    """

    def __init__(self: "ExecutionTimer") -> None:
        """Initialize ExecutionTimer."""
        self._start = 0
        self.duration = 0.0
        self.duration_ms = 0.0
        self.duration_ns = 0

    def __enter__(self: "ExecutionTimer") -> "ExecutionTimer":
        """Start the timed context by recording the current time.

        Returns:
            The timed context.
        """
        self._start = time.perf_counter_ns()
        return self

    def __exit__(
        self: "ExecutionTimer",
        exc_type: typing.Optional[typing.Type[BaseException]],
        exc_value: typing.Optional[BaseException],
        exc_traceback: typing.Optional[types.TracebackType],
    ) -> typing.Literal[False]:
        """Stop the timed context and calculate the elapsed time.

        Args:
            exc_type: optional exception type
            exc_value: optional exception value
            exc_traceback: optional exception traceback

        Returns:
            False, any captured exception will be propagated.
        """
        stop = time.perf_counter_ns()
        self.duration_ns = stop - self._start
        self.duration_ms = self.duration_ns * 1e-6
        self.duration = self.duration_ns * 1e-9
        return False


def bob(command: Command, input_options: OptionsMapT) -> None:
    """Executes a `bob` command.

    Args:
        command: a command to execute
        input_options: a map of options to pass to the command

    Todo:
        - split options into given and parsed dicts.
        - in case of an error, signal the CLI to match a return code?
    """
    logging.info("Execting command: %s", command)
    logging.debug("Given options: %s", input_options)

    cwd = pathlib.Path.cwd()
    logging.debug("Working directory: %s", cwd)

    tasks = _determine_dependent_tasks(command)
    logging.debug("Processing %d tasks: %s", len(tasks), tasks)

    env = {
        "root_path": cwd,
    }
    options = parse_options(input_options)
    for task in tasks:
        module = get_task(task)

        with contextlib.suppress(AttributeError):
            env = module.parse_env(env, options)

        try:
            module.parse_options(input_options, options)
        except AttributeError:
            pass
        except ValueError:
            logging.exception("Error processing options")

        try:
            cmd_list = module.generate_commands(options, env)
        except ValueError:
            logging.exception("Valued to generate commansd for the current task")
            break

        for cmd in cmd_list:
            logging.debug(" ".join(cmd))
            with ExecutionTimer() as timer:
                result = subprocess.run(cmd, check=True)
            logging.debug(
                "Result code: `%d` in %f seconds", result.returncode, timer.duration
            )


def _determine_dependent_tasks(command: Command) -> typing.List[Command]:
    def scan_deps(deps: typing.List[Command]) -> typing.List[Command]:
        result = []
        for n in deps:
            result.append(n)
            t = get_task(n)
            result += scan_deps(t.depends_on())
        return result

    result = scan_deps([command])
    result.reverse()
    return result
