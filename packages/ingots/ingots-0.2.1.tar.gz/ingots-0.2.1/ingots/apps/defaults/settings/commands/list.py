__all__ = (
    "ListCommand",
    "OutputMode",
)

import logging
import typing as t
from enum import Enum
from pprint import PrettyPrinter

from ingots.apps.cli import CliCommand

if t.TYPE_CHECKING:
    from argparse import ArgumentParser

    from ingots.apps.defaults.settings.units import SettingsUnit


logger = logging.getLogger(__name__)


class OutputMode(Enum):
    SIMPLE = "simple"
    PRETTY = "pretty"

    def __str__(self):
        return self.value


class ListCommand(CliCommand):
    cli_name = "list"
    cli_description = "Prints all project configs."

    unit: "SettingsUnit"

    @classmethod
    def prepare_cli_parser(cls, parser: "ArgumentParser"):
        super().prepare_cli_parser(parser=parser)
        parser.add_argument(
            "--config-prefix",
            dest="configs_prefixes",
            action="append",
            default=[],
            help="Specifies configs prefixes for filtering settings.",
        )
        parser.add_argument(
            "--output-mode",
            dest="configs_output_mode",
            type=OutputMode,
            choices=[*OutputMode],
            default=OutputMode.SIMPLE,
            help=f"Specifies output mode. By default: {OutputMode.SIMPLE}.",
        )

    @property
    def prefixes(self) -> list[str]:
        return self.creating_params.configs_prefixes

    @property
    def output_mode(self) -> "OutputMode":
        return self.creating_params.configs_output_mode

    async def run(self):
        print("-" * 80)
        print_method = getattr(self, f"print_{self.output_mode.value}")
        configs = self.extract_configs()
        print_method(configs=configs)
        print("-" * 80)

    def extract_configs(self) -> list[tuple[str, t.Any]]:
        if not self.prefixes:
            return self.unit.get_configs()

        configs = []
        for name, value in self.unit.get_configs():
            for prefix in self.prefixes:
                if name.startswith(prefix):
                    configs.append((name, value))
        return configs

    def print_simple(self, configs: list[tuple[str, t.Any]]):
        for name, value in configs:
            print(f"{name} = {value}")

    def print_pretty(self, configs: list[tuple[str, t.Any]]):
        pp = PrettyPrinter(indent=4)
        for name, value in configs:
            print(f"{name} = {pp.pformat(value)}")
