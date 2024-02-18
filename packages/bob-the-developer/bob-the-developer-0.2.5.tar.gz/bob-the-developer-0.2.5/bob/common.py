"""Module with functionality shared between various modules."""
import contextlib
import enum
import logging
import pathlib
import typing

from bob.api import BuildConfig
from bob.typehints import BuildTargetT, OptionsMapT


def determine_output_folder(options: OptionsMapT) -> str:
    """Generate the output path based on project settings.

    Args:
        options: set of options to take into account.

    Returns:
        The output' folder name for the given options.
    """
    return f"{options['build_target'].name}-{options['build_config']}".lower()


def parse_options(options: OptionsMapT) -> OptionsMapT:
    """Update the options map.

    Args:
        options: set of options to take into account.

    Returns:
        An updated options map.
    """
    result = {
        "build_config": _determine_config(options),
        "build_target": _determine_build_target(options),
    }

    with contextlib.suppress(KeyError):
        target = result["build_target"].name.lower()  # type: ignore [attr-defined]
        toolchain = options["targets"][target]["toolchain"]
        result["container"] = options["toolchains"][toolchain]["container"]

    return result


def _determine_config(options: OptionsMapT) -> BuildConfig:
    try:
        config = options["config"].lower()
        if config == "debug":
            return BuildConfig.Debug
        return BuildConfig.Release  # noqa: TRY300
    except KeyError:
        logging.info("No build config selected, defaulting to release build config")
        return BuildConfig.Release


def generate_targets(targets: typing.Sequence[str]) -> enum.Enum:
    """Generate an Enum for the available targers."""
    names = [x.capitalize() for x in targets]
    return enum.Enum("BuildTarget", names)


def _determine_build_target(options: OptionsMapT) -> BuildTargetT:
    targets = ["native"]
    with contextlib.suppress(KeyError):
        targets += list(options["targets"].keys())
    build_targets = generate_targets(targets)

    try:
        target = options["target"].lower().capitalize()
        for x in build_targets:  # type: ignore [attr-defined]
            if x.name == target:
                return x

        raise ValueError(f"Invalid target specified: {target}")
    except KeyError:
        logging.info("No build target selected, defaulting to native build target")
        return build_targets.Native  # type: ignore [attr-defined]


def generate_container_command(
    options: OptionsMapT, cwd: pathlib.Path
) -> typing.List[str]:
    """Generate a Docker command to prepend the build command.

    Args:
        options: set of options to take into account.
        cwd: the path to the codebase.

    Returns:
        List representing a single command, ready to be passed to subprocess.run.
    """
    try:
        return [
            "docker",
            "run",
            "--rm",
            "-v",
            f"{cwd}:/work/",
            options["container"],
        ]
    except KeyError:
        return []
