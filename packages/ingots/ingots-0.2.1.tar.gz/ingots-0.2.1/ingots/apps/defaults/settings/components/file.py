__all__ = ("FileConfigsUpdatorComponent",)

import logging
import os.path
import typing as t

from ingots.apps.cli import CliComponent
from ingots.utils.classes_builder import FinalClassesBuilder

from .readers import JsonConfigsFileReader, PyFileConfigsReader, TomlConfigsFileReader

if t.TYPE_CHECKING:
    from argparse import ArgumentParser

    from .applications import SettingsApplication  # noqa
    from .readers import BaseConfigsFileReader
    from .units import SettingsUnit  # noqa


logger = logging.getLogger(__name__)


class FileConfigsUpdatorComponent(CliComponent["SettingsApplication", "SettingsUnit"]):
    cli_name = "file_configs_updator"
    cli_description = "Provides configs updating from files."

    unit: "SettingsUnit"

    _final_readers_classes_map: dict[
        type["BaseConfigsFileReader"],
        type["BaseConfigsFileReader"],
    ]

    @classmethod
    def prepare_final_classes(cls):
        cls._final_readers_classes_map = FinalClassesBuilder["BaseConfigsFileReader"](
            container=cls,
            nested="Readers",
            base_classes=cls.register_readers_classes(),
            extensions=cls.register_readers_extensions(),
        ).build()

    @classmethod
    def register_readers_classes(
        cls,
    ) -> set[type["BaseConfigsFileReader"]]:
        return {PyFileConfigsReader, TomlConfigsFileReader, JsonConfigsFileReader}

    @classmethod
    def register_readers_extensions(
        cls,
    ) -> set[type["BaseConfigsFileReader"]]:
        return set()

    @classmethod
    def get_reader_cls(cls, ext: str) -> t.Optional[type["BaseConfigsFileReader"]]:
        found = [
            i
            for i in cls._final_readers_classes_map.values()
            if ext in i.supported_extensions
        ]
        try:
            return found[0]
        except IndexError:
            return None

    @classmethod
    def prepare_cli_parser(cls, parser: "ArgumentParser"):
        super().prepare_cli_parser(parser=parser)
        parser.add_argument(
            "--configs-file",
            dest="app_configs_file_paths",
            action="append",
            default=[],
            help="Specifies file names with configs for override.",
        )

    @property
    def cli_configs_file_paths(self) -> list[str]:
        return self.creating_params.app_configs_file_paths

    async def configure(self):
        for path in self.cli_configs_file_paths:
            try:
                self.update_configs_from_file(path=path)
            except Exception as err:
                logger.warning(
                    "Update configs error: %s. File: %r.",
                    err,
                    path,
                )

    async def shut_down(self): ...

    def update_configs_from_file(self, path: str):
        _, ext = os.path.splitext(path)
        ext = ext.strip(".")

        reader_cls = self.get_reader_cls(ext=ext)
        if not reader_cls:
            logger.warning("Unregistered file configs reader for extension: %s.", ext)
            return

        reader = reader_cls(settings=self.unit, path=path)
        logger.info(
            "Configs FileReader is created: %r. File: %s.",
            reader,
            path,
        )
        reader.run()
