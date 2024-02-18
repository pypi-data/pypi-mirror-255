__all__ = ("CliUnit",)

import logging
import typing as t

from ingots.apps.base import BaseUnit
from ingots.utils.cli import CliAbleClassInterface

if t.TYPE_CHECKING:
    from argparse import ArgumentParser, Namespace  # noqa

    from .applications import CliApplication
    from .commands import CliCommand
    from .components import CliComponent


logger = logging.getLogger(__name__)

ApplicationTypeVar = t.TypeVar("ApplicationTypeVar", bound="CliApplication")
ComponentTypeVar = t.TypeVar("ComponentTypeVar", bound="CliComponent")
CommandTypeVar = t.TypeVar("CommandTypeVar", bound="CliCommand")


class CliUnit(
    CliAbleClassInterface,
    BaseUnit["Namespace", ApplicationTypeVar, ComponentTypeVar, CommandTypeVar],
    t.Generic[ApplicationTypeVar, ComponentTypeVar, CommandTypeVar],
):
    @classmethod
    def get_cli_parser_creating_parameters(cls) -> dict:
        return {
            "description": cls.cli_description,
        }

    @classmethod
    def prepare_cli_parser(cls, parser: "ArgumentParser"): ...

    @classmethod
    def get_base_command_cls_by_cli_name(cls, name: str) -> type[CommandTypeVar]:
        return [
            i for i in cls._final_commands_classes_map.keys() if i.cli_name == name
        ][0]
