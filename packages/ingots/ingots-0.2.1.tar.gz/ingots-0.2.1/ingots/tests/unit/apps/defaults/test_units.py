__all__ = ("UnitTestCase",)

import typing as t

from ingots.apps.defaults.units import Unit
from ingots.tests.unit.apps.cli import test_units

if t.TYPE_CHECKING:
    ...

TestedClassTypeVar = t.TypeVar("TestedClassTypeVar", bound=Unit)


class UnitTestCase(
    test_units.CliUnitTestCase[TestedClassTypeVar],
    t.Generic[TestedClassTypeVar],
):
    """Contains tests for Unit class."""

    tst_cls: type[TestedClassTypeVar] = Unit
