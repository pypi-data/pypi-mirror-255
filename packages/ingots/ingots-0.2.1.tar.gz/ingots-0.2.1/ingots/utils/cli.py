__all__ = (
    "CliAbleClassInterface",
    "CliInterface",
    "Cli",
)

import logging
import typing as t
from argparse import ArgumentParser

if t.TYPE_CHECKING:
    from argparse import Namespace


logger = logging.getLogger(__name__)


class CliAbleClassInterface:
    """The CLI mixin provides functionality for working with argument parsers."""

    cli_name: str
    cli_description: str

    @classmethod
    def get_cli_parser_creating_parameters(cls) -> dict:
        """https://docs.python.org/3/library/argparse.html#argumentparser-objects"""
        raise NotImplementedError()

    @classmethod
    def prepare_cli_parser(cls, parser: "ArgumentParser"):
        """https://docs.python.org/3/library/argparse.html#the-add-argument-method"""
        raise NotImplementedError()


class CliInterface:
    cli_name: str
    cli_description: str

    def parse_cli_arguments(self, args: t.Optional[t.List[str]] = None) -> "Namespace":
        raise NotImplementedError()

    def build_cli_parser(self) -> "ArgumentParser":
        raise NotImplementedError()

    def get_cli_parser_creating_parameters(self) -> dict:
        """https://docs.python.org/3/library/argparse.html#argumentparser-objects"""
        raise NotImplementedError()

    def prepare_cli_parser(self, parser: "ArgumentParser"):
        """https://docs.python.org/3/library/argparse.html#the-add-argument-method"""
        raise NotImplementedError()


class Cli(CliInterface):
    def parse_cli_arguments(self, args: t.Optional[t.List[str]] = None) -> "Namespace":
        parser = self.build_cli_parser()
        self.prepare_cli_parser(parser=parser)
        namespace, unknown_arguments = parser.parse_known_args(args=args)
        logger.debug(
            "Parsed CLI arguments: %s. Unknown arguments: %s.",
            namespace,
            unknown_arguments,
        )
        return namespace

    def build_cli_parser(self) -> "ArgumentParser":
        params = self.get_cli_parser_creating_parameters()
        logger.debug("CLI ArgumentParser for: %r. Parameters: %r.", self, params)
        return ArgumentParser(**params)
