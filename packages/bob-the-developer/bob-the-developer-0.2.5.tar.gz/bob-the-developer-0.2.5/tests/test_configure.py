"""Tests specifically for the configure command."""
import pathlib

from bob.api import Command
from bob.common import parse_options as common_parse_options
from bob.tasks.configure import depends_on, generate_commands, parse_env, parse_options


def test_dependency() -> None:
    """Verify commands's dependecies."""
    result = depends_on()

    assert result == [Command.Bootstrap]


def test_configure_default_options(tmp_path: pathlib.Path) -> None:
    """Verify the default options generate a valid configure command.

    Todo:
    - Actually default the options?
    """
    # 1. Prepare
    options = {}
    parsed_options = common_parse_options(options)
    parse_options(options, parsed_options)
    env = {"root_path": tmp_path}
    env = parse_env(env, parsed_options)

    # 2. Execute
    result = generate_commands(parsed_options, env)

    # 3. Verify
    assert len(result) == 1
    assert result[0] == [
        "cmake",
        "-B",
        "build/native-release",
        "-S",
        ".",
        "-DCMAKE_BUILD_TYPE=Release",
    ]


def test_configure_with_container_linux_clang(tmp_path: pathlib.Path) -> None:
    """Verify Linux build triggers the use of a Linux container."""
    # 1. Prepare
    options = {
        "config": "release",
        "target": "linux",
        "toolchains": {"linux": {"container": "renemoll/builder_clang"}},
        "targets": {"linux": {"toolchain": "linux"}},
    }
    parsed_options = common_parse_options(options)
    parse_options(options, parsed_options)
    env = {"root_path": tmp_path}
    env = parse_env(env, parsed_options)

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
        "-B",
        "build/linux-release",
        "-S",
        ".",
        "-DCMAKE_BUILD_TYPE=Release",
    ]


def test_configure_with_additional_toolchain_options(tmp_path: pathlib.Path) -> None:
    """Verify additional options are passed along."""
    # 1. Prepare
    options = {
        "config": "release",
        "target": "linux",
        "toolchains": {
            "linux": {
                "container": "renemoll/builder_clang",
                "additional_options": {"configuration": "-G Ninja"},
            }
        },
        "targets": {"linux": {"toolchain": "linux"}},
    }
    parsed_options = common_parse_options(options)
    parse_options(options, parsed_options)
    env = {"root_path": tmp_path}
    env = parse_env(env, parsed_options)

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
        "-B",
        "build/linux-release",
        "-S",
        ".",
        "-DCMAKE_BUILD_TYPE=Release",
        "-G",
        "Ninja",
    ]


def test_configure_with_additional_target_options(tmp_path: pathlib.Path) -> None:
    """Verify additional options are passed along."""
    # 1. Prepare
    options = {
        "config": "release",
        "target": "linux",
        "toolchains": {"linux": {"container": "renemoll/builder_clang"}},
        "targets": {
            "linux": {
                "toolchain": "linux",
                "additional_options": {"configuration": "-DTOGGLE"},
            }
        },
    }
    parsed_options = common_parse_options(options)
    parse_options(options, parsed_options)
    env = {"root_path": tmp_path}
    env = parse_env(env, parsed_options)

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
        "-B",
        "build/linux-release",
        "-S",
        ".",
        "-DCMAKE_BUILD_TYPE=Release",
        "-DTOGGLE",
    ]
