__all__ = ("CliApplication",)

import logging
import typing as t

from ingots.apps.base import BaseApplication
from ingots.utils.cli import CliAbleClassInterface

if t.TYPE_CHECKING:
    from argparse import ArgumentParser, Namespace  # noqa

    from .components import CliComponent
    from .units import CliUnit


logger = logging.getLogger(__name__)

UnitTypeVar = t.TypeVar("UnitTypeVar", bound="CliUnit")
ComponentTypeVar = t.TypeVar("ComponentTypeVar", bound="CliComponent")


class CliApplication(
    CliAbleClassInterface,
    BaseApplication["Namespace", UnitTypeVar, ComponentTypeVar],
    t.Generic[UnitTypeVar, ComponentTypeVar],
):
    @classmethod
    def get_cli_parser_creating_parameters(cls) -> dict:
        return {
            "description": cls.cli_description,
        }

    @classmethod
    def prepare_cli_parser(cls, parser: "ArgumentParser"): ...

    @classmethod
    def get_base_unit_cls_by_cli_name(cls, name: str) -> type[UnitTypeVar]:
        return [i for i in cls._final_units_classes_map.keys() if i.cli_name == name][0]
