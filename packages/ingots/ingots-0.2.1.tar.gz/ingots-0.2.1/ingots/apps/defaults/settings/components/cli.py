__all__ = ("CliConfigsUpdatorComponent",)

import logging
import typing as t
from argparse import ArgumentTypeError
from dataclasses import dataclass

from ingots.apps.cli import CliComponent
from ingots.utils import delimiters

if t.TYPE_CHECKING:
    from argparse import ArgumentParser

    from ingots.apps.cli import CliApplication, CliUnit  # noqa

    from .units import SettingsUnit  # noqa


logger = logging.getLogger(__name__)


@dataclass
class CliConfigInfo:
    name: str
    raw_value: str


class CliConfigsUpdatorComponent(CliComponent["CliApplication", "SettingsUnit"]):
    cli_name = "cli-configs-updator"
    cli_description = "Provides configs updating from CLI arguments."
    cli_config_delimiter: str = delimiters.EQUAL

    unit: "SettingsUnit"

    @classmethod
    def prepare_final_classes(cls): ...

    @classmethod
    def prepare_cli_parser(cls, parser: "ArgumentParser"):
        super().prepare_cli_parser(parser=parser)
        parser.add_argument(
            "--config",
            dest="app_configs_overrides",
            action="append",
            default=[],
            help=(
                f"Specifies configs overrides via CLI arguments."
                f" Format: <CONFIG>{cls.cli_config_delimiter}<value>."
            ),
            type=cls.validate_cli_config_value,
        )

    @classmethod
    def validate_cli_config_value(cls, cli_value: str) -> "CliConfigInfo":
        try:
            name, raw_value = cli_value.split(cls.cli_config_delimiter, maxsplit=1)
        except ValueError:
            logger.error("Malformed value for CLI '--config' argument: %s.", cli_value)
            raise ArgumentTypeError(
                f"Malformed value for --config argument: {cli_value}"
            )
        else:
            return CliConfigInfo(name=name, raw_value=raw_value)

    @property
    def cli_configs(self) -> list["CliConfigInfo"]:
        return self.creating_params.app_configs_overrides

    async def configure(self):
        logger.info("CLI. Configs overrides: %s.", self.cli_configs)
        while self.cli_configs:
            cli_config = self.cli_configs.pop()
            self.unit.set_config_value(
                name=cli_config.name, raw_value=cli_config.raw_value
            )

    async def shut_down(self): ...
