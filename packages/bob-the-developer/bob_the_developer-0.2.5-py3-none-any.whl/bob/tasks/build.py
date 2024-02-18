"""The build task builds the codebase."""
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
    return [Command.Configure]


def generate_commands(options: OptionsMapT, env: EnvMapT) -> CommandListT:
    """Generate a set of commands to build the codebase.

    Args:
        options: set of options to take into account.
        env: a map with relevant locations in the codebase.

    Returns:
        A list of commands, each command is a list of strings which can be
        passed to `subprocess.run`.

    Todo:
        - split target and compiler (should be a matrix [target vs compiler])
    """
    steps = []
    steps += generate_container_command(options, env["root_path"])
    steps += _generate_build_project_command(env["build_path"])

    return [steps]


def _generate_build_project_command(output_path: pathlib.Path) -> typing.List[str]:
    return ["cmake", "--build", str(output_path)]
