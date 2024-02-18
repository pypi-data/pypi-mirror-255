"""Test the CLI entry point."""
import os
import pathlib
import shutil
import subprocess
import typing
import unittest

import docopt
import pytest
import pytest_mock

from bob.cli import main


@pytest.fixture()
def no_config_path(tmp_path_factory: pytest.TempPathFactory) -> pathlib.Path:
    """Fixture for a working folder without a configuration file."""
    work = tmp_path_factory.mktemp("work")
    os.chdir(str(work))

    return work


@pytest.fixture()
def valid_config_path(tmp_path_factory: pytest.TempPathFactory) -> pathlib.Path:
    """Fixture for a working folder with a valid configuration file."""
    work = tmp_path_factory.mktemp("work")
    os.chdir(str(work))

    toml_file = pathlib.Path(__file__).parent.resolve() / "config" / "bob.toml"
    shutil.copy(toml_file, work / "bob.toml")

    return work


@pytest.fixture()
def invalid_config_path(tmp_path_factory: pytest.TempPathFactory) -> pathlib.Path:
    """Fixture for a working folder with an invalid configuration file."""
    work = tmp_path_factory.mktemp("work")
    os.chdir(str(work))

    toml_file = pathlib.Path(__file__).parent.resolve() / "config" / "invalid.toml"
    shutil.copy(toml_file, work / "bob.toml")

    return work


def test_cli_bootstrap(
    mocker: pytest_mock.MockerFixture, no_config_path: pathlib.Path
) -> None:
    """Verify the CLI performs a plain bootstrap operation."""
    # 1. Prepare
    mocker.patch("docopt.docopt")

    docopt.docopt.return_value = {
        "--help": False,
        "--version": False,
        "<target>": None,
        "bootstrap": True,
        "build": False,
        "configure": False,
        "install": False,
        "debug": False,
        "release": False,
    }

    # 2. Execute
    result = main()

    # 3. Verify
    assert result == 0
    cmake = no_config_path / "cmake"
    assert cmake.is_dir()
    cmake_file = cmake / "FindBob.cmake"
    assert cmake_file.is_file()
    ref = pathlib.Path(__file__).parent.resolve() / "ref" / "bootstrap.cmake"
    assert cmake_file.read_text().strip() == ref.read_text().strip()


def bootstrap_calls() -> typing.List[typing.Any]:
    """Generate the mock calls for the bootstrap task."""
    cwd = pathlib.Path.cwd()
    template = (
        pathlib.Path(__file__).parent.parent.resolve()
        / "bob"
        / "templates"
        / "FindBob.cmake"
    )

    return [
        unittest.mock.call(
            ["cmake", "-E", "make_directory", f"{cwd}/cmake"], check=True
        ),
        unittest.mock.call(
            ["cmake", "-E", "copy", str(template), f"{cwd}/cmake"], check=True
        ),
    ]


def test_cli_configure_default(
    mocker: pytest_mock.MockerFixture, no_config_path: pathlib.Path  # noqa: ARG001
) -> None:
    """Verify the CLI performs the correct argument conversion for a configure."""
    # 1. Prepare
    mocker.patch("subprocess.run")
    mocker.patch("docopt.docopt")

    docopt.docopt.return_value = {
        "--help": False,
        "--version": False,
        "<target>": None,
        "bootstrap": False,
        "build": False,
        "configure": True,
        "install": False,
        "debug": False,
        "release": False,
    }

    # 2. Execute
    result = main()

    # 3. Verify
    assert result == 0
    calls = bootstrap_calls()
    calls.append(
        unittest.mock.call(
            [
                "cmake",
                "-B",
                "build/native-release",
                "-S",
                ".",
                "-DCMAKE_BUILD_TYPE=Release",
            ],
            check=True,
        )
    )
    assert subprocess.run.call_count == len(calls)
    subprocess.run.assert_has_calls(calls)


def test_cli_configure_release(mocker: pytest_mock.MockerFixture) -> None:
    """Verify the CLI performs the correct argument conversion for a configure."""
    # 1. Prepare
    mocker.patch("subprocess.run")
    mocker.patch("docopt.docopt")

    docopt.docopt.return_value = {
        "--help": False,
        "--version": False,
        "<target>": None,
        "bootstrap": False,
        "build": False,
        "configure": True,
        "install": False,
        "debug": False,
        "release": True,
    }

    # 2. Execute
    result = main()

    # 3. Verify
    assert result == 0
    calls = bootstrap_calls()
    calls.append(
        unittest.mock.call(
            [
                "cmake",
                "-B",
                "build/native-release",
                "-S",
                ".",
                "-DCMAKE_BUILD_TYPE=Release",
            ],
            check=True,
        )
    )
    assert subprocess.run.call_count == len(calls)
    subprocess.run.assert_has_calls(calls)


def test_cli_configure_debug(mocker: pytest_mock.MockerFixture) -> None:
    """Verify the CLI performs the correct argument conversion for a configure."""
    # 1. Prepare
    mocker.patch("subprocess.run")
    mocker.patch("docopt.docopt")

    docopt.docopt.return_value = {
        "--help": False,
        "--version": False,
        "<target>": None,
        "bootstrap": False,
        "build": False,
        "configure": True,
        "install": False,
        "debug": True,
        "release": False,
    }

    # 2. Execute
    result = main()

    # 3. Verify
    assert result == 0
    calls = bootstrap_calls()
    calls.append(
        unittest.mock.call(
            [
                "cmake",
                "-B",
                "build/native-debug",
                "-S",
                ".",
                "-DCMAKE_BUILD_TYPE=Debug",
            ],
            check=True,
        )
    )
    assert subprocess.run.call_count == len(calls)
    subprocess.run.assert_has_calls(calls)


def dependency_calls() -> typing.List[typing.Any]:
    """Generate the mock calls for the dependencies."""
    cwd = pathlib.Path.cwd()
    return [
        unittest.mock.call(
            [
                "git",
                "clone",
                "https://github.com/renemoll/bob-cmake.git",
                f"{cwd}/external/test",
            ],
            check=True,
        ),
        unittest.mock.call(
            [
                "cmake",
                "-E",
                "chdir",
                f"{cwd}/external/test",
                "git",
                "checkout",
                "master",
            ],
            check=True,
        ),
    ]


def test_cli_configure_linux_default(
    mocker: pytest_mock.MockerFixture, valid_config_path: pathlib.Path  # noqa: ARG001
) -> None:
    """Verify the CLI performs the correct argument conversion for a configure."""
    # 1. Prepare
    mocker.patch("subprocess.run")
    mocker.patch("docopt.docopt")

    docopt.docopt.return_value = {
        "--help": False,
        "--version": False,
        "<target>": "linux",
        "bootstrap": False,
        "build": False,
        "configure": True,
        "install": False,
        "debug": False,
        "release": False,
    }

    # 2. Execute
    result = main()

    # 3. Verify
    assert result == 0
    cwd = pathlib.Path.cwd()
    calls = bootstrap_calls()
    calls += dependency_calls()
    calls.append(
        unittest.mock.call(
            [
                "docker",
                "run",
                "--rm",
                "-v",
                f"{cwd}:/work/",
                "renemoll/builder_clang",
                "cmake",
                "-B",
                "build/linux-release",
                "-S",
                ".",
                "-DCMAKE_BUILD_TYPE=Release",
            ],
            check=True,
        )
    )
    assert subprocess.run.call_count == len(calls)
    subprocess.run.assert_has_calls(calls)


def test_cli_configure_linux_release(
    mocker: pytest_mock.MockerFixture, valid_config_path: pathlib.Path  # noqa: ARG001
) -> None:
    """Verify the CLI performs the correct argument conversion for a configure."""
    # 1. Prepare
    mocker.patch("subprocess.run")
    mocker.patch("docopt.docopt")

    docopt.docopt.return_value = {
        "--help": False,
        "--version": False,
        "<target>": "linux",
        "bootstrap": False,
        "build": False,
        "configure": True,
        "install": False,
        "debug": False,
        "release": True,
    }

    # 2. Execute
    result = main()

    # 3. Verify
    assert result == 0
    cwd = pathlib.Path.cwd()
    calls = bootstrap_calls()
    calls += dependency_calls()
    calls.append(
        unittest.mock.call(
            [
                "docker",
                "run",
                "--rm",
                "-v",
                f"{cwd}:/work/",
                "renemoll/builder_clang",
                "cmake",
                "-B",
                "build/linux-release",
                "-S",
                ".",
                "-DCMAKE_BUILD_TYPE=Release",
            ],
            check=True,
        )
    )
    assert subprocess.run.call_count == len(calls)
    subprocess.run.assert_has_calls(calls)


def test_cli_configure_linux_debug(
    mocker: pytest_mock.MockerFixture, valid_config_path: pathlib.Path  # noqa: ARG001
) -> None:
    """Verify the CLI performs the correct argument conversion for a configure."""
    # 1. Prepare
    mocker.patch("subprocess.run")
    mocker.patch("docopt.docopt")

    docopt.docopt.return_value = {
        "--help": False,
        "--version": False,
        "<target>": "linux",
        "bootstrap": False,
        "build": False,
        "configure": True,
        "install": False,
        "debug": True,
        "release": False,
    }

    # 2. Execute
    result = main()

    # 3. Verify
    assert result == 0
    cwd = pathlib.Path.cwd()
    calls = bootstrap_calls()
    calls += dependency_calls()
    calls.append(
        unittest.mock.call(
            [
                "docker",
                "run",
                "--rm",
                "-v",
                f"{cwd}:/work/",
                "renemoll/builder_clang",
                "cmake",
                "-B",
                "build/linux-debug",
                "-S",
                ".",
                "-DCMAKE_BUILD_TYPE=Debug",
            ],
            check=True,
        )
    )
    assert subprocess.run.call_count == len(calls)
    subprocess.run.assert_has_calls(calls)


def test_cli_configure_stm32_default(
    mocker: pytest_mock.MockerFixture, valid_config_path: pathlib.Path  # noqa: ARG001
) -> None:
    """Verify the CLI performs the correct argument conversion for a configure."""
    # 1. Prepare
    mocker.patch("subprocess.run")
    mocker.patch("docopt.docopt")

    docopt.docopt.return_value = {
        "--help": False,
        "--version": False,
        "<target>": "stm32",
        "bootstrap": False,
        "build": False,
        "configure": True,
        "install": False,
        "debug": False,
        "release": False,
    }

    # 2. Execute
    result = main()

    # 3. Verify
    assert result == 0
    cwd = pathlib.Path.cwd()
    calls = bootstrap_calls()
    calls += dependency_calls()
    calls.append(
        unittest.mock.call(
            [
                "docker",
                "run",
                "--rm",
                "-v",
                f"{cwd}:/work/",
                "renemoll/builder_arm_gcc",
                "cmake",
                "-B",
                "build/stm32-release",
                "-S",
                ".",
                "-DCMAKE_BUILD_TYPE=Release",
                "-DSTM32F4",
                "-G",
                "Ninja",
            ],
            check=True,
        )
    )
    assert subprocess.run.call_count == len(calls)
    subprocess.run.assert_has_calls(calls)


def test_cli_configure_invalid_target(mocker: pytest_mock.MockerFixture) -> None:
    """Verify the CLI performs the correct argument conversion for a configure."""
    # 1. Prepare
    mocker.patch("subprocess.run")
    mocker.patch("docopt.docopt")

    docopt.docopt.return_value = {
        "--help": False,
        "--version": False,
        "<target>": "dummy",
        "bootstrap": False,
        "build": False,
        "configure": True,
        "install": False,
        "debug": True,
        "release": False,
    }

    # 2. Execute
    result = main()

    # 3. Verify
    invalid_arguments_code = 65
    assert result == invalid_arguments_code
    subprocess.run.assert_not_called()


def test_cli_build_default(mocker: pytest_mock.MockerFixture) -> None:
    """Verify the CLI performs the correct argument conversion for a build."""
    # 1. Prepare
    mocker.patch("subprocess.run")
    mocker.patch("docopt.docopt")

    docopt.docopt.return_value = {
        "--help": False,
        "--version": False,
        "<target>": None,
        "bootstrap": False,
        "build": True,
        "configure": False,
        "install": False,
        "debug": False,
        "release": False,
    }

    # 2. Execute
    result = main()

    # 3. Verify
    assert result == 0
    calls = bootstrap_calls()
    calls += dependency_calls()
    calls.append(
        unittest.mock.call(
            [
                "cmake",
                "-B",
                "build/native-release",
                "-S",
                ".",
                "-DCMAKE_BUILD_TYPE=Release",
            ],
            check=True,
        )
    )
    calls.append(
        unittest.mock.call(["cmake", "--build", "build/native-release"], check=True)
    )
    assert subprocess.run.call_count == len(calls)
    subprocess.run.assert_has_calls(calls)


def test_cli_build_release(mocker: pytest_mock.MockerFixture) -> None:
    """Verify the CLI performs the correct argument conversion for a build."""
    # 1. Prepare
    mocker.patch("subprocess.run")
    mocker.patch("docopt.docopt")

    docopt.docopt.return_value = {
        "--help": False,
        "--version": False,
        "<target>": None,
        "bootstrap": False,
        "build": True,
        "configure": False,
        "install": False,
        "debug": False,
        "release": True,
    }

    # 2. Execute
    result = main()

    # 3. Verify
    assert result == 0
    calls = bootstrap_calls()
    calls += dependency_calls()
    calls.append(
        unittest.mock.call(
            [
                "cmake",
                "-B",
                "build/native-release",
                "-S",
                ".",
                "-DCMAKE_BUILD_TYPE=Release",
            ],
            check=True,
        )
    )
    calls.append(
        unittest.mock.call(["cmake", "--build", "build/native-release"], check=True)
    )
    assert subprocess.run.call_count == len(calls)
    subprocess.run.assert_has_calls(calls)


def test_cli_build_debug(mocker: pytest_mock.MockerFixture) -> None:
    """Verify the CLI performs the correct argument conversion for a build."""
    # 1. Prepare
    mocker.patch("subprocess.run")
    mocker.patch("docopt.docopt")

    docopt.docopt.return_value = {
        "--help": False,
        "--version": False,
        "<target>": None,
        "bootstrap": False,
        "build": True,
        "configure": False,
        "install": False,
        "debug": True,
        "release": False,
    }

    # 2. Execute
    result = main()

    # 3. Verify
    assert result == 0
    calls = bootstrap_calls()
    calls += dependency_calls()
    calls.append(
        unittest.mock.call(
            [
                "cmake",
                "-B",
                "build/native-debug",
                "-S",
                ".",
                "-DCMAKE_BUILD_TYPE=Debug",
            ],
            check=True,
        )
    )
    calls.append(
        unittest.mock.call(["cmake", "--build", "build/native-debug"], check=True)
    )
    assert subprocess.run.call_count == len(calls)
    subprocess.run.assert_has_calls(calls)


def test_cli_build_linux_default(mocker: pytest_mock.MockerFixture) -> None:
    """Verify the CLI performs the correct argument conversion for a build."""
    # 1. Prepare
    mocker.patch("subprocess.run")
    mocker.patch("docopt.docopt")

    docopt.docopt.return_value = {
        "--help": False,
        "--version": False,
        "<target>": "linux",
        "bootstrap": False,
        "build": True,
        "configure": False,
        "install": False,
        "debug": False,
        "release": False,
    }

    # 2. Execute
    result = main()

    # 3. Verify
    assert result == 0
    cwd = pathlib.Path.cwd()
    calls = bootstrap_calls()
    calls += dependency_calls()
    calls.append(
        unittest.mock.call(
            [
                "docker",
                "run",
                "--rm",
                "-v",
                f"{cwd}:/work/",
                "renemoll/builder_clang",
                "cmake",
                "-B",
                "build/linux-release",
                "-S",
                ".",
                "-DCMAKE_BUILD_TYPE=Release",
            ],
            check=True,
        )
    )
    calls.append(
        unittest.mock.call(
            [
                "docker",
                "run",
                "--rm",
                "-v",
                f"{cwd}:/work/",
                "renemoll/builder_clang",
                "cmake",
                "--build",
                "build/linux-release",
            ],
            check=True,
        )
    )
    assert subprocess.run.call_count == len(calls)
    subprocess.run.assert_has_calls(calls)


def test_cli_build_linux_release(
    mocker: pytest_mock.MockerFixture, valid_config_path: pathlib.Path  # noqa: ARG001
) -> None:
    """Verify the CLI performs the correct argument conversion for a build."""
    # 1. Prepare
    mocker.patch("subprocess.run")
    mocker.patch("docopt.docopt")

    docopt.docopt.return_value = {
        "--help": False,
        "--version": False,
        "<target>": "linux",
        "bootstrap": False,
        "build": True,
        "configure": False,
        "install": False,
        "debug": False,
        "release": True,
    }

    # 2. Execute
    result = main()

    # 3. Verify
    assert result == 0
    cwd = pathlib.Path.cwd()
    calls = bootstrap_calls()
    calls += dependency_calls()
    calls.append(
        unittest.mock.call(
            [
                "docker",
                "run",
                "--rm",
                "-v",
                f"{cwd}:/work/",
                "renemoll/builder_clang",
                "cmake",
                "-B",
                "build/linux-release",
                "-S",
                ".",
                "-DCMAKE_BUILD_TYPE=Release",
            ],
            check=True,
        )
    )
    calls.append(
        unittest.mock.call(
            [
                "docker",
                "run",
                "--rm",
                "-v",
                f"{cwd}:/work/",
                "renemoll/builder_clang",
                "cmake",
                "--build",
                "build/linux-release",
            ],
            check=True,
        )
    )
    assert subprocess.run.call_count == len(calls)
    subprocess.run.assert_has_calls(calls)


def test_cli_build_linux_debug(
    mocker: pytest_mock.MockerFixture, valid_config_path: pathlib.Path  # noqa: ARG001
) -> None:
    """Verify the CLI performs the correct argument conversion for a build."""
    # 1. Prepare
    mocker.patch("subprocess.run")
    mocker.patch("docopt.docopt")

    docopt.docopt.return_value = {
        "--help": False,
        "--version": False,
        "<target>": "linux",
        "bootstrap": False,
        "build": True,
        "configure": False,
        "install": False,
        "debug": True,
        "release": False,
    }

    # 2. Execute
    result = main()

    # 3. Verify
    assert result == 0
    cwd = pathlib.Path.cwd()
    calls = bootstrap_calls()
    calls += dependency_calls()
    calls.append(
        unittest.mock.call(
            [
                "docker",
                "run",
                "--rm",
                "-v",
                f"{cwd}:/work/",
                "renemoll/builder_clang",
                "cmake",
                "-B",
                "build/linux-debug",
                "-S",
                ".",
                "-DCMAKE_BUILD_TYPE=Debug",
            ],
            check=True,
        )
    )
    calls.append(
        unittest.mock.call(
            [
                "docker",
                "run",
                "--rm",
                "-v",
                f"{cwd}:/work/",
                "renemoll/builder_clang",
                "cmake",
                "--build",
                "build/linux-debug",
            ],
            check=True,
        )
    )
    assert subprocess.run.call_count == len(calls)
    subprocess.run.assert_has_calls(calls)


def test_cli_build_error(mocker: pytest_mock.MockerFixture) -> None:
    """Verify the CLI captures subprocess exceptions."""
    # 1. Prepare
    mocker.patch("subprocess.run")
    mocker.patch("docopt.docopt")

    docopt.docopt.return_value = {
        "--help": False,
        "--version": False,
        "<target>": None,
        "bootstrap": False,
        "build": True,
        "configure": False,
        "install": False,
        "debug": True,
        "release": False,
    }

    subprocess.run.side_effect = subprocess.CalledProcessError(
        returncode=1, cmd="exception_cmd"
    )

    # 2. Execute
    result = main()

    # 3. Verify
    assert result == os.EX_SOFTWARE
    cwd = pathlib.Path.cwd()
    subprocess.run.assert_called_once_with(
        ["cmake", "-E", "make_directory", f"{cwd}/cmake"],
        check=True,
    )


def test_cli_read_toml_file(
    mocker: pytest_mock.MockerFixture, valid_config_path: pathlib.Path
) -> None:
    """Verify the CLI reads and utilizes an options TOML file."""
    # 1. Prepare
    mocker.patch("docopt.docopt")

    docopt.docopt.return_value = {
        "--help": False,
        "--version": False,
        "<target>": None,
        "bootstrap": True,
        "build": False,
        "configure": False,
        "install": False,
        "debug": False,
        "release": False,
    }

    # 2. Execute
    main()

    # 3. Verify
    assert (valid_config_path / "external").is_dir()


def test_cli_error_invalid_toml_file(
    mocker: pytest_mock.MockerFixture, invalid_config_path: pathlib.Path  # noqa: ARG001
) -> None:
    """Verify the CLI reads and utilizes an options TOML file."""
    # 1. Prepare
    mocker.patch("docopt.docopt")

    docopt.docopt.return_value = {
        "--help": False,
        "--version": False,
        "<target>": None,
        "bootstrap": True,
        "build": False,
        "configure": False,
        "install": False,
        "debug": False,
        "release": False,
    }

    # 2. Execute
    main()

    # 3. Verify
    cwd = pathlib.Path.cwd()
    assert not (cwd / "external").is_dir()


def test_cli_install_default(
    mocker: pytest_mock.MockerFixture, valid_config_path: pathlib.Path  # noqa: ARG001
) -> None:
    """Verify the CLI performs the correct argument conversion for an install."""
    # 1. Prepare
    mocker.patch("subprocess.run")
    mocker.patch("docopt.docopt")

    docopt.docopt.return_value = {
        "--help": False,
        "--version": False,
        "<target>": None,
        "bootstrap": False,
        "build": False,
        "configure": False,
        "install": True,
        "debug": False,
        "release": False,
    }

    # 2. Execute
    result = main()

    # 3. Verify
    assert result == 0
    calls = bootstrap_calls()
    calls += dependency_calls()
    calls.append(
        unittest.mock.call(
            [
                "cmake",
                "-B",
                "build/native-release",
                "-S",
                ".",
                "-DCMAKE_BUILD_TYPE=Release",
            ],
            check=True,
        )
    )
    calls.append(
        unittest.mock.call(["cmake", "--build", "build/native-release"], check=True)
    )
    calls.append(
        unittest.mock.call(
            [
                "cmake",
                "--install",
                "build/native-release",
            ],
            check=True,
        )
    )

    assert subprocess.run.call_count == len(calls)
    subprocess.run.assert_has_calls(calls)


def test_cli_install_linux_default(
    mocker: pytest_mock.MockerFixture, valid_config_path: pathlib.Path  # noqa: ARG001
) -> None:
    """Verify the CLI performs the correct argument conversion for an install."""
    # 1. Prepare
    mocker.patch("subprocess.run")
    mocker.patch("docopt.docopt")

    docopt.docopt.return_value = {
        "--help": False,
        "--version": False,
        "<target>": "linux",
        "bootstrap": False,
        "build": False,
        "configure": False,
        "install": True,
        "debug": False,
        "release": False,
    }

    # 2. Execute
    result = main()

    # 3. Verify
    assert result == 0
    cwd = pathlib.Path.cwd()
    calls = bootstrap_calls()
    calls += dependency_calls()
    calls.append(
        unittest.mock.call(
            [
                "docker",
                "run",
                "--rm",
                "-v",
                f"{cwd}:/work/",
                "renemoll/builder_clang",
                "cmake",
                "-B",
                "build/linux-release",
                "-S",
                ".",
                "-DCMAKE_BUILD_TYPE=Release",
            ],
            check=True,
        )
    )
    calls.append(
        unittest.mock.call(
            [
                "docker",
                "run",
                "--rm",
                "-v",
                f"{cwd}:/work/",
                "renemoll/builder_clang",
                "cmake",
                "--build",
                "build/linux-release",
            ],
            check=True,
        )
    )
    calls.append(
        unittest.mock.call(
            [
                "docker",
                "run",
                "--rm",
                "-v",
                f"{cwd}:/work/",
                "renemoll/builder_clang",
                "cmake",
                "--install",
                "build/linux-release",
            ],
            check=True,
        )
    )
    assert subprocess.run.call_count == len(calls)
    subprocess.run.assert_has_calls(calls)
