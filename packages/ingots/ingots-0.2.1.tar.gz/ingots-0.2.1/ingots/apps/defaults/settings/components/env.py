__all__ = (
    "EnvConfigsUpdatorComponent",
    "EnvConfigsApplication",
)

import logging
import os
import typing as t

from ingots.apps.cli import CliApplication, CliComponent
from ingots.utils import delimiters

if t.TYPE_CHECKING:
    from ingots.apps.cli import CliUnit

    from .units import SettingsUnit  # noqa


logger = logging.getLogger(__name__)

UnitTypeVar = t.TypeVar("UnitTypeVar", bound="CliUnit")
ComponentTypeVar = t.TypeVar("ComponentTypeVar", bound="CliComponent")


class EnvConfigsApplication(
    CliApplication[UnitTypeVar, ComponentTypeVar],
    t.Generic[UnitTypeVar, ComponentTypeVar],
):
    env_configs_prefix: str
    env_configs_prefix_delimiter: str = delimiters.UNDERSCORE


class EnvConfigsUpdatorComponent(CliComponent["EnvConfigsApplication", "SettingsUnit"]):
    cli_name = "env-configs-updator"
    cli_description = "Provides configs updating from environment."

    unit: "SettingsUnit"

    @classmethod
    def prepare_final_classes(cls): ...

    async def configure(self):
        suitable_configs_overrides = self.find_suitable_configs_overrides()
        for name, raw_value in suitable_configs_overrides.items():
            self.unit.set_config_value(name=name, raw_value=raw_value)

    def find_suitable_configs_overrides(self) -> t.Dict[str, str]:
        suitable_configs_overrides = {}
        full_prefix = (
            f"{self.application.env_configs_prefix.upper()}"
            f"{self.application.env_configs_prefix_delimiter}"
        )
        logger.debug(
            "ENV. Prefix: %s. All process environment variables: %s.",
            full_prefix,
            os.environ,
        )
        for key, raw_value in os.environ.items():
            key = key.upper()
            if not key.startswith(full_prefix):
                continue
            suitable_configs_overrides[key.replace(full_prefix, "")] = raw_value
        logger.info("ENV. Configs overrides: %s.", suitable_configs_overrides)
        return suitable_configs_overrides

    async def shut_down(self): ...
