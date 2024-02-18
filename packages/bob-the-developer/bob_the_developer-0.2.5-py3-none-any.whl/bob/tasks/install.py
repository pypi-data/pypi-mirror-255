"""Module focussing on the `install` command.

Contains the task and helpers to install a project.
"""
import pathlib
import typing

from bob.api import Command
from bob.common import generate_container_command
from bob.typehints import CommandListT, EnvMapT, OptionsMapT


def depends_on() -> typing.List[Command]:
    """Generate a list of task names this task depends on.

    Returns:
        A list of commands.
    """
    return [Command.Build]


def generate_commands(options: OptionsMapT, env: EnvMapT) -> CommandListT:
    """Generate a set of commands to install the project.

    Args:
        options: set of options to take into account.
        env: a map with relevant locations in the codebase.

    Returns:
        A list of commands, each command is a list of strings which can be
        passed to `subprocess.run`.
    """
    steps = []
    steps += generate_container_command(options, env["root_path"])
    steps += _generare_install_command(env["build_path"])

    return [steps]


def _generare_install_command(output_path: pathlib.Path) -> typing.List[str]:
    return [
        "cmake",
        "--install",
        str(output_path),
        # "--prefix",
        # f"/work/install",
    ]
