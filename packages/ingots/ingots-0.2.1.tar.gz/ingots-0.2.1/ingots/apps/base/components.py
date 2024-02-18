__all__ = ("BaseComponent",)

import logging
import typing as t

from ingots.apps.interfaces import ComponentInterface
from ingots.utils.classes_builder import BuildClassInterface

if t.TYPE_CHECKING:
    from .applications import BaseApplication
    from .units import BaseUnit


logger = logging.getLogger(__name__)

CreatingParamsTypeVar = t.TypeVar("CreatingParamsTypeVar")
UnitTypeVar = t.TypeVar("UnitTypeVar", bound="BaseUnit")
ApplicationTypeVar = t.TypeVar("ApplicationTypeVar", bound="BaseApplication")


class BaseComponent(
    BuildClassInterface,
    ComponentInterface[CreatingParamsTypeVar, ApplicationTypeVar, UnitTypeVar],
    t.Generic[CreatingParamsTypeVar, ApplicationTypeVar, UnitTypeVar],
):
    build_class_extensions_order = 5
    shut_down_order = 0

    @classmethod
    def prepare_final_classes(cls): ...

    @classmethod
    def create(cls, unit: UnitTypeVar, params: CreatingParamsTypeVar) -> t.Self:
        return cls(unit=unit, params=params)

    def __init__(self, unit: UnitTypeVar, params: CreatingParamsTypeVar):
        self.unit = unit
        self.application = unit.application
        self.creating_params = params
