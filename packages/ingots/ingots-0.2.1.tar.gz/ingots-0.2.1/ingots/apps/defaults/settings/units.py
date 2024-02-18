__all__ = ("SettingsUnit",)

import logging
import typing as t

from ingots.apps.cli import CliUnit
from ingots.utils.logging import (
    INGOTS_LOGGING_MARKER,
    STARTUP_LOGGING_FORMAT,
    ContextVarsFilter,
)

from .commands import ListCommand
from .components import (
    CliConfigsUpdatorComponent,
    EnvConfigsUpdatorComponent,
    FileConfigsUpdatorComponent,
)

if t.TYPE_CHECKING:
    from ingots.apps.cli import CliCommand, CliComponent

    from .applications import SettingsApplication  # noqa


logger = logging.getLogger(__name__)


class SettingsUnit(
    CliUnit["SettingsApplication", "CliComponent", "CliCommand"],
):
    cli_name = "settings"
    cli_description = "Provides project's configs."

    @classmethod
    def register_components_classes(cls) -> set[type["CliComponent"]]:
        classes = super().register_components_classes()
        classes.add(FileConfigsUpdatorComponent)
        classes.add(EnvConfigsUpdatorComponent)
        classes.add(CliConfigsUpdatorComponent)
        return classes

    @classmethod
    def register_commands_classes(cls) -> set[type["CliCommand"]]:
        classes = super().register_commands_classes()
        classes.add(ListCommand)
        return classes

    async def configure(self):
        await self.get_component(component_cls=FileConfigsUpdatorComponent)
        await self.shut_down_component(component_cls=FileConfigsUpdatorComponent)

        await self.get_component(component_cls=EnvConfigsUpdatorComponent)
        await self.shut_down_component(component_cls=EnvConfigsUpdatorComponent)

        await self.get_component(component_cls=CliConfigsUpdatorComponent)
        await self.shut_down_component(component_cls=CliConfigsUpdatorComponent)

    def set_config_value(self, name: str, raw_value: t.Any):
        if not hasattr(self, name):
            logger.warning("Undefined config: %s.", name)
            return

        try:
            new_value = self.coerce_value(name=name, raw_value=raw_value)
        except Exception as err:
            logger.warning(
                "Coercing error: %r. Config: %s. Raw value: %s.",
                err,
                name,
                raw_value,
            )
            return
        else:
            logger.info(
                "Config: %s. New value: %s.",
                name,
                new_value,
            )
            setattr(self, name, new_value)

    def coerce_value(self, name: str, raw_value: t.Any) -> t.Any:
        config_type = type(getattr(self, name))
        if isinstance(raw_value, config_type):
            return raw_value

        return config_type(raw_value)

    def get_configs(self) -> list[tuple[str, t.Any]]:
        return [
            (attr_name, getattr(self, attr_name))
            for attr_name in dir(self)
            if attr_name.upper() == attr_name  # all configs are in UPPER_CASE
        ]

    # region Logging
    LOGGING_VERSION = 1
    LOGGING_DISABLE_EXISTING_LOGGERS: bool = False
    LOGGING_INCREMENTAL: bool = False

    LOGGING_DEFAULT_FORMAT = (
        f"%(asctime)s ▶ {STARTUP_LOGGING_FORMAT} ▶ %(ctx)s ▶ %(taskName)s"
    )

    INGOTS_LOGGING_LEVEL: str = "INFO"

    LOGGING_ENABLE_ROOT_LOGGER: bool = False
    LOGGING_ROOT_LOGGER_LEVEL: str = "INFO"

    def get_logging_formatters_config(self) -> dict[str, dict]:
        return {
            "default": {
                "format": self.LOGGING_DEFAULT_FORMAT,
            },
            "ingots": {
                "format": f"{INGOTS_LOGGING_MARKER} {self.LOGGING_DEFAULT_FORMAT}",
            },
        }

    def get_logging_filters_config(self) -> dict[str, dict]:
        return {
            "ctx": {
                "()": ContextVarsFilter,
            },
        }

    def get_logging_handlers_config(self) -> dict[str, dict]:
        return {
            "default": {
                "formatter": "default",
                "filters": ["ctx"],
            },
            "ingots": {
                "formatter": "ingots",
                "filters": ["ctx"],
            },
        }

    def get_logging_loggers_config(self) -> dict[str, dict]:
        return {
            "ingots": {
                "level": self.INGOTS_LOGGING_LEVEL,
            }
        }

    def build_logging_formatters_config(self) -> dict[str, dict]:
        return self.get_logging_formatters_config()

    def build_logging_handlers_config(self) -> dict[str, dict]:
        config = self.get_logging_handlers_config()
        for handler_config in config.values():
            handler_config.setdefault("class", "logging.StreamHandler")
            handler_config.setdefault("level", logging.NOTSET)
        return config

    def build_logging_filters_config(self) -> dict[str, dict]:
        return self.get_logging_filters_config()

    def build_logging_loggers_config(self) -> dict[str, dict]:
        config = self.get_logging_loggers_config()
        for name, log_config in config.items():
            log_config.setdefault("propagate", False)
            log_config.setdefault("handlers", ["default"])
        return config

    def build_logging_dict_config(self) -> dict:
        # https://docs.python.org
        # /3/library/logging.config.html#dictionary-schema-details
        config: dict = {
            "version": self.LOGGING_VERSION,
            "disable_existing_loggers": self.LOGGING_DISABLE_EXISTING_LOGGERS,
            "incremental": self.LOGGING_INCREMENTAL,
            "formatters": self.build_logging_formatters_config(),
            "handlers": self.build_logging_handlers_config(),
            "filters": self.build_logging_filters_config(),
            "loggers": self.build_logging_loggers_config(),
        }

        if self.LOGGING_ENABLE_ROOT_LOGGER:
            config["root"] = {
                "level": self.LOGGING_ROOT_LOGGER_LEVEL,
                "handlers": ["default"],
            }

        return config

    # endregion Logging
