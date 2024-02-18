__all__ = ("CliApplicationRunnerTestCase",)

import asyncio
import typing as t
from unittest.mock import AsyncMock, Mock, patch

from ingots.apps.cli.runners import CliApplicationRunner
from ingots.tests.unit.apps.base import test_runners

if t.TYPE_CHECKING:
    ...


TestedClassTypeVar = t.TypeVar("TestedClassTypeVar", bound=CliApplicationRunner)


class CliApplicationRunnerTestCase(
    test_runners.BaseApplicationRunnerTestCase[TestedClassTypeVar],
    t.Generic[TestedClassTypeVar],
):
    """Contains tests for CliApplicationRunner class."""

    tst_cls: type[TestedClassTypeVar] = CliApplicationRunner

    def test_prepare_creating_params(self):
        """Checks the prepare_creating_params method."""
        mock_namespace = Mock()
        tst_obj = self.build_tst_obj()
        tst_obj.parse_cli_arguments = Mock(return_value=mock_namespace)

        tst_res = tst_obj.prepare_creating_params()

        assert tst_res == mock_namespace

    def test_get_cli_parser_creating_parameters(self):
        """Checks the get_cli_parser_creating_parameters method."""
        mock_creating_params = Mock()
        tst_obj = self.build_tst_obj()
        tst_obj.application_cls.get_cli_parser_creating_parameters = Mock(
            return_value=mock_creating_params
        )

        tst_res = tst_obj.get_cli_parser_creating_parameters()

        assert tst_res == mock_creating_params
        mock_app_cls = tst_obj.application_cls
        mock_app_cls.get_cli_parser_creating_parameters.assert_called_once_with()

    def test_prepare_cli_parser(self):
        """Checks the prepare_cli_parser method."""
        mock_parser = Mock()
        mock_parser.add_argument = Mock()
        tst_obj = self.build_tst_obj()
        tst_obj.application_cls.prepare_cli_parser = Mock()
        tst_obj.prepare_cli_parser_from_components_classes = Mock()
        tst_obj.prepare_cli_parser_from_units_classes = Mock()

        tst_obj.prepare_cli_parser(parser=mock_parser)

        mock_parser.add_argument.assert_called_once_with(
            "--debug-mode",
            dest="runner_is_debug_mode",
            action="store_true",
            help="Flag for running application in debug mode",
        )
        tst_obj.application_cls.prepare_cli_parser.assert_called_once_with(
            parser=mock_parser
        )
        tst_obj.prepare_cli_parser_from_components_classes.assert_called_once_with(
            parser=mock_parser
        )
        tst_obj.prepare_cli_parser_from_units_classes.assert_called_once_with(
            parser=mock_parser
        )

    def test_prepare_cli_parser_from_components_classes(self):
        """Checks the prepare_cli_parser_from_components_classes method."""
        mock_component_cls = Mock()
        mock_component_cls.prepare_cli_parser = Mock()
        mock_unit_cls = Mock()
        mock_unit_cls.get_components_classes = Mock(return_value=[mock_component_cls])
        tst_obj = self.build_tst_obj()
        tst_obj.application_cls.get_units_classes = Mock(return_value=[mock_unit_cls])
        mock_parser = Mock()

        tst_obj.prepare_cli_parser_from_components_classes(parser=mock_parser)

        tst_obj.application_cls.get_units_classes.assert_called_once_with()
        mock_unit_cls.get_components_classes.assert_called_once_with()
        mock_component_cls.prepare_cli_parser.assert_called_once_with(
            parser=mock_parser
        )

    def test_prepare_cli_parser_from_units_classes(self):
        """Checks the prepare_cli_parser_from_units_classes method."""
        mock_units_subparsers_manager = Mock()
        mock_unit_cls = Mock()
        tst_obj = self.build_tst_obj()
        tst_obj.build_units_cli_subparsers_manager = Mock(
            return_value=mock_units_subparsers_manager
        )
        tst_obj.application_cls.get_units_classes = Mock(return_value=[mock_unit_cls])
        tst_obj.prepare_cli_parser_from_unit_cls = Mock()
        mock_parser = Mock()

        tst_obj.prepare_cli_parser_from_units_classes(parser=mock_parser)

        tst_obj.build_units_cli_subparsers_manager.assert_called_once_with(
            parser=mock_parser
        )
        tst_obj.application_cls.get_units_classes.assert_called_once_with()
        tst_obj.prepare_cli_parser_from_unit_cls.assert_called_once_with(
            subparsers_manager=mock_units_subparsers_manager, unit_cls=mock_unit_cls
        )

    def test_build_units_cli_subparsers_manager(self):
        """Checks the build_units_cli_subparsers_manager method."""
        tst_obj = self.build_tst_obj()
        mock_units_subparsers_manager = Mock()
        mock_parser = Mock()
        mock_parser.add_subparsers = Mock(return_value=mock_units_subparsers_manager)

        tst_res = tst_obj.build_units_cli_subparsers_manager(parser=mock_parser)

        assert tst_res == mock_units_subparsers_manager
        mock_parser.add_subparsers.assert_called_once_with(
            title="Registered units",
            dest="runner_unit_name",
            required=True,
        )

    def test_prepare_cli_parser_from_unit_cls(self):
        """Checks the prepare_cli_parser_from_unit_cls method."""
        tst_obj = self.build_tst_obj()
        tst_obj.prepare_cli_parser_from_unit_commands_classes = Mock()
        mock_unit_cls = Mock()
        mock_unit_cls.cli_name = "test_unit_cli_name"
        mock_unit_cls.get_cli_parser_creating_parameters = Mock(
            return_value={"tst_param": "tst-value"}
        )
        mock_unit_cls.prepare_cli_parser = Mock()
        mock_unit_parser = Mock()
        mock_subparsers_manager = Mock()
        mock_subparsers_manager.add_parser = Mock(return_value=mock_unit_parser)

        tst_obj.prepare_cli_parser_from_unit_cls(
            subparsers_manager=mock_subparsers_manager, unit_cls=mock_unit_cls
        )

        mock_unit_cls.get_cli_parser_creating_parameters.assert_called_once_with()
        mock_subparsers_manager.add_parser.assert_called_once_with(
            "test_unit_cli_name", tst_param="tst-value"
        )
        mock_unit_cls.prepare_cli_parser.assert_called_once_with(
            parser=mock_unit_parser
        )
        tst_obj.prepare_cli_parser_from_unit_commands_classes.assert_called_once_with(
            parser=mock_unit_parser, unit_cls=mock_unit_cls
        )

    def test_prepare_cli_parser_from_unit_commands_classes(self):
        """Checks the prepare_cli_parser_from_unit_commands_classes method."""
        mock_commands_subparser_manager = Mock()
        tst_obj = self.build_tst_obj()
        tst_obj.build_commands_cli_subparsers_manager = Mock(
            return_value=mock_commands_subparser_manager
        )
        tst_obj.prepare_cli_parser_from_command_cls = Mock()
        mock_command_cls = Mock()
        mock_unit_cls = Mock()
        mock_unit_cls.get_commands_classes = Mock(return_value=[mock_command_cls])
        mock_parser = Mock()

        tst_obj.prepare_cli_parser_from_unit_commands_classes(
            parser=mock_parser, unit_cls=mock_unit_cls
        )

        tst_obj.build_commands_cli_subparsers_manager.assert_called_once_with(
            parser=mock_parser
        )
        mock_unit_cls.get_commands_classes.assert_called_once_with()
        tst_obj.prepare_cli_parser_from_command_cls.assert_called_once_with(
            subparsers_manager=mock_commands_subparser_manager,
            command_cls=mock_command_cls,
        )

    def test_prepare_cli_parser_from_command_cls(self):
        """Checks the prepare_cli_parser_from_command_cls method."""
        tst_obj = self.build_tst_obj()
        mock_command_parser = Mock()
        mock_subparsers_manager = Mock()
        mock_subparsers_manager.add_parser = Mock(return_value=mock_command_parser)
        mock_command_cls = Mock()
        mock_command_cls.cli_name = "test_command_cli_name"
        mock_command_cls.get_cli_parser_creating_parameters = Mock(
            return_value={"tst_param": "tst-value"}
        )
        mock_command_cls.prepare_cli_parser = Mock()

        tst_obj.prepare_cli_parser_from_command_cls(
            subparsers_manager=mock_subparsers_manager,
            command_cls=mock_command_cls,
        )

        mock_command_cls.get_cli_parser_creating_parameters.assert_called_once_with()
        mock_subparsers_manager.add_parser.assert_called_once_with(
            "test_command_cli_name", tst_param="tst-value"
        )
        mock_command_cls.prepare_cli_parser.assert_called_once_with(
            parser=mock_command_parser
        )

    def test_build_commands_cli_subparsers_manager(self):
        """Checks the build_commands_cli_subparsers_manager method."""
        tst_obj = self.build_tst_obj()
        mock_commands_subparsers_manager = Mock()
        mock_parser = Mock()
        mock_parser.add_subparsers = Mock(return_value=mock_commands_subparsers_manager)

        tst_res = tst_obj.build_commands_cli_subparsers_manager(parser=mock_parser)

        assert tst_res == mock_commands_subparsers_manager
        mock_parser.add_subparsers.assert_called_once_with(
            title="Registered commands",
            dest="runner_command_name",
            required=True,
        )

    def test_is_debug_mode(self):
        """Checks is_debug_mode property."""
        tst_obj = self.build_tst_obj()
        tst_obj.creating_params = Mock(runner_is_debug_mode=True)

        assert tst_obj.is_debug_mode is True

    def test_unit_name(self):
        """Checks unit_name property."""
        tst_obj = self.build_tst_obj()
        tst_obj.creating_params = Mock(runner_unit_name="tst_unit")

        assert tst_obj.unit_name == "tst_unit"

    def test_command_name(self):
        """Checks command_name property."""
        tst_obj = self.build_tst_obj()
        tst_obj.creating_params = Mock(runner_command_name="tst_command")

        assert tst_obj.command_name == "tst_command"

    def test_run(self):
        """Checks the run method."""
        tst_obj = self.build_tst_obj()
        tst_obj.run_workflow = Mock()

        with patch("sys.exit") as mock_sys_exit:
            tst_obj.run()

        tst_obj.run_workflow.assert_called_once_with()
        assert tst_obj.exit_code == 0
        mock_sys_exit.assert_called_once_with(0)

    def test_run_error(self):
        """Checks the run method for catching exception case."""
        tst_obj = self.build_tst_obj()
        tst_obj.run_workflow = Mock(side_effect=Exception("Test"))

        with patch("sys.exit") as mock_sys_exit:
            tst_obj.run()

        tst_obj.run_workflow.assert_called_once_with()
        assert tst_obj.exit_code == 1
        mock_sys_exit.assert_called_once_with(1)

    def test_run_workflow(self):
        """Checks the run_workflow method."""
        mock_creating_params = Mock()
        mock_creating_params.runner_is_debug_mode = True
        mock_application = Mock()
        mock_async_workflow_coro = Mock()
        tst_obj = self.build_tst_obj()
        tst_obj.prepare_creating_params = Mock(return_value=mock_creating_params)
        tst_obj.create_application = Mock(return_value=mock_application)
        tst_obj.prepare_asyncio = Mock()
        tst_obj.run_async_workflow = Mock(return_value=mock_async_workflow_coro)

        with patch.object(asyncio, "run") as mock_run:
            tst_obj.run_workflow()

        tst_obj.prepare_creating_params.assert_called_once_with()
        assert tst_obj.creating_params == mock_creating_params
        tst_obj.create_application.assert_called_once_with()
        assert tst_obj.application == mock_application
        tst_obj.prepare_asyncio.assert_called_once_with()
        tst_obj.run_async_workflow.assert_called_once_with()
        mock_run.assert_called_once_with(mock_async_workflow_coro, debug=True)

    def test_prepare_asyncio(self):
        """Checks the prepare_asyncio method."""
        tst_obj = self.build_tst_obj()
        tst_res = tst_obj.prepare_asyncio()
        assert tst_res is None

    async def test_run_async_workflow(self):
        """Checks the run_async_workflow async method."""
        tst_obj = self.build_tst_obj()
        tst_obj.run_command_workflow = AsyncMock()
        tst_obj.application = Mock()
        tst_obj.application.configure = AsyncMock()
        tst_obj.application.shut_down = AsyncMock()

        await tst_obj.run_async_workflow()

        tst_obj.application.configure.assert_awaited_once_with()
        tst_obj.run_command_workflow.assert_awaited_once_with()
        tst_obj.application.shut_down.assert_awaited_once_with()

    async def test_run_async_workflow_error(self):
        """Checks the run_async_workflow async method for raising error case."""
        tst_obj = self.build_tst_obj()
        tst_obj.run_command_workflow = AsyncMock()
        tst_obj.application = Mock()
        tst_obj.application.configure = AsyncMock(side_effect=Exception("Test"))
        tst_obj.application.shut_down = AsyncMock()

        with self.assertRaises(Exception):
            await tst_obj.run_async_workflow()

        tst_obj.application.configure.assert_awaited_once_with()
        tst_obj.run_command_workflow.assert_not_awaited()
        tst_obj.application.shut_down.assert_awaited_once_with()

    async def test_build_command(self):
        """Checks the build_command async method."""
        mock_base_command_cls = Mock(cli_name="tst_command")
        mock_base_unit_cls = Mock(cli_name="tst_unit")
        mock_command = Mock()
        mock_unit = Mock()
        mock_unit.get_base_command_cls_by_cli_name = Mock(
            return_value=mock_base_command_cls
        )
        mock_unit.create_command = Mock(return_value=mock_command)
        tst_obj = self.build_tst_obj()
        tst_obj.creating_params = Mock(
            runner_unit_name="tst_unit", runner_command_name="tst_command"
        )
        tst_obj.application = Mock()
        tst_obj.application_cls.get_base_unit_cls_by_cli_name = Mock(
            return_value=mock_base_unit_cls
        )
        tst_obj.application.get_unit = AsyncMock(return_value=mock_unit)

        tst_res = await tst_obj.build_command()

        assert tst_res == mock_command
        tst_obj.application_cls.get_base_unit_cls_by_cli_name.assert_called_once_with(
            name="tst_unit"
        )
        tst_obj.application.get_unit.assert_awaited_once_with(
            unit_cls=mock_base_unit_cls
        )
        mock_unit.get_base_command_cls_by_cli_name.assert_called_once_with(
            name="tst_command"
        )
        mock_unit.create_command.assert_called_once_with(
            command_cls=mock_base_command_cls
        )

    def test_run_command_tack_done_callback(self):
        """Checks the run_command_tack_done_callback."""
        mock_future = Mock()
        mock_future.done = Mock(return_value=False)
        mock_future.set_result = Mock()
        mock_future.set_exception = Mock()
        tst_obj = self.build_tst_obj()
        tst_obj._running_command_task_future = mock_future
        mock_result = Mock()
        mock_task = Mock()
        mock_task.result = Mock(return_value=mock_result)
        mock_task.exception = Mock(return_value=None)

        tst_obj.run_command_tack_done_callback(task=mock_task)

        mock_future.done.assert_called_once_with()
        mock_task.exception.assert_called_once_with()
        mock_future.set_exception.assert_not_called()
        mock_task.result.assert_called_once_with()
        mock_future.set_result.assert_called_once_with(mock_result)

    def test_run_command_tack_done_callback_future_completed(self):
        """Checks the run_command_tack_done_callback for future completed case."""
        mock_future = Mock()
        mock_future.done = Mock(return_value=True)
        mock_future.set_result = Mock()
        tst_obj = self.build_tst_obj()
        tst_obj._running_command_task_future = mock_future
        mock_result = Mock()
        mock_task = Mock()
        mock_task.result = Mock(return_value=mock_result)

        tst_obj.run_command_tack_done_callback(task=mock_task)

        mock_future.done.assert_called_once_with()
        mock_task.result.assert_not_called()
        mock_future.set_result.assert_not_called()

    def test_handle_sigint_sigterm_callback(self):
        """Checks the handle_sigint_sigterm_callback method."""
        mock_future = Mock()
        mock_future.done = Mock(return_value=False)
        mock_future.set_exception = Mock()
        tst_obj = self.build_tst_obj()
        tst_obj._running_command_task_future = mock_future

        tst_obj.handle_sigint_sigterm_callback("SIGTEST")

        mock_future.done.assert_called_once_with()
        mock_future.set_exception.assert_called_once()

    def test_handle_sigint_sigterm_callback_future_completed(self):
        """
        Checks the handle_sigint_sigterm_callback method for completed future case.
        """
        mock_future = Mock()
        mock_future.done = Mock(return_value=True)
        mock_future.set_result = Mock()
        tst_obj = self.build_tst_obj()
        tst_obj._running_command_task_future = mock_future

        tst_obj.handle_sigint_sigterm_callback("SIGTEST")

        mock_future.done.assert_called_once_with()
        mock_future.set_result.assert_not_called()
