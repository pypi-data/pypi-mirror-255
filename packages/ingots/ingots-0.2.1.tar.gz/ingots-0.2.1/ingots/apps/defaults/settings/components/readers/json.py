__all__ = ("JsonConfigsFileReader",)

import json
import logging
import typing as t

from .base import BaseConfigsTextFileReader

if t.TYPE_CHECKING:
    ...


logger = logging.getLogger(__name__)


class JsonConfigsFileReader(BaseConfigsTextFileReader):
    supported_extensions = ["json"]

    def parse_content(self, content: str) -> dict[str, t.Any]:
        configs = json.loads(content)
        return configs
