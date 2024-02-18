"""The builder, Bob the builder.

Usage:
    bob.py bootstrap [<target>]
    bob.py configure [<target>] [(debug|release)]
    bob.py build [<target>] [(debug|release)]
    bob.py install [<target>] [(debug|release)]
    bob.py -h | --help
    bob.py --version

Possible commands:
    bootstrap: retrieve tooling/external dependencies.
    build:     build the project for the a target.
    configure: prepare the project for the first build, automatically executed with build.
    install:   build and install the project.

Options:
    -h --help        Show this screen.
    --version        Show version.
"""
import logging
import pathlib
import subprocess
import typing

import docopt
import toml

from bob import __version__
from bob.api import Command
from bob.bob import bob
from bob.compat import EX_DATAERR, EX_OK, EX_SOFTWARE
from bob.typehints import OptionsMapT

ArgsT = typing.TypeVar("ArgsT", None, bool, str)


def main() -> int:
    """CLI entry-point.

    Returns:
        A result code to be returned to the OS.
    """
    logging.basicConfig(
        level=logging.DEBUG,
        format="%(asctime)s - %(filename)s:%(lineno)s - %(levelname)s: %(message)s",
        datefmt="%Y.%m.%d %H:%M:%S",
    )

    arguments = docopt.docopt(__doc__, version=__version__)
    logging.debug(arguments)
    try:
        command = _determine_command(arguments)
        options = _determine_options(arguments)
    except ValueError:
        logging.exception("Exception caught parsing input")
        return EX_DATAERR

    try:
        bob(command, options)
    except ValueError:
        logging.exception("Exception caught parsing input")
        return EX_DATAERR
    except subprocess.CalledProcessError:
        logging.exception("Exception caught executing commands")
        return EX_SOFTWARE

    return EX_OK


def _determine_command(arguments: typing.Mapping[str, ArgsT]) -> Command:
    if arguments["bootstrap"]:
        return Command.Bootstrap
    if arguments["configure"]:
        return Command.Configure
    if arguments["install"]:
        return Command.Install
    return Command.Build


def _determine_options(arguments: typing.Mapping[str, ArgsT]) -> OptionsMapT:
    """Returns map with options based on the given arguments.

    Args:
        arguments (dict): a map with input arguments.

    Returns:
        A map representing the options for each step.

    Raises:
        ValueError: upon errors parsing a `bob.toml` file.
    """
    options = {
        "config": _determine_build_config(arguments),
        "target": _determine_build_target(arguments),
    }

    cwd = pathlib.Path.cwd()
    toml_file = cwd / "bob.toml"

    try:
        file_options = toml.load(toml_file)
        logging.debug("Loading settings: %s", toml_file)
        options.update(file_options)
    except FileNotFoundError:
        pass
    except Exception as ex:
        logging.exception("Exception caught parsing %s", toml_file)
        raise ValueError from ex

    return options


def _determine_build_config(arguments: typing.Mapping[str, ArgsT]) -> str:
    if arguments["release"]:
        return "release"
    if arguments["debug"]:
        return "debug"

    logging.info("No build config selected, defaulting to release build config")
    return "release"


def _determine_build_target(arguments: typing.Mapping[str, ArgsT]) -> str:
    try:
        return arguments["<target>"].lower()  # type: ignore [attr-defined]
    except AttributeError:
        logging.info("No build target selected, defaulting to native build target")
        return "native"
