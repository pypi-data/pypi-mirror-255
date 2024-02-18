__all__ = (
    "CliAbleClassInterfaceTestCase",
    "CliInterfaceTestCase",
)

import typing as t
from unittest.mock import Mock

from ingots.tests.helpers import ClassTestingTestCase
from ingots.utils.cli import CliAbleClassInterface, CliInterface

CliAbleClassInterfaceTypeVar = t.TypeVar(
    "CliAbleClassInterfaceTypeVar", bound=CliAbleClassInterface
)


class CliAbleClassInterfaceTestCase(ClassTestingTestCase[CliAbleClassInterfaceTypeVar]):
    """Contains tests for CliAbleClassInterface class."""

    tst_cls: type["CliAbleClassInterface"] = CliAbleClassInterface

    def test_get_cli_parser_creating_parameters(self):
        """Checks the get_cli_parser_creating_parameters class method."""
        with self.assertRaises(NotImplementedError):
            self.tst_cls.get_cli_parser_creating_parameters()

    def test_prepare_cli_parser(self):
        """Checks the prepare_cli_parser class method."""

        with self.assertRaises(NotImplementedError):
            self.tst_cls.prepare_cli_parser(parser=Mock())


CliInterfaceTypeVar = t.TypeVar("CliInterfaceTypeVar", bound=CliInterface)


class CliInterfaceTestCase(ClassTestingTestCase[CliInterfaceTypeVar]):
    """Contains tests for CliInterface class."""

    tst_cls = CliInterface

    def test_parse_cli_arguments(self):
        """Checks the parse_cli_arguments class method."""
        tst_obj = self.build_tst_obj()

        with self.assertRaises(NotImplementedError):
            tst_obj.parse_cli_arguments()

    def test_build_cli_parser(self):
        """Checks the build_cli_parser class method."""
        tst_obj = self.build_tst_obj()

        with self.assertRaises(NotImplementedError):
            tst_obj.build_cli_parser()

    def test_get_cli_parser_creating_parameters(self):
        """Checks the get_cli_parser_creating_parameters class method."""
        tst_obj = self.build_tst_obj()

        with self.assertRaises(NotImplementedError):
            tst_obj.get_cli_parser_creating_parameters()

    def test_prepare_cli_parser(self):
        """Checks the prepare_cli_parser class method."""
        tst_obj = self.build_tst_obj()

        with self.assertRaises(NotImplementedError):
            tst_obj.prepare_cli_parser(parser=Mock())
