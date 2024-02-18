"""Test API types."""

from bob.api import BuildConfig, Command


def test_command_to_string() -> None:
    """Verify Command type can be converted to string (note the case)."""
    assert str(Command.Build) == "Build"


def test_buildconfig_to_string() -> None:
    """Verify BuildConfig type can be converted to string (note the case)."""
    assert str(BuildConfig.Release) == "Release"
