__all__ = ("ListCommandTestCase",)

import typing as t
from unittest.mock import Mock

from ingots.apps.defaults.settings.commands.list import ListCommand, OutputMode
from ingots.tests.unit.apps.cli import test_commands

if t.TYPE_CHECKING:
    ...


TestedClassTypeVar = t.TypeVar("TestedClassTypeVar", bound=ListCommand)


class ListCommandTestCase(
    test_commands.CliCommandTestCase[TestedClassTypeVar],
    t.Generic[TestedClassTypeVar],
):
    """Contains tests for ListCommand class."""

    tst_cls: type[TestedClassTypeVar] = ListCommand

    async def test_run(self):
        """Checks the run async method."""
        mock_configs = Mock()
        tst_obj = self.build_tst_obj()
        tst_obj.creating_params.configs_output_mode = OutputMode.SIMPLE
        tst_obj.extract_configs = Mock(return_value=mock_configs)
        tst_obj.print_simple = Mock()

        await tst_obj.run()

        tst_obj.extract_configs.assert_called_once_with()
        tst_obj.print_simple.assert_called_once_with(configs=mock_configs)
