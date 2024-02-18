__all__ = ("CliUnitTestCase",)

import typing as t
from unittest.mock import Mock

from ingots.apps.cli.units import CliUnit
from ingots.tests.unit.apps.base import test_units

if t.TYPE_CHECKING:
    ...


TestedClassTypeVar = t.TypeVar("TestedClassTypeVar", bound=CliUnit)


class CliUnitTestCase(
    test_units.BaseUnitTestCase[TestedClassTypeVar],
    t.Generic[TestedClassTypeVar],
):
    """Contains tests for CliUnit class."""

    tst_cls: type[TestedClassTypeVar] = CliUnit

    def test_get_cli_parser_creating_parameters(self):
        """Checks the get_cli_parser_creating_parameters class method."""
        tst_cls = self.build_tst_cls()
        tst_cls.cli_description = "Test CLI description"

        tst_res = tst_cls.get_cli_parser_creating_parameters()

        assert tst_res == {"description": "Test CLI description"}

    def test_prepare_cli_parser(self):
        """Checks the prepare_cli_parser class method."""
        tst_res = self.tst_cls.prepare_cli_parser(parser=Mock())
        assert tst_res is None
