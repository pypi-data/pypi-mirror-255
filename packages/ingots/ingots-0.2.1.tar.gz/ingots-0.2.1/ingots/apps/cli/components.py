__all__ = ("CliComponent",)

import logging
import typing as t

from ingots.apps.base import BaseComponent
from ingots.utils.cli import CliAbleClassInterface

if t.TYPE_CHECKING:
    from argparse import ArgumentParser, Namespace  # noqa

    from .applications import CliApplication
    from .units import CliUnit


logger = logging.getLogger(__name__)

UnitTypeVar = t.TypeVar("UnitTypeVar", bound="CliUnit")
ApplicationTypeVar = t.TypeVar("ApplicationTypeVar", bound="CliApplication")


class CliComponent(
    CliAbleClassInterface,
    BaseComponent["Namespace", ApplicationTypeVar, UnitTypeVar],
    t.Generic[ApplicationTypeVar, UnitTypeVar],
):
    @classmethod
    def get_cli_parser_creating_parameters(cls) -> dict:
        return {
            "description": cls.cli_description,
        }

    @classmethod
    def prepare_cli_parser(cls, parser: "ArgumentParser"): ...
