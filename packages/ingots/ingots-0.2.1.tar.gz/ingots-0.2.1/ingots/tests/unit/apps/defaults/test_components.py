__all__ = ("ComponentTestCase",)

import typing as t

from ingots.apps.defaults.components import Component
from ingots.tests.unit.apps.cli import test_components

if t.TYPE_CHECKING:
    ...

TestedClassTypeVar = t.TypeVar("TestedClassTypeVar", bound=Component)


class ComponentTestCase(
    test_components.CliComponentTestCase[TestedClassTypeVar],
    t.Generic[TestedClassTypeVar],
):
    """Contains tests for Component class."""

    tst_cls: type[TestedClassTypeVar] = Component
