__all__ = ("TomlConfigsFileReader",)

import logging
import tomllib
import typing as t

from .base import BaseConfigsTextFileReader

if t.TYPE_CHECKING:
    ...


logger = logging.getLogger(__name__)


class TomlConfigsFileReader(BaseConfigsTextFileReader):
    supported_extensions = ["toml"]

    def parse_content(self, content: str) -> dict[str, t.Any]:
        configs = tomllib.loads(content)
        return configs
