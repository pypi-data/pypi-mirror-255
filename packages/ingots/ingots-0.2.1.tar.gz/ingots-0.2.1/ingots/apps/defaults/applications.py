__all__ = ("Application",)

import logging
import typing as t

from .settings import SettingsApplication

if t.TYPE_CHECKING:
    from .components import Component
    from .units import Unit


logger = logging.getLogger(__name__)


ComponentTypeVar = t.TypeVar("ComponentTypeVar", bound="Component")
UnitTypeVar = t.TypeVar("UnitTypeVar", bound="Unit")


class Application(
    SettingsApplication[UnitTypeVar, ComponentTypeVar],
    t.Generic[UnitTypeVar, ComponentTypeVar],
): ...
