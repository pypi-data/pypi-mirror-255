"""Tests specifically for the build command."""
import pathlib

from bob.api import Command
from bob.common import parse_options
from bob.tasks.build import depends_on, generate_commands


def test_dependency() -> None:
    """Verify build's dependecies."""
    result = depends_on()

    assert result == [Command.Configure]


def test_build_default_options(tmp_path: pathlib.Path) -> None:
    """Verify the default options generate a valid build command.

    Todo:
    - Actually default the options?
    """
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
    assert result[0] == ["cmake", "--build", "build/native-release"]


def test_build_with_container_linux_clang(tmp_path: pathlib.Path) -> None:
    """Verify Linux build triggers the use of a Linux container."""
    # 1. Prepare
    options = {
        "config": "release",
        "target": "linux",
        "toolchains": {"linux": {"container": "renemoll/builder_clang"}},
        "targets": {"linux": {"toolchain": "linux"}},
    }
    parsed_options = parse_options(options)
    env = {"root_path": tmp_path, "build_path": "build/linux-release"}

    # 2. Execute
    result = generate_commands(parsed_options, env)

    # 3. Verify
    assert len(result) == 1
    assert result[0] == [
        "docker",
        "run",
        "--rm",
        "-v",
        f"{env['root_path']}:/work/",
        "renemoll/builder_clang",
        "cmake",
        "--build",
        "build/linux-release",
    ]
