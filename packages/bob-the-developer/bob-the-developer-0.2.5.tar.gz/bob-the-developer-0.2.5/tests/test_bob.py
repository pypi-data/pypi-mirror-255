"""Test the basic flow for each command."""

import subprocess

import pytest_mock

import bob


def test_bob_configure(mocker: pytest_mock.MockerFixture) -> None:
    """Verify the configure command produces a configure command call."""
    # 1. Prepare
    mocker.patch("subprocess.run")

    cmd = bob.Command.Configure
    options = {
        "config": "Debug",
        "target": "native",
    }

    # 2. Execute
    bob.bob(cmd, options)

    # 3. Verify
    subprocess.run.assert_any_call(
        ["cmake", "-B", "build/native-debug", "-S", ".", "-DCMAKE_BUILD_TYPE=Debug"],
        check=True,
    )


def test_bob_build(mocker: pytest_mock.MockerFixture) -> None:
    """Verify the build command produces a configure and build command call.

    Todo:
    * Improve by enforcing call order. However, I do not want to assert every in between call.
    """
    # 1. Prepare
    mocker.patch("subprocess.run")

    cmd = bob.Command.Build
    options = {
        "config": "release",
        "target": "native",
    }

    # 2. Execute
    bob.bob(cmd, options)

    # 3. Verify
    subprocess.run.assert_any_call(
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
    subprocess.run.assert_any_call(
        ["cmake", "--build", "build/native-release"], check=True
    )


def test_bob_invalid_toolchain_url(mocker: pytest_mock.MockerFixture) -> None:
    """Verify bootstrap checks URLs."""
    # 1. Prepare
    mocker.patch("subprocess.run")

    cmd = bob.Command.Build
    options = {
        "config": "release",
        "target": "stm32",
        "toolchains": {
            "gcc_arm": {
                "windows": "file://developer.arm.com/-/media/Files/downloads/gnu/12.2.mpacbti-rel1/binrel/arm-gnu-toolchain-12.2.mpacbti-rel1-mingw-w64-i686-arm-none-eabi.zip",
                "linux": "file://developer.arm.com/-/media/Files/downloads/gnu/12.2.mpacbti-rel1/binrel/arm-gnu-toolchain-12.2.mpacbti-rel1-x86_64-arm-none-eabi.tar.xz",
            },
        },
        "targets": {"stm32": {"toolchain": "gcc_arm"}},
    }

    # 2. Execute
    bob.bob(cmd, options)

    # 3. Verify
    subprocess.run.assert_not_called()
