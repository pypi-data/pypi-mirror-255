__all__ = ("SettingsApplication",)

import logging
import typing as t
from logging.config import dictConfig

from .components import EnvConfigsApplication
from .units import SettingsUnit

if t.TYPE_CHECKING:
    from ingots.apps.cli import CliComponent, CliUnit


logger = logging.getLogger(__name__)

UnitTypeVar = t.TypeVar("UnitTypeVar", bound="CliUnit")
ComponentTypeVar = t.TypeVar("ComponentTypeVar", bound="CliComponent")


class SettingsApplication(
    EnvConfigsApplication[UnitTypeVar, ComponentTypeVar],
    t.Generic[UnitTypeVar, ComponentTypeVar],
):
    settings: "SettingsUnit"

    @classmethod
    def register_units_classes(cls) -> set[type[UnitTypeVar]]:
        classes = super().register_units_classes()
        classes.add(SettingsUnit)  # type: ignore
        return classes

    async def configure(self):
        self.settings = await self.get_unit(unit_cls=SettingsUnit)  # type: ignore
        self.configure_logging()

    def configure_logging(self):
        config = self.settings.build_logging_dict_config()
        logger.info("Logging config: %s.", config)
        dictConfig(config)
