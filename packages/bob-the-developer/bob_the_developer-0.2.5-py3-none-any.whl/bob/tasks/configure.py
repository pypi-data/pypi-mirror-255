"""Module focussing on the `configure` command.

Contains the task and helpers to configure a build.
"""
import contextlib
import logging
import pathlib
import typing

from bob.api import Command
from bob.common import determine_output_folder, generate_container_command
from bob.typehints import CommandListT, EnvMapT, OptionsMapT


def depends_on() -> typing.List[Command]:
    """Generate a list of task names this task depends on.

    Returns:
        A list of commands.
    """
    return [Command.Bootstrap]


def parse_env(env: EnvMapT, options: OptionsMapT) -> EnvMapT:
    """Update the envorinment map.

    Args:
        env: a map with relevant locations in the codebase.
        options: set of options to take into account.

    Returns:
        An updated env map.
    """
    name = determine_output_folder(options)
    env["build_path"] = pathlib.Path("build") / name
    env["source_path"] = pathlib.Path(".")  # noqa: PTH201
    logging.debug("Determined output folder: %s", env["build_path"])
    return env


def parse_options(options: OptionsMapT, parsed: OptionsMapT) -> None:
    """Update the options map.

    Args:
        options: set of options passed as input.
        parsed: parsed options.
    """
    parsed["configure"] = {}

    target = parsed["build_target"].name.lower()
    addopts = []
    with contextlib.suppress(KeyError):
        config = options["targets"][target]["additional_options"]["configuration"]
        addopts += config.split(" ")

    with contextlib.suppress(KeyError):
        toolchain = options["targets"][target]["toolchain"]
        config = options["toolchains"][toolchain]["additional_options"]["configuration"]
        addopts += config.split(" ")

    parsed["configure"]["additional_options"] = addopts

    with contextlib.suppress(KeyError):
        toolchain = options["targets"][target]["toolchain"]
        toolchain_file = options["toolchains"][toolchain]["toolchain_file"]
        parsed["configure"]["toolchain_file"] = toolchain_file

    logging.debug("parse_options input: %s", options)
    logging.debug("parse_options output: %s", parsed)


def generate_commands(options: OptionsMapT, env: EnvMapT) -> CommandListT:
    """Generate a set of commands to configure the build.

    Args:
        options: set of options to take into account.
        env: a map with relevant locations in the codebase.

    Returns:
        A list of commands, each command is a list of strings which can be
        passed to `subprocess.run`.
    """
    steps = []
    steps += generate_container_command(options, env["root_path"])
    steps += _generate_build_system_command(
        options, env["build_path"], env["source_path"]
    )

    with contextlib.suppress(KeyError):
        steps += [f"-DCMAKE_TOOLCHAIN_FILE={options['configure']['toolchain_file']}"]

    with contextlib.suppress(KeyError):
        steps += options["configure"]["additional_options"]

    return [steps]


def _generate_build_system_command(
    options: OptionsMapT, output_path: pathlib.Path, source_path: pathlib.Path
) -> typing.List[str]:
    return [
        "cmake",
        "-B",
        str(output_path),
        "-S",
        str(source_path),
        f"-DCMAKE_BUILD_TYPE={options['build_config']}",
    ]
