__all__ = ("PyFileConfigsReader",)

import logging
import os.path
import types
import typing as t
from importlib import import_module

from .base import BaseConfigsFileReader

if t.TYPE_CHECKING:
    ...


logger = logging.getLogger(__name__)


class PyFileConfigsReader(BaseConfigsFileReader):
    supported_extensions = ["py"]

    def load_configs(self) -> dict[str, t.Any]:
        name, package = self.build_name_package()
        py_module = import_module(name=name, package=package)
        return self.extract_configs(module=py_module)

    def build_name_package(self) -> tuple[str, str]:
        dir_path = os.path.dirname(self.path)
        if dir_path:
            package_parts = dir_path.split(os.path.sep)
        else:
            package_parts = []

        file_name, _ = os.path.splitext(os.path.basename(self.path))
        if package_parts:
            file_name = f".{file_name}"

        return file_name, ".".join(package_parts)

    def extract_configs(self, module: types.ModuleType) -> dict[str, t.Any]:
        return {k: v for k, v in module.__dict__.items() if k.upper() == k}
