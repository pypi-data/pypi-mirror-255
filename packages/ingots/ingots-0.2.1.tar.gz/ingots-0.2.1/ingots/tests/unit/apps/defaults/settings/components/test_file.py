__all__ = ("FileConfigsUpdatorComponentTestCase",)

import typing as t
from unittest.mock import Mock

from ingots.apps.defaults.settings.components.file import FileConfigsUpdatorComponent
from ingots.tests.unit.apps.cli import test_components

if t.TYPE_CHECKING:
    ...


TestedClassTypeVar = t.TypeVar("TestedClassTypeVar", bound=FileConfigsUpdatorComponent)


class FileConfigsUpdatorComponentTestCase(
    test_components.CliComponentTestCase[TestedClassTypeVar],
    t.Generic[TestedClassTypeVar],
):
    """Contains tests for FileConfigsUpdatorComponent class."""

    tst_cls: type[TestedClassTypeVar] = FileConfigsUpdatorComponent

    async def test_configure(self):
        """Checks the configure async method."""
        tst_obj = self.build_tst_obj()
        tst_obj.creating_params.app_configs_file_paths = ["mock_file.ext"]
        tst_obj.update_configs_from_file = Mock()

        await tst_obj.configure()

        tst_obj.update_configs_from_file.assert_called_once_with(path="mock_file.ext")

    async def test_shut_down(self):
        """Checks the shut_down async method."""
        tst_obj = self.build_tst_obj()

        tst_res = await tst_obj.shut_down()

        assert tst_res is None
