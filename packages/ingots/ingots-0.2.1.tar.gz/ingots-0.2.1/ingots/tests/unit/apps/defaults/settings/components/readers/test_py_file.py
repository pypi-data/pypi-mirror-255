__all__ = ("PyFileConfigsReaderTestCase",)

import typing as t
from unittest.mock import Mock, patch

from ingots.apps.defaults.settings.components.readers.py_file import PyFileConfigsReader
from ingots.tests.unit.apps.defaults.settings.components.readers import test_base

if t.TYPE_CHECKING:
    ...


TestedClassTypeVar = t.TypeVar("TestedClassTypeVar", bound=PyFileConfigsReader)


class PyFileConfigsReaderTestCase(
    test_base.BaseConfigsFileReaderTestCase[TestedClassTypeVar],
    t.Generic[TestedClassTypeVar],
):
    """Contains tests for PyFileConfigsReader class."""

    tst_cls: type[TestedClassTypeVar] = PyFileConfigsReader

    def test_load_configs(self):
        """Checks the load_configs method."""
        mock_py_module = Mock()
        mock_configs = Mock()
        tst_obj = self.build_tst_obj()
        tst_obj.build_name_package = Mock(return_value=(".tst_file", "path.to.package"))
        tst_obj.extract_configs = Mock(return_value=mock_configs)

        with patch(
            f"{PyFileConfigsReader.__module__}.import_module"
        ) as mock_import_module:
            mock_import_module.return_value = mock_py_module
            tst_res = tst_obj.load_configs()

        tst_obj.build_name_package.assert_called_once_with()
        mock_import_module.assert_called_once_with(
            name=".tst_file", package="path.to.package"
        )
        tst_obj.extract_configs.assert_called_once_with(module=mock_py_module)
        assert tst_res == mock_configs
