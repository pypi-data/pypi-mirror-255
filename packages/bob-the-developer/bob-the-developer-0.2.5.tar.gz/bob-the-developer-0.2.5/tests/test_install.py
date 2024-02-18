"""Tests specifically for the install command."""
import pathlib

from bob.api import Command
from bob.common import parse_options
from bob.tasks.install import depends_on, generate_commands


def test_dependency() -> None:
    """Verify bootstraps's dependecies."""
    result = depends_on()

    assert result == [Command.Build]


def test_install_default_options(tmp_path: pathlib.Path) -> None:
    """Verify the default options generate a valid install command."""
    # 1. Prepare
    # 1. Prepare
    options = {
        "config": "Release",
        "target": "Native",
    }
    parsed_options = parse_options(options)
    env = {"root_path": tmp_path, "build_path": "build/native-release"}

    # 2. Execute
    result = generate_commands(parsed_options, env)

    # 3. Verify
    assert len(result) == 1
    assert result[0] == ["cmake", "--install", "build/native-release"]
