__all__ = ("ApplicationRunnerTestCase",)

import typing as t

from ingots.apps.defaults.runners import ApplicationRunner
from ingots.tests.unit.apps.cli import test_runners

if t.TYPE_CHECKING:
    ...

TestedClassTypeVar = t.TypeVar("TestedClassTypeVar", bound=ApplicationRunner)


class ApplicationRunnerTestCase(
    test_runners.CliApplicationRunnerTestCase[TestedClassTypeVar],
    t.Generic[TestedClassTypeVar],
):
    """Contains tests for ApplicationRunner class."""

    tst_cls: type[TestedClassTypeVar] = ApplicationRunner
