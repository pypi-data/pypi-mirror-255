"""The bootstrap task prepares the codebase for building.

Bootstrapping ensures all dependencies and toolchains are avaialble. Actual building of
dependencies is out of scope due to the project to project variation.
"""
import collections.abc
import contextlib
import logging
import pathlib
import platform
import shutil
import typing
import urllib.request

from bob.api import Command
from bob.typehints import CommandListT, EnvMapT, OptionsMapT


def depends_on() -> typing.List[Command]:
    """Generate a list of task names this task depends on.

    Returns:
        A list of commands.
    """
    return []


def parse_env(env: EnvMapT, options: OptionsMapT) -> EnvMapT:
    """Update the envorinment map.

    Args:
        env: a map with relevant locations in the codebase.
        options: set of options to take into account.

    Returns:
        An updated env map.
    """
    try:
        env["dependencies_path"] = pathlib.Path(options["dependencies"]["folder"])
    except KeyError:
        env["dependencies_path"] = env["root_path"] / "external"

    try:
        env["toolchains_path"] = pathlib.Path(options["toolchains"]["folder"])
    except KeyError:
        env["toolchains_path"] = env["root_path"] / "toolchains"

    return env


def parse_options(options: OptionsMapT, parsed: OptionsMapT) -> None:
    """Update the options map.

    Args:
        options: set of options passed as input.
        parsed: parsed options.

    Todo:
    - toolchain may have container and archive?
    """
    parsed["bootstrap"] = {}

    deps = {}
    with contextlib.suppress(KeyError):
        for k, v in options["dependencies"].items():
            if isinstance(v, collections.abc.Mapping):
                deps[k] = v
    parsed["bootstrap"]["dependencies"] = deps

    tools = {}
    with contextlib.suppress(KeyError):
        os = platform.system().lower()
        for k, v in options["toolchains"].items():
            with contextlib.suppress(TypeError, KeyError):
                tools[k] = v[os]
    parsed["bootstrap"]["toolchains"] = tools


def generate_commands(options: OptionsMapT, env: EnvMapT) -> CommandListT:
    """Generate a set of commands to prepare the codebase.

    Args:
        options: set of options to take into account.
        env: a map with relevant locations in the codebase.

    Returns:
        A list of commands, each command is a list of strings which can be
        passed to `subprocess.run`.
    """
    result = []
    result += _setup_bob(env["root_path"])

    with contextlib.suppress(KeyError):
        result += _gather_dependencies(
            options["bootstrap"]["dependencies"],
            env["dependencies_path"],
        )

    with contextlib.suppress(KeyError):
        _gather_toolchain(
            options["bootstrap"]["toolchains"],
            env["toolchains_path"],
        )

    return result


def _setup_bob(root_path: pathlib.Path) -> CommandListT:
    """Install Bob into the cmake folder.

    Todo:
     - determine if FindBob.cmake should always be overwritten. Might not be expected by users.
    """
    output_folder = root_path / "cmake"
    logging.debug("Determined cmake folder: %s", output_folder)
    output_folder.mkdir(parents=True, exist_ok=True)

    base_file = (
        pathlib.Path(__file__).parent.parent.resolve() / "templates" / "FindBob.cmake"
    )

    return [
        ["cmake", "-E", "make_directory", str(output_folder)],
        ["cmake", "-E", "copy", str(base_file), str(output_folder)],
    ]


def _gather_dependencies(
    deps: typing.Mapping[str, typing.Mapping[str, typing.Any]],
    output_path: pathlib.Path,
) -> CommandListT:
    if len(deps) == 0:
        return []

    logging.debug("Ensure external folder: %s", output_path)
    output_path.mkdir(parents=True, exist_ok=True)

    result = []
    for name, options in deps.items():
        logging.info("Found external dependecy: %s", name)
        rep_path = output_path / name

        if not rep_path.exists():
            result.append(["git", "clone", options["repository"], str(rep_path)])

        result.append(
            ["cmake", "-E", "chdir", str(rep_path), "git", "checkout", options["tag"]]
        )

    return result


def _get_package(url: str, output_path: pathlib.Path) -> pathlib.Path:
    path = output_path / pathlib.Path(url).name
    logging.info("Retrieving: %s", pathlib.Path(url).name)

    if not path.exists():
        logging.info("Downloading: %s", url)

        #
        # Yes, using urllib.request but limiting the protocols beforehand.
        #
        if not url.startswith(("http:", "https:")):
            raise ValueError("URL must start with 'http:' or 'https:'")

        urllib.request.urlretrieve(url, path)  # noqa: S310
    else:
        logging.info("Archive found: %s", path)

    return path


def _remove_suffix_from_archive_name(name: str) -> str:
    def format_to_suffix(x: str) -> str:
        if "tar" in x and x.find("tar") > 0:
            return f".tar.{x.replace('tar', '')}"
        return f".{x}"

    formats = [format_to_suffix(x[0]) for x in shutil.get_archive_formats()]

    for x in formats:
        if name.endswith(x):
            return name.replace(x, "")

    raise ValueError("Unsupported archive type")


def _extract_package(archive: pathlib.Path, output_path: pathlib.Path) -> None:
    logging.info("Extracting: %s to %s", archive, output_path)
    expected = output_path / _remove_suffix_from_archive_name(archive.name)
    if not expected.exists():
        shutil.unpack_archive(archive, output_path)


def _gather_toolchain(
    toolchains: typing.Mapping[str, str], output_path: pathlib.Path
) -> None:
    if len(toolchains) == 0:
        return

    logging.debug("Ensure toolchain folder: %s", output_path)
    output_path.mkdir(parents=True, exist_ok=True)
    archive_path = output_path / "download"
    archive_path.mkdir(parents=True, exist_ok=True)

    for name, url in toolchains.items():
        logging.info("Found toolchain dependency: %s", name)
        archive = _get_package(url, archive_path)
        _extract_package(archive, output_path)
