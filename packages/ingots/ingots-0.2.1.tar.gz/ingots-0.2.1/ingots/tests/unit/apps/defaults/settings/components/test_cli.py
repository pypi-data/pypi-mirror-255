__all__ = ("CliConfigsUpdatorComponentTestCase",)

import typing as t
from unittest.mock import Mock

from ingots.apps.defaults.settings.components.cli import CliConfigsUpdatorComponent
from ingots.tests.unit.apps.cli import test_components

if t.TYPE_CHECKING:
    ...


TestedClassTypeVar = t.TypeVar("TestedClassTypeVar", bound=CliConfigsUpdatorComponent)


class CliConfigsUpdatorComponentTestCase(
    test_components.CliComponentTestCase[TestedClassTypeVar],
    t.Generic[TestedClassTypeVar],
):
    """Contains tests for CliConfigsUpdatorComponent class."""

    tst_cls: type[TestedClassTypeVar] = CliConfigsUpdatorComponent

    async def test_configure(self):
        """Checks the configure async method."""
        mock_cli_config_info = Mock()
        mock_cli_config_info.name = "mock_name"
        mock_cli_config_info.raw_value = "mock_value"
        tst_obj = self.build_tst_obj()
        tst_obj.creating_params.app_configs_overrides = [mock_cli_config_info]
        tst_obj.unit.set_config_value = Mock()

        await tst_obj.configure()

        assert tst_obj.creating_params.app_configs_overrides == []
        tst_obj.unit.set_config_value.assert_called_once_with(
            name="mock_name", raw_value="mock_value"
        )

    async def test_shut_down(self):
        """Checks the shut_down async method."""
        tst_obj = self.build_tst_obj()

        tst_res = await tst_obj.shut_down()

        assert tst_res is None
