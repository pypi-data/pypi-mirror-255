__all__ = ("Unit",)

import logging
import typing as t

from ingots.apps.cli import CliUnit

if t.TYPE_CHECKING:
    from .applications import Application
    from .commands import Command
    from .components import Component
    from .settings import SettingsUnit


logger = logging.getLogger(__name__)


CommandTypeVar = t.TypeVar("CommandTypeVar", bound="Command")
ComponentTypeVar = t.TypeVar("ComponentTypeVar", bound="Component")
ApplicationTypeVar = t.TypeVar("ApplicationTypeVar", bound="Application")


class Unit(
    CliUnit[ApplicationTypeVar, ComponentTypeVar, CommandTypeVar],
    t.Generic[ApplicationTypeVar, ComponentTypeVar, CommandTypeVar],
):
    settings: "SettingsUnit"

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.settings = self.application.settings
