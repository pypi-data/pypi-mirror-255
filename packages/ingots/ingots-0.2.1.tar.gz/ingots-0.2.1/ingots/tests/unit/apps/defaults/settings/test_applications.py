__all__ = ("SettingsApplicationTestCase",)

import typing as t
from unittest.mock import AsyncMock, Mock, patch

from ingots.apps.defaults.settings.applications import SettingsApplication
from ingots.apps.defaults.settings.units import SettingsUnit
from ingots.tests.unit.apps.defaults.settings.components import test_env

if t.TYPE_CHECKING:
    ...


TestedClassTypeVar = t.TypeVar("TestedClassTypeVar", bound=SettingsApplication)


class SettingsApplicationTestCase(
    test_env.EnvConfigsApplicationTestCase[TestedClassTypeVar],
    t.Generic[TestedClassTypeVar],
):
    """Contains tests for SettingsApplication class."""

    tst_cls: type[TestedClassTypeVar] = SettingsApplication

    def test_register_units_classes(self):
        """Checks the register_units_classes class method."""
        tst_res = self.tst_cls.register_units_classes()

        assert SettingsUnit in tst_res

    async def test_configure(self):
        """Checks the configure async method."""
        mock_settings = Mock()
        tst_obj = self.build_tst_obj()
        tst_obj.get_unit = AsyncMock(return_value=mock_settings)
        tst_obj.configure_logging = Mock()

        await tst_obj.configure()

        tst_obj.get_unit.assert_awaited_once_with(unit_cls=SettingsUnit)
        assert tst_obj.settings == mock_settings
        tst_obj.configure_logging.assert_called_once_with()

    def test_configure_logging(self):
        """Checks the configure_logging method."""
        mock_config = Mock()
        tst_obj = self.build_tst_obj()
        tst_obj.settings = Mock()
        tst_obj.settings.build_logging_dict_config = Mock(return_value=mock_config)

        with patch(f"{SettingsApplication.__module__}.dictConfig") as mock_dict_config:
            tst_obj.configure_logging()

        tst_obj.settings.build_logging_dict_config.assert_called_once_with()
        mock_dict_config.assert_called_once_with(mock_config)
