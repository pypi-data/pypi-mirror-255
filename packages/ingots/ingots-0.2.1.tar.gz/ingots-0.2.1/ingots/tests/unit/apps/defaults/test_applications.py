__all__ = ("ApplicationTestCase",)

import typing as t

from ingots.apps.defaults.applications import Application
from ingots.tests.unit.apps.defaults.settings import test_applications

if t.TYPE_CHECKING:
    ...

TestedClassTypeVar = t.TypeVar("TestedClassTypeVar", bound=Application)


class ApplicationTestCase(
    test_applications.SettingsApplicationTestCase[TestedClassTypeVar],
    t.Generic[TestedClassTypeVar],
):
    """Contains tests for Application class."""

    tst_cls: type[TestedClassTypeVar] = Application
