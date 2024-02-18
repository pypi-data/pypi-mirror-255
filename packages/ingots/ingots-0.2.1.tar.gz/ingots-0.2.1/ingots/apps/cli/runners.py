__all__ = ("CliApplicationRunner",)

import asyncio
import logging
import signal
import sys
import typing as t

from ingots.apps.base import BaseApplicationRunner
from ingots.utils.cli import Cli

if t.TYPE_CHECKING:
    from argparse import ArgumentParser, Namespace, _SubParsersAction

    from .applications import CliApplication
    from .commands import CliCommand
    from .units import CliUnit


logger = logging.getLogger(__name__)

ApplicationTypeVar = t.TypeVar("ApplicationTypeVar", bound="CliApplication")


class CliApplicationRunner(
    Cli,
    BaseApplicationRunner["Namespace", ApplicationTypeVar],
    t.Generic[ApplicationTypeVar],
):
    command_cancellation_timeout: int = 5

    _run_command_task: "asyncio.Task"
    _running_command_task_future: "asyncio.Future"

    def __init__(self, cli_args: t.Optional[list[str]] = None, **kwargs):
        super().__init__(**kwargs)
        self.cli_args = cli_args
        self.exit_code = 0
        self.command: t.Optional["CliCommand"] = None

    def prepare_creating_params(self) -> "Namespace":
        return self.parse_cli_arguments(args=self.cli_args)

    def get_cli_parser_creating_parameters(self) -> dict:
        return self.application_cls.get_cli_parser_creating_parameters()

    def prepare_cli_parser(self, parser: "ArgumentParser"):
        parser.add_argument(
            "--debug-mode",
            dest="runner_is_debug_mode",
            action="store_true",
            help="Flag for running application in debug mode",
        )
        logger.debug(
            "CLI ArgumentParser: %r. Prepare from: %r.", parser, self.application_cls
        )
        self.application_cls.prepare_cli_parser(parser=parser)
        self.prepare_cli_parser_from_components_classes(parser=parser)
        self.prepare_cli_parser_from_units_classes(parser=parser)

    def prepare_cli_parser_from_components_classes(self, parser: "ArgumentParser"):
        for unit_cls in self.application_cls.get_units_classes():
            for component_cls in unit_cls.get_components_classes():
                logger.debug(
                    "CLI ArgumentParser: %r. Prepare from: %r.", parser, component_cls
                )
                component_cls.prepare_cli_parser(parser=parser)

    def prepare_cli_parser_from_units_classes(self, parser: "ArgumentParser"):
        units_subparsers_manager = self.build_units_cli_subparsers_manager(
            parser=parser
        )
        for unit_cls in self.application_cls.get_units_classes():
            self.prepare_cli_parser_from_unit_cls(
                subparsers_manager=units_subparsers_manager, unit_cls=unit_cls
            )

    def build_units_cli_subparsers_manager(
        self, parser: "ArgumentParser"
    ) -> "_SubParsersAction":
        return parser.add_subparsers(
            title="Registered units",
            dest="runner_unit_name",
            required=True,
        )

    def prepare_cli_parser_from_unit_cls(
        self, subparsers_manager: "_SubParsersAction", unit_cls: type["CliUnit"]
    ):
        params = unit_cls.get_cli_parser_creating_parameters()
        logger.debug("CLI ArgumentParser for: %r. Parameters: %r.", unit_cls, params)
        unit_parser = subparsers_manager.add_parser(unit_cls.cli_name, **params)
        logger.debug("CLI ArgumentParser: %r. Prepare from: %r.", unit_parser, unit_cls)
        unit_cls.prepare_cli_parser(parser=unit_parser)
        self.prepare_cli_parser_from_unit_commands_classes(
            parser=unit_parser, unit_cls=unit_cls
        )

    def prepare_cli_parser_from_unit_commands_classes(
        self, parser: "ArgumentParser", unit_cls: type["CliUnit"]
    ):
        commands_subparsers_manager = self.build_commands_cli_subparsers_manager(
            parser=parser
        )
        for command_cls in unit_cls.get_commands_classes():
            self.prepare_cli_parser_from_command_cls(
                subparsers_manager=commands_subparsers_manager,
                command_cls=command_cls,
            )

    def prepare_cli_parser_from_command_cls(
        self, subparsers_manager: "_SubParsersAction", command_cls: type["CliCommand"]
    ):
        params = command_cls.get_cli_parser_creating_parameters()
        logger.debug("CLI ArgumentParser for: %r. Parameters: %r.", command_cls, params)
        command_parser = subparsers_manager.add_parser(command_cls.cli_name, **params)
        logger.debug(
            "CLI ArgumentParser: %r. Prepare from: %r.", command_parser, command_cls
        )
        command_cls.prepare_cli_parser(parser=command_parser)

    def build_commands_cli_subparsers_manager(
        self, parser: "ArgumentParser"
    ) -> "_SubParsersAction":
        return parser.add_subparsers(
            title="Registered commands",
            dest="runner_command_name",
            required=True,
        )

    @property
    def is_debug_mode(self) -> bool:
        return self.creating_params.runner_is_debug_mode

    @property
    def unit_name(self) -> str:
        return self.creating_params.runner_unit_name

    @property
    def command_name(self) -> str:
        return self.creating_params.runner_command_name

    def run(self):
        logger.info("Start running.")
        try:
            self.run_workflow()
        except Exception as err:
            logger.exception("Running error: %r.", err)
            self.exit_code = 1
        finally:
            logger.info("Finish running.")

        sys.exit(self.exit_code)

    def run_workflow(self):
        self.creating_params = self.prepare_creating_params()
        logger.info(
            "Ingots Entities creating parameters: %r.",
            self.creating_params,
        )
        self.application = self.create_application()
        self.prepare_asyncio()
        asyncio.run(
            self.run_async_workflow(),
            debug=self.is_debug_mode,
        )

    def prepare_asyncio(self): ...

    async def run_async_workflow(self):
        try:
            logger.info("Configuring application.")
            await self.application.configure()
            await self.run_command_workflow()
        finally:
            logger.info("Shutdown application.")
            await self.application.shut_down()

    async def run_command_workflow(self):
        event_loop = asyncio.get_running_loop()
        self.command = await self.build_command()
        self._run_command_task = event_loop.create_task(self.command.run())
        self._run_command_task.add_done_callback(self.run_command_tack_done_callback)
        self._running_command_task_future = event_loop.create_future()
        logger.info(
            "Start command executing. Send SIGINT or SIGTERM signal for cancelling"
            " running."
        )

        event_loop.add_signal_handler(
            signal.SIGINT,
            self.handle_sigint_sigterm_callback,
            "SIGINT",
        )
        event_loop.add_signal_handler(
            signal.SIGTERM,
            self.handle_sigint_sigterm_callback,
            "SIGTERM",
        )

        try:
            await self._running_command_task_future
        except asyncio.CancelledError:
            logger.warning("Command executing is cancelled.")
            try:
                await asyncio.wait_for(
                    self.command.cancel_running(),
                    timeout=self.command_cancellation_timeout,
                )
            except Exception as err:
                logger.exception("Command cancellation is failed. Error: %r", err)
                self._run_command_task.cancel()
                try:
                    await self._run_command_task
                except asyncio.CancelledError:
                    pass
        except Exception as err:
            logger.exception("Command executing is failed. Error: %r", err)
            self.exit_code = 1
        else:
            logger.info("Command executing is finished successfully.")
        finally:
            event_loop.remove_signal_handler(signal.SIGINT)
            event_loop.remove_signal_handler(signal.SIGTERM)

    async def build_command(self) -> "CliCommand":
        base_unit_cls = self.application_cls.get_base_unit_cls_by_cli_name(
            name=self.unit_name
        )
        unit = await self.application.get_unit(unit_cls=base_unit_cls)
        base_command_cls = unit.get_base_command_cls_by_cli_name(name=self.command_name)
        return unit.create_command(command_cls=base_command_cls)

    def run_command_tack_done_callback(self, task: "asyncio.Task"):
        if not self._running_command_task_future.done():
            err = task.exception()
            if err:
                self._running_command_task_future.set_exception(err)
            else:
                self._running_command_task_future.set_result(task.result())

    def handle_sigint_sigterm_callback(self, sig_name: str):
        logger.info("The %s signal is received.", sig_name)
        if not self._running_command_task_future.done():
            self._running_command_task_future.set_exception(
                asyncio.CancelledError(f"Cancelled by receiving the {sig_name}")
            )
