"""Tests specifically for the bootstrap command."""
import os
import pathlib
import shutil
import urllib.request

import pytest
import pytest_mock

import bob
from bob.tasks.bootstrap import depends_on, generate_commands, parse_env, parse_options


def test_dependency() -> None:
    """Verify bootstraps's dependecies."""
    result = depends_on()

    assert result == []


def test_bootstrap_default_options(tmp_path: pathlib.Path) -> None:
    """Verify the default option to bootstrap a project."""
    # 1. Prepare
    options = {}
    parsed_options = {}
    parse_options(options, parsed_options)
    env = {"root_path": tmp_path}

    # 2. Execute
    result = generate_commands(parsed_options, env)

    # 3. Verify
    nof_commands = 2
    assert len(result) == nof_commands
    assert result[0] == ["cmake", "-E", "make_directory", f"{env['root_path']}/cmake"]
    template_path = pathlib.Path(bob.__file__).parent / "templates"
    template = template_path / "FindBob.cmake"
    assert result[1] == [
        "cmake",
        "-E",
        "copy",
        str(template.resolve()),
        f"{env['root_path']}/cmake",
    ]


def test_bootstrap_no_dependencies_no_toolchains(tmp_path: pathlib.Path) -> None:
    """Verify bootstrap without any dependencies and toolchains."""
    # 1. Prepare
    options = {"dependencies": {}, "toolchains": {}}
    parsed_options = {}
    parse_options(options, parsed_options)

    cwd = tmp_path / "work"
    cwd.mkdir()
    os.chdir(str(cwd))

    env = {"dependencies_path": cwd / "external", "root_path": cwd}

    # 2. Execute
    result = generate_commands(parsed_options, env)

    # 3. Verify
    nof_commands = 2
    assert len(result) == nof_commands


def test_bootstrap_external_git_repo(tmp_path: pathlib.Path) -> None:
    """Verify bootstrap will clone extrnal repositories."""
    # 1. Prepare
    options = {
        "dependencies": {
            "test": {
                "repository": "https://github.com/renemoll/bob-cmake.git",
                "tag": "master",
            },
        }
    }
    parsed_options = {}
    parse_options(options, parsed_options)

    cwd = tmp_path / "work"
    cwd.mkdir()
    os.chdir(str(cwd))

    env = {"dependencies_path": cwd / "external", "root_path": cwd}

    # 2. Execute
    result = generate_commands(parsed_options, env)

    # 3. Verify
    nof_commands = 4
    assert len(result) == nof_commands
    assert result[2] == [
        "git",
        "clone",
        "https://github.com/renemoll/bob-cmake.git",
        str(cwd / "external" / "test"),
    ]
    assert result[3] == [
        "cmake",
        "-E",
        "chdir",
        str(env["dependencies_path"] / "test"),
        "git",
        "checkout",
        "master",
    ]


def test_bootstrap_external_git_repo_already_present(tmp_path: pathlib.Path) -> None:
    """Verify bootstrap clone if the repo is already present."""
    # 1. Prepare
    options = {
        "dependencies": {
            "test": {
                "repository": "https://github.com/renemoll/bob-cmake.git",
                "tag": "master",
            },
        }
    }
    parsed_options = {}
    parse_options(options, parsed_options)

    cwd = tmp_path / "work"
    cwd.mkdir()
    os.chdir(str(cwd))
    repo_path = cwd / "external" / "test"
    repo_path.mkdir(parents=True)

    env = {"dependencies_path": cwd / "external", "root_path": cwd}

    # 2. Execute
    result = generate_commands(parsed_options, env)

    # 3. Verify
    nof_commands = 3
    assert len(result) == nof_commands
    assert result[2] == [
        "cmake",
        "-E",
        "chdir",
        str(env["dependencies_path"] / "test"),
        "git",
        "checkout",
        "master",
    ]


def test_bootstrap_custom_toolchain(
    mocker: pytest_mock.MockerFixture, tmp_path: pathlib.Path
) -> None:
    """Verify toolchain download and unpack."""
    # 1. Prepare
    mocker.patch("shutil.unpack_archive")
    mocker.patch("urllib.request.urlretrieve")

    options = {
        "toolchains": {
            "gcc_arm": {
                "windows": "https://developer.arm.com/-/media/Files/downloads/gnu/12.2.mpacbti-rel1/binrel/arm-gnu-toolchain-12.2.mpacbti-rel1-mingw-w64-i686-arm-none-eabi.zip",
                "linux": "https://developer.arm.com/-/media/Files/downloads/gnu/12.2.mpacbti-rel1/binrel/arm-gnu-toolchain-12.2.mpacbti-rel1-x86_64-arm-none-eabi.tar.xz",
            },
        }
    }
    parsed_options = {}
    parse_options(options, parsed_options)

    cwd = tmp_path / "work"
    cwd.mkdir()
    os.chdir(str(cwd))

    env = parse_env({"root_path": cwd}, parsed_options)

    # 2. Execute
    result = generate_commands(parsed_options, env)

    # 3. Verify
    nof_commands = 2
    assert len(result) == nof_commands
    urllib.request.urlretrieve.assert_called_once_with(
        options["toolchains"]["gcc_arm"]["linux"],
        cwd
        / "toolchains"
        / "download"
        / "arm-gnu-toolchain-12.2.mpacbti-rel1-x86_64-arm-none-eabi.tar.xz",
    )
    shutil.unpack_archive.assert_called_once_with(
        cwd
        / "toolchains"
        / "download"
        / "arm-gnu-toolchain-12.2.mpacbti-rel1-x86_64-arm-none-eabi.tar.xz",
        cwd / "toolchains",
    )


def test_bootstrap_custom_toolchain_already_downloaded(
    mocker: pytest_mock.MockerFixture, tmp_path: pathlib.Path
) -> None:
    """Verify toolchain download is skipped when the archive is present."""
    # 1. Prepare
    mocker.patch("shutil.unpack_archive")
    mocker.patch("urllib.request.urlretrieve")

    options = {
        "toolchains": {
            "gcc_arm": {
                "windows": "https://developer.arm.com/-/media/Files/downloads/gnu/12.2.mpacbti-rel1/binrel/arm-gnu-toolchain-12.2.mpacbti-rel1-mingw-w64-i686-arm-none-eabi.zip",
                "linux": "https://developer.arm.com/-/media/Files/downloads/gnu/12.2.mpacbti-rel1/binrel/arm-gnu-toolchain-12.2.mpacbti-rel1-x86_64-arm-none-eabi.tar.xz",
            },
        }
    }
    parsed_options = {}
    parse_options(options, parsed_options)

    cwd = tmp_path / "work"
    cwd.mkdir()
    os.chdir(str(cwd))

    download_path = cwd / "toolchains" / "download"
    download_path.mkdir(parents=True)
    archive_path = (
        cwd
        / "toolchains"
        / "download"
        / "arm-gnu-toolchain-12.2.mpacbti-rel1-x86_64-arm-none-eabi.tar.xz"
    )
    archive_path.touch()

    env = parse_env({"root_path": cwd}, parsed_options)

    # 2. Execute
    result = generate_commands(parsed_options, env)

    # 3. Verify
    nof_commands = 2
    assert len(result) == nof_commands
    urllib.request.urlretrieve.assert_not_called()
    shutil.unpack_archive.assert_called_once_with(
        cwd
        / "toolchains"
        / "download"
        / "arm-gnu-toolchain-12.2.mpacbti-rel1-x86_64-arm-none-eabi.tar.xz",
        cwd / "toolchains",
    )


def test_bootstrap_custom_toolchain_already_present(
    mocker: pytest_mock.MockerFixture, tmp_path: pathlib.Path
) -> None:
    """Verify toolchain download and unpack is skipped when the toolchain is present."""
    # 1. Prepare
    mocker.patch("shutil.unpack_archive")
    mocker.patch("urllib.request.urlretrieve")

    options = {
        "toolchains": {
            "gcc_arm": {
                "windows": "https://developer.arm.com/-/media/Files/downloads/gnu/12.2.mpacbti-rel1/binrel/arm-gnu-toolchain-12.2.mpacbti-rel1-mingw-w64-i686-arm-none-eabi.zip",
                "linux": "https://developer.arm.com/-/media/Files/downloads/gnu/12.2.mpacbti-rel1/binrel/arm-gnu-toolchain-12.2.mpacbti-rel1-x86_64-arm-none-eabi.tar.xz",
            },
        }
    }
    parsed_options = {}
    parse_options(options, parsed_options)

    cwd = tmp_path / "work"
    cwd.mkdir()
    os.chdir(str(cwd))

    download_path = cwd / "toolchains" / "download"
    download_path.mkdir(parents=True)
    archive_path = (
        cwd
        / "toolchains"
        / "download"
        / "arm-gnu-toolchain-12.2.mpacbti-rel1-x86_64-arm-none-eabi.tar.xz"
    )
    archive_path.touch()
    destination_path = (
        cwd / "toolchains" / "arm-gnu-toolchain-12.2.mpacbti-rel1-x86_64-arm-none-eabi"
    )
    destination_path.mkdir()

    env = parse_env({"root_path": cwd}, parsed_options)

    # 2. Execute
    result = generate_commands(parsed_options, env)

    # 3. Verify
    nof_commands = 2
    assert len(result) == nof_commands
    urllib.request.urlretrieve.assert_not_called()
    shutil.unpack_archive.assert_not_called()


def test_bootstrap_invalid_toolchain_url(tmp_path: pathlib.Path) -> None:
    """Verify bootstrap will clone extrnal repositories."""
    # 1. Prepare
    options = {
        "toolchains": {
            "gcc_arm": {
                "windows": "file://developer.arm.com/-/media/Files/downloads/gnu/12.2.mpacbti-rel1/binrel/arm-gnu-toolchain-12.2.mpacbti-rel1-mingw-w64-i686-arm-none-eabi.zip",
                "linux": "file://developer.arm.com/-/media/Files/downloads/gnu/12.2.mpacbti-rel1/binrel/arm-gnu-toolchain-12.2.mpacbti-rel1-x86_64-arm-none-eabi.tar.xz",
            },
        }
    }
    parsed_options = {}
    parse_options(options, parsed_options)

    cwd = tmp_path / "work"
    cwd.mkdir()
    os.chdir(str(cwd))

    env = parse_env({"root_path": cwd}, parsed_options)

    # 2. Execute
    with pytest.raises(ValueError, match="URL must start with 'http:' or 'https:'"):
        generate_commands(parsed_options, env)
