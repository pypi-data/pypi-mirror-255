__all__ = ("Component",)

import logging
import typing as t

from ingots.apps.cli import CliComponent

if t.TYPE_CHECKING:
    from .applications import Application
    from .settings import SettingsUnit
    from .units import Unit


logger = logging.getLogger(__name__)


UnitTypeVar = t.TypeVar("UnitTypeVar", bound="Unit")
ApplicationTypeVar = t.TypeVar("ApplicationTypeVar", bound="Application")


class Component(
    CliComponent[ApplicationTypeVar, UnitTypeVar],
    t.Generic[ApplicationTypeVar, UnitTypeVar],
):
    settings: "SettingsUnit"

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.settings = self.application.settings
