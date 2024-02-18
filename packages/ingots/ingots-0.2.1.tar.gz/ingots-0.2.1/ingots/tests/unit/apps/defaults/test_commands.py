__all__ = ("CommandTestCase",)

import typing as t

from ingots.apps.defaults.commands import Command
from ingots.tests.unit.apps.cli import test_commands

if t.TYPE_CHECKING:
    ...

TestedClassTypeVar = t.TypeVar("TestedClassTypeVar", bound=Command)


class CommandTestCase(
    test_commands.CliCommandTestCase[TestedClassTypeVar],
    t.Generic[TestedClassTypeVar],
):
    """Contains tests for Command class."""

    tst_cls: type[TestedClassTypeVar] = Command
