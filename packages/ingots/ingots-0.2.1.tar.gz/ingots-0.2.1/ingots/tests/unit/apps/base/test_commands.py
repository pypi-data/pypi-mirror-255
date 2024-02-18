__all__ = ("BaseCommandTestCase",)

import typing as t
from unittest.mock import Mock

from ingots.apps.base.commands import BaseCommand
from ingots.tests.unit.apps import test_interfaces

if t.TYPE_CHECKING:
    ...


TestedClassTypeVar = t.TypeVar("TestedClassTypeVar", bound=BaseCommand)


class BaseCommandTestCase(
    test_interfaces.CommandInterfaceTestCase[TestedClassTypeVar],
    t.Generic[TestedClassTypeVar],
):
    """Contains tests for BaseCommand class."""

    tst_cls: type[TestedClassTypeVar] = BaseCommand

    def get_tst_obj_init_params(self, **kwargs) -> dict:
        kwargs.setdefault("unit", Mock())
        kwargs.setdefault("params", Mock())
        return super().get_tst_obj_init_params(**kwargs)

    def test_create(self):
        """Checks the create class method."""
        tst_obj = self.tst_cls.create(unit=Mock(), params=Mock())

        assert isinstance(tst_obj, self.tst_cls)

    def test_init(self):
        """Checks the __init__ method."""
        mock_unit = Mock()
        mock_unit.application = Mock()
        mock_creating_params = Mock()

        tst_obj = self.build_tst_obj(unit=mock_unit, params=mock_creating_params)

        assert tst_obj.unit == mock_unit
        assert tst_obj.application == mock_unit.application
        assert tst_obj.creating_params == mock_creating_params
