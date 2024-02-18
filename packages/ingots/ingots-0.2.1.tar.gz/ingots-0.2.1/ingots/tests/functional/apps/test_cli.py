import asyncio
import typing as t

from ingots.apps.cli import (
    CliApplication,
    CliApplicationRunner,
    CliCommand,
    CliComponent,
    CliUnit,
)
from ingots.tests import helpers

if t.TYPE_CHECKING:
    from argparse import ArgumentParser


class TstCommand(CliCommand["TstApplication", "TstUnit"]):
    cli_name = "command"
    cli_description = "Test command CLI description"

    @classmethod
    def prepare_cli_parser(cls, parser: "ArgumentParser"):
        super().prepare_cli_parser(parser=parser)
        parser.add_argument(
            "--cmd-arg",
            dest="unit_command_arg",
            default="",
        )

    @property
    def arg(self) -> str:
        return self.creating_params.unit_command_arg

    async def run(self): ...

    async def cancel_running(self): ...


class TstLongCommand(CliCommand["TstApplication", "TstUnit"]):
    cli_name = "long"
    cli_description = "Test long command CLI description"

    is_running_started: bool = False
    is_running_completed: bool = False

    is_cancellation_started: bool = False
    is_cancellation_completed: bool = False

    _run_sleeping_task: "asyncio.Task"

    @classmethod
    def prepare_cli_parser(cls, parser: "ArgumentParser"):
        super().prepare_cli_parser(parser=parser)
        parser.add_argument(
            "--cmd-running-delay",
            dest="unit_command_running_delay",
            type=int,
            default=0,
        )
        parser.add_argument(
            "--cmd-cancelling-delay",
            dest="unit_command_cancelling_delay",
            type=int,
            default=0,
        )

    async def run(self):
        self.is_running_started = True
        event_loop = asyncio.get_running_loop()
        self._run_sleeping_task = event_loop.create_task(
            asyncio.sleep(self.creating_params.unit_command_running_delay)
        )
        await self._run_sleeping_task
        self.is_running_completed = True

    async def cancel_running(self):
        self.is_cancellation_started = True
        self._run_sleeping_task.cancel()
        await asyncio.sleep(self.creating_params.unit_command_cancelling_delay)
        self.is_cancellation_completed = True


class TstFailedCommand(CliCommand["TstApplication", "TstUnit"]):
    cli_name = "failed"
    cli_description = "Test failed command CLI description"


class TstComponent(CliComponent["TstApplication", "TstUnit"]):
    cli_name = "component"
    cli_description = "Test component CLI description"

    @classmethod
    def prepare_final_classes(cls): ...

    @classmethod
    def prepare_cli_parser(cls, parser: "ArgumentParser"):
        super().prepare_cli_parser(parser=parser)
        parser.add_argument(
            "--cmp-arg",
            dest="unit_component_arg",
            default="",
        )

    @property
    def arg(self) -> str:
        return self.creating_params.unit_component_arg

    async def configure(self): ...

    async def shut_down(self): ...


class TstUnit(CliUnit["TstApplication", "TstComponent", "TstCommand"]):
    cli_name = "unit"
    cli_description = "Test unit CLI description"

    @classmethod
    def register_components_classes(cls) -> set[type["TstComponent"]]:
        classes = super().register_components_classes()
        classes.add(TstComponent)
        return classes

    @classmethod
    def register_commands_classes(cls) -> set[type["TstCommand"]]:
        classes = super().register_commands_classes()
        classes.add(TstCommand)
        classes.add(TstLongCommand)
        classes.add(TstFailedCommand)
        return classes

    @classmethod
    def prepare_cli_parser(cls, parser: "ArgumentParser"):
        super().prepare_cli_parser(parser=parser)
        parser.add_argument(
            "--unit-arg",
            dest="unit_arg",
            default="",
        )

    @property
    def arg(self) -> str:
        return self.creating_params.unit_arg

    async def configure(self): ...


class TstCommandExt(TstCommand):
    @classmethod
    def prepare_cli_parser(cls, parser: "ArgumentParser"):
        super().prepare_cli_parser(parser=parser)
        parser.add_argument(
            "--cmd-ext-arg",
            dest="unit_command_ext_arg",
            default="",
        )

    @property
    def ext_arg(self) -> str:
        return self.creating_params.unit_command_ext_arg


class TstComponentExt(TstComponent):
    @classmethod
    def prepare_cli_parser(cls, parser: "ArgumentParser"):
        super().prepare_cli_parser(parser=parser)
        parser.add_argument(
            "--cmp-ext-arg",
            dest="unit_component_ext_arg",
            default="",
        )

    @property
    def ext_arg(self) -> str:
        return self.creating_params.unit_component_ext_arg


class TstUnitExt(TstUnit):
    @classmethod
    def register_components_extensions(cls) -> set[type["TstComponent"]]:
        extensions = super().register_components_extensions()
        extensions.add(TstComponentExt)
        return extensions

    @classmethod
    def register_commands_extensions(cls) -> set[type["TstCommand"]]:
        extensions = super().register_commands_extensions()
        extensions.add(TstCommandExt)
        return extensions

    @classmethod
    def prepare_cli_parser(cls, parser: "ArgumentParser"):
        super().prepare_cli_parser(parser=parser)
        parser.add_argument(
            "--unit-ext-arg",
            dest="unit_ext_arg",
            default="",
        )

    @property
    def ext_arg(self) -> str:
        return self.creating_params.unit_ext_arg


class TstApplication(CliApplication["TstUnit", "TstComponent"]):
    cli_name = "app"
    cli_description = "Test application CLI description"

    @classmethod
    def register_units_classes(cls) -> set[type["TstUnit"]]:
        classes = super().register_units_classes()
        classes.add(TstUnit)
        return classes

    @classmethod
    def register_units_extensions(cls) -> set[type["TstUnit"]]:
        extensions = super().register_units_extensions()
        extensions.add(TstUnitExt)
        return extensions

    @classmethod
    def prepare_cli_parser(cls, parser: "ArgumentParser"):
        super().prepare_cli_parser(parser=parser)
        parser.add_argument(
            "--app-arg",
            dest="app_arg",
            default="",
        )

    @property
    def arg(self) -> str:
        return self.creating_params.app_arg

    async def configure(self): ...


class TstApplicationRunner(CliApplicationRunner["TstApplication"]):
    def prepare_cli_parser(self, parser: "ArgumentParser"):
        super().prepare_cli_parser(parser=parser)
        parser.add_argument(
            "--runner-arg",
            dest="runner_arg",
            default="",
        )

    @property
    def arg(self) -> str:
        return self.creating_params.runner_arg

    async def run_test_workflow(self):
        self.creating_params = self.prepare_creating_params()
        self.application = self.create_application()
        await self.run_async_workflow()


class MainFlowTestCase(helpers.ClassTestingTestCase[TstApplicationRunner]):
    """Contains tests for base apps feature."""

    tst_cls = TstApplicationRunner
    tst_application_cls: type["TstApplication"] = TstApplication

    def get_tst_obj_init_params(self, **kwargs) -> dict:
        kwargs.setdefault("application_cls", self.tst_application_cls)
        kwargs.setdefault("cli_args", ["unit", "command"])
        return super().get_tst_obj_init_params(**kwargs)

    async def test_instances(self):
        """Checks instances creating, configuring and shutting down flow."""
        tst_runner = self.build_tst_obj(
            cli_args=[
                # "--help",
                "--runner-arg=runner-arg-value",
                "--app-arg=app-arg-value",
                "--cmp-arg=cmp-arg-value",
                "--cmp-ext-arg=cmp-ext-arg-value",
                "unit",
                "--unit-arg=unit-arg-value",
                "--unit-ext-arg=unit-ext-arg-value",
                "command",
                "--cmd-arg=cmd-arg-value",
                "--cmd-ext-arg=cmd-ext-arg-value",
            ]
        )
        await tst_runner.run_test_workflow()

        assert tst_runner.arg == "runner-arg-value"

        assert tst_runner.application.arg == "app-arg-value"

        tst_unit = await tst_runner.application.get_unit(unit_cls=TstUnit)
        assert tst_unit.arg == "unit-arg-value"
        assert tst_unit.ext_arg == "unit-ext-arg-value"

        tst_component = await tst_unit.get_component(component_cls=TstComponent)
        assert tst_component.arg == "cmp-arg-value"
        assert tst_component.ext_arg == "cmp-ext-arg-value"

        tst_command = tst_unit.create_command(command_cls=TstCommand)
        assert tst_command.arg == "cmd-arg-value"
        assert tst_command.ext_arg == "cmd-ext-arg-value"

    async def test_long_command_execution(self):
        """Checks the long command running without cancellation."""
        tst_runner = self.build_tst_obj(cli_args=["unit", "long"])

        await tst_runner.run_test_workflow()

        assert isinstance(tst_runner.command, TstLongCommand)
        assert tst_runner.command.is_running_started is True
        assert tst_runner.command.is_running_completed is True
        assert tst_runner.command.is_cancellation_started is False
        assert tst_runner.command.is_cancellation_completed is False

    async def test_long_command_execution_cancel(self):
        """Checks the long command running with cancellation."""
        tst_runner = self.build_tst_obj(
            cli_args=["unit", "long", "--cmd-running-delay=2"]
        )
        event_loop = asyncio.get_running_loop()
        event_loop.call_later(1, tst_runner.handle_sigint_sigterm_callback, "SIGTST")

        await tst_runner.run_test_workflow()

        assert isinstance(tst_runner.command, TstLongCommand)
        assert tst_runner.command.is_running_started is True
        assert tst_runner.command.is_running_completed is False
        assert tst_runner.command.is_cancellation_started is True
        assert tst_runner.command.is_cancellation_completed is True

    async def test_long_command_execution_cancel_timeout(self):
        """Checks the long command running with cancellation by timeout."""
        tst_runner = self.build_tst_obj(
            cli_args=[
                "unit",
                "long",
                "--cmd-running-delay=2",
                "--cmd-cancelling-delay=2",
            ]
        )
        tst_runner.command_cancellation_timeout = 1
        event_loop = asyncio.get_running_loop()
        event_loop.call_later(1, tst_runner.handle_sigint_sigterm_callback, "SIGTST")

        await tst_runner.run_test_workflow()

        assert isinstance(tst_runner.command, TstLongCommand)
        assert tst_runner.command.is_running_started is True
        assert tst_runner.command.is_running_completed is False
        assert tst_runner.command.is_cancellation_started is True
        assert tst_runner.command.is_cancellation_completed is False

    async def test_failed_command_execution(self):
        """Checks the failed command running without cancellation."""
        tst_runner = self.build_tst_obj(cli_args=["unit", "failed"])

        await tst_runner.run_test_workflow()

        assert isinstance(tst_runner.command, TstFailedCommand)
