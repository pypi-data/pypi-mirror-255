__all__ = (
    "BaseConfigsFileReaderTestCase",
    "BaseConfigsTextFileReaderTestCase",
)

import typing as t
from unittest.mock import Mock, patch

from ingots.apps.defaults.settings.components.readers.base import (
    BaseConfigsFileReader,
    BaseConfigsTextFileReader,
)
from ingots.tests import helpers

if t.TYPE_CHECKING:
    ...


BaseConfigsFileReaderTypeVar = t.TypeVar(
    "BaseConfigsFileReaderTypeVar", bound=BaseConfigsFileReader
)


class BaseConfigsFileReaderTestCase(
    helpers.ClassTestingTestCase[BaseConfigsFileReaderTypeVar],
    t.Generic[BaseConfigsFileReaderTypeVar],
):
    """Contains tests for BaseConfigsFileReader class."""

    tst_cls: type[BaseConfigsFileReaderTypeVar] = BaseConfigsFileReader

    def get_tst_obj_init_params(self, **kwargs) -> dict:
        kwargs.setdefault("settings", Mock())
        kwargs.setdefault("path", "path/to/configs/file.tst")
        return super().get_tst_obj_init_params(**kwargs)

    def test_init(self):
        """Checks the __init__ method."""
        mock_settings = Mock()

        tst_obj = self.build_tst_obj(settings=mock_settings, path="mock_file.ext")

        assert tst_obj.settings == mock_settings
        assert tst_obj.path == "mock_file.ext"

    def test_run(self):
        """Checks the run method."""
        mock_configs = Mock()
        tst_obj = self.build_tst_obj()
        tst_obj.load_configs = Mock(return_value=mock_configs)
        tst_obj.apply_configs = Mock()

        tst_obj.run()

        tst_obj.load_configs.assert_called_once_with()
        tst_obj.apply_configs.assert_called_once_with(configs=mock_configs)

    def test_load_configs(self):
        """Checks the load_configs method."""
        tst_obj = self.build_tst_obj()

        with self.assertRaises(NotImplementedError):
            tst_obj.load_configs()


BaseConfigsTextFileReaderTypeVar = t.TypeVar(
    "BaseConfigsTextFileReaderTypeVar", bound=BaseConfigsTextFileReader
)


class BaseConfigsTextFileReaderTestCase(
    BaseConfigsFileReaderTestCase[BaseConfigsTextFileReaderTypeVar],
    t.Generic[BaseConfigsTextFileReaderTypeVar],
):
    """Contains tests for BaseConfigsTextFileReader class."""

    tst_cls: type[BaseConfigsTextFileReaderTypeVar] = BaseConfigsTextFileReader

    def test_load_configs(self):
        """Checks the load_configs method."""
        mock_content = Mock()
        tst_obj = self.build_tst_obj()
        tst_obj.load_content = Mock(return_value=mock_content)
        tst_obj.parse_content = Mock()

        tst_obj.load_configs()

        tst_obj.load_content.assert_called_once_with()
        tst_obj.parse_content.assert_called_once_with(content=mock_content)

    def test_load_content(self):
        """Checks the load_content method."""
        tst_obj = self.build_tst_obj()
        mock_content = Mock()
        mock_fd = Mock()
        mock_fd.read = Mock(return_value=mock_content)
        mock_fd_cm = Mock()
        mock_fd_cm.__enter__ = Mock(return_value=mock_fd)
        mock_fd_cm.__exit__ = Mock()

        with patch("builtins.open") as mock_open:
            mock_open.return_value = mock_fd_cm
            tst_res = tst_obj.load_content()

        mock_open.assert_called_once_with(tst_obj.path, mode=tst_obj.file_mode)
        mock_fd_cm.__enter__.assert_called_once_with()
        mock_fd.read.assert_called_once_with()
        mock_fd_cm.__exit__.assert_called_once_with(None, None, None)
        assert tst_res == mock_content

    def test_parse_content(self):
        """Checks the parse_content method."""
        tst_obj = self.build_tst_obj()

        with self.assertRaises(NotImplementedError):
            tst_obj.parse_content(content=Mock())
