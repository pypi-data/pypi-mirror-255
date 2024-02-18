"""Task loader.

Each command Bob can execute has a corresponding module. These modules provide
isoalted functionality solely for the specific command. Additionally, each module
implement the same interface.
"""
import enum
import importlib
import logging
import pathlib
import pkgutil
import types

from bob.api import Command


def get_task(command: Command) -> types.ModuleType:
    """Get the module corresponding to the given task.

    Args:
        command: a valid Command

    Returns:
        A module to execute the command.

    Raises:
        ValueError: when the task has no corresponding module.
    """
    for t in _list_tasks():  # type: ignore [attr-defined]
        if t.name == command.name:
            return _load_task(t)

    raise ValueError(f"No corresponding task for {command}")  # pragma: no cover


def _list_tasks() -> enum.Enum:
    tasks_path = pathlib.Path(__file__).parent.resolve() / "tasks"
    modules = [
        name.capitalize() for _, name, _ in pkgutil.iter_modules([str(tasks_path)])
    ]
    logging.debug("Found the following modules: %s", modules)
    return enum.Enum("Tasks", modules)


def _load_task(task: enum.Enum) -> types.ModuleType:
    return importlib.import_module(f".tasks.{task.name.lower()}", "bob")
