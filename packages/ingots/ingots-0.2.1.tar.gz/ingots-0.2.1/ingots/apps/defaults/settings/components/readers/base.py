__all__ = (
    "BaseConfigsFileReader",
    "BaseConfigsTextFileReader",
)

import logging
import typing as t

from ingots.utils.classes_builder import BuildClassInterface

if t.TYPE_CHECKING:
    from ingots.apps.defaults.settings.units import SettingsUnit


logger = logging.getLogger(__name__)


class BaseConfigsFileReader(BuildClassInterface):
    build_class_extensions_order = 5
    supported_extensions: list[str]

    def __init__(self, settings: "SettingsUnit", path: str):
        self.settings = settings
        self.path = path

    def run(self):
        configs = self.load_configs()
        logger.info(
            "FILE: %s. Configs overrides: %s.",
            self.path,
            configs,
        )
        self.apply_configs(configs=configs)

    def load_configs(self) -> dict[str, t.Any]:
        raise NotImplementedError(f"{self.__class__.__name__}.load_configs")

    def apply_configs(self, configs: dict[str, t.Any]):
        for name, raw_value in configs.items():
            self.apply_config(name=name, raw_value=raw_value)

    def apply_config(self, name: str, raw_value: t.Any):
        self.settings.set_config_value(name=name, raw_value=raw_value)


class BaseConfigsTextFileReader(BaseConfigsFileReader):
    file_mode = "rt"

    def load_configs(self) -> dict[str, t.Any]:
        content = self.load_content()
        logger.debug(
            "Reader: %r. File: %s. Content: %s.",
            self,
            self.path,
            content,
        )
        return self.parse_content(content=content)

    def load_content(self) -> str:
        with open(self.path, mode=self.file_mode) as fd:
            content = fd.read()
        return content

    def parse_content(self, content: str) -> dict[str, t.Any]:
        raise NotImplementedError(f"{self.__class__.__name__}.parse_content")
