__all__ = ("CliComponentTestCase",)

import typing as t
from unittest.mock import Mock

from ingots.apps.cli.components import CliComponent
from ingots.tests.unit.apps.base import test_components

if t.TYPE_CHECKING:
    ...


TestedClassTypeVar = t.TypeVar("TestedClassTypeVar", bound=CliComponent)


class CliComponentTestCase(
    test_components.BaseComponentTestCase[TestedClassTypeVar],
    t.Generic[TestedClassTypeVar],
):
    """Contains tests for CliComponent class."""

    tst_cls: type[TestedClassTypeVar] = CliComponent

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
