__all__ = ("JsonConfigsFileReaderTestCase",)

import json
import typing as t
from unittest.mock import Mock, patch

from ingots.apps.defaults.settings.components.readers.json import JsonConfigsFileReader
from ingots.tests.unit.apps.defaults.settings.components.readers import test_base

if t.TYPE_CHECKING:
    ...


TestedClassTypeVar = t.TypeVar("TestedClassTypeVar", bound=JsonConfigsFileReader)


class JsonConfigsFileReaderTestCase(
    test_base.BaseConfigsTextFileReaderTestCase[TestedClassTypeVar],
    t.Generic[TestedClassTypeVar],
):
    """Contains tests for JsonConfigsFileReader class."""

    tst_cls: type[TestedClassTypeVar] = JsonConfigsFileReader

    def test_parse_content(self):
        """Checks the parse_content method."""
        tst_obj = self.build_tst_obj()
        mock_content = Mock()
        mock_configs = Mock()

        with patch.object(json, "loads") as mock_loads:
            mock_loads.return_value = mock_configs
            tst_res = tst_obj.parse_content(content=mock_content)

        mock_loads.assert_called_once_with(mock_content)
        assert tst_res == mock_configs
