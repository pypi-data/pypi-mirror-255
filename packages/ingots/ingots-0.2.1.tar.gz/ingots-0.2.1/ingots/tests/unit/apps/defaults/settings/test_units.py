__all__ = ("SettingsUnitTestCase",)

import typing as t
from unittest.mock import AsyncMock, Mock, call

from ingots.apps.defaults.settings.commands import ListCommand
from ingots.apps.defaults.settings.components import (
    CliConfigsUpdatorComponent,
    EnvConfigsUpdatorComponent,
    FileConfigsUpdatorComponent,
)
from ingots.apps.defaults.settings.units import SettingsUnit
from ingots.tests.unit.apps.cli import test_units

if t.TYPE_CHECKING:
    ...


TestedClassTypeVar = t.TypeVar("TestedClassTypeVar", bound=SettingsUnit)


class SettingsUnitTestCase(
    test_units.CliUnitTestCase[TestedClassTypeVar],
    t.Generic[TestedClassTypeVar],
):
    """Contains tests for SettingsUnit class."""

    tst_cls: type[TestedClassTypeVar] = SettingsUnit

    def test_register_components_classes(self):
        """Checks the register_components_classes class method."""
        tst_res = self.tst_cls.register_components_classes()

        assert FileConfigsUpdatorComponent in tst_res
        assert CliConfigsUpdatorComponent in tst_res
        assert EnvConfigsUpdatorComponent in tst_res

    def test_register_commands_classes(self):
        """Checks the register_commands_classes class method."""
        tst_res = self.tst_cls.register_commands_classes()

        assert ListCommand in tst_res

    async def test_configure(self):
        """Checks the configure async method."""
        mock_file_updator_component = Mock()
        mock_env_updator_component = Mock()
        mock_cli_updator_component = Mock()
        tst_obj = self.build_tst_obj()
        tst_obj.get_component = AsyncMock(
            side_effect=[
                mock_file_updator_component,
                mock_env_updator_component,
                mock_cli_updator_component,
            ]
        )
        tst_obj.shut_down_component = AsyncMock()

        await tst_obj.configure()

        tst_obj.get_component.assert_has_awaits(
            [
                call(component_cls=FileConfigsUpdatorComponent),
                call(component_cls=EnvConfigsUpdatorComponent),
                call(component_cls=CliConfigsUpdatorComponent),
            ]
        )
        tst_obj.shut_down_component.assert_has_awaits(
            [
                call(component_cls=EnvConfigsUpdatorComponent),
                call(component_cls=CliConfigsUpdatorComponent),
            ]
        )

    def test_set_config_value(self):
        """Checks the set_config_value method."""
        tst_obj = self.build_tst_obj()
        tst_obj.TST_CONFIG = 12

        tst_obj.set_config_value(name="TST_CONFIG", raw_value="13")

        assert tst_obj.TST_CONFIG == 13

    def test_set_config_value_undefined(self):
        """Checks the set_config_value method for undefined config case."""
        tst_obj = self.build_tst_obj()
        tst_obj.TST_CONFIG = 12

        tst_obj.set_config_value(name="TST_UNDEFINED", raw_value="13")

        assert tst_obj.TST_CONFIG == 12

    def test_set_config_value_coerce_error(self):
        """Checks the set_config_value method for coercing error."""
        tst_obj = self.build_tst_obj()
        tst_obj.TST_CONFIG = 12

        tst_obj.set_config_value(name="TST_CONFIG", raw_value="wrong")

        assert tst_obj.TST_CONFIG == 12

    def test_get_configs(self):
        """Checks the get_configs method."""
        tst_obj = self.build_tst_obj()
        tst_obj.TST_CONFIG = 12
        tst_obj.tst_not_config = "value"

        tst_res = tst_obj.get_configs()

        assert ("TST_CONFIG", 12) in tst_res
        assert ("tst_not_config", "value") not in tst_res
