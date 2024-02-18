__all__ = (
    "EnvConfigsUpdatorComponentTestCase",
    "EnvConfigsApplicationTestCase",
)

import typing as t
from unittest.mock import Mock

from ingots.apps.defaults.settings.components.env import (
    EnvConfigsApplication,
    EnvConfigsUpdatorComponent,
)
from ingots.tests.unit.apps.cli import test_applications, test_components

if t.TYPE_CHECKING:
    ...


TestedAppClassTypeVar = t.TypeVar("TestedAppClassTypeVar", bound=EnvConfigsApplication)


class EnvConfigsApplicationTestCase(
    test_applications.CliApplicationTestCase[TestedAppClassTypeVar],
    t.Generic[TestedAppClassTypeVar],
):
    """Contains tests for EnvConfigsApplication class."""

    tst_cls: type[TestedAppClassTypeVar] = EnvConfigsApplication


TestedClassTypeVar = t.TypeVar("TestedClassTypeVar", bound=EnvConfigsUpdatorComponent)


class EnvConfigsUpdatorComponentTestCase(
    test_components.CliComponentTestCase[TestedClassTypeVar],
    t.Generic[TestedClassTypeVar],
):
    """Contains tests for EnvConfigsUpdatorComponent class."""

    tst_cls: type[TestedClassTypeVar] = EnvConfigsUpdatorComponent

    async def test_configure(self):
        """Checks the configure async method."""
        tst_obj = self.build_tst_obj()
        tst_obj.find_suitable_configs_overrides = Mock(
            return_value={"mock_name": "mock_value"}
        )
        tst_obj.unit.set_config_value = Mock()

        await tst_obj.configure()

        tst_obj.find_suitable_configs_overrides.assert_called_once_with()
        tst_obj.unit.set_config_value.assert_called_once_with(
            name="mock_name", raw_value="mock_value"
        )

    async def test_shut_down(self):
        """Checks the shut_down async method."""
        tst_obj = self.build_tst_obj()

        tst_res = await tst_obj.shut_down()

        assert tst_res is None
