import os
import typing as t
from unittest.mock import patch

from ingots.apps.defaults import (
    Application,
    ApplicationRunner,
    Command,
    Component,
    SettingsUnit,
    Unit,
)
from ingots.tests import helpers

if t.TYPE_CHECKING:
    ...


class TstCommand(Command["TstApplication", "TstUnit"]):
    cli_name = "command"
    cli_description = "Test command CLI description"

    async def run(self): ...


class TstComponent(Component["TstApplication", "TstUnit"]):
    cli_name = "component"
    cli_description = "Test component CLI description"

    @classmethod
    def prepare_final_classes(cls): ...

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.unit.is_component_created = True

    async def configure(self):
        self.unit.is_component_configured = True

    async def shut_down(self):
        self.unit.is_component_shut_down = True


class TstUnit(Unit["TstApplication", "TstComponent", "TstCommand"]):
    cli_name = "unit"
    cli_description = "Test unit CLI description"
    is_component_created: bool = False
    is_component_configured: bool = False
    is_component_shut_down: bool = False

    @classmethod
    def register_components_classes(cls) -> set[type["TstComponent"]]:
        classes = super().register_components_classes()
        classes.add(TstComponent)
        return classes

    @classmethod
    def register_commands_classes(cls) -> set[type["TstCommand"]]:
        classes = super().register_commands_classes()
        classes.add(TstCommand)
        return classes

    async def configure(self):
        if self.settings.TST_UNIT_IS_TST_COMPONENT_ENABLED:
            await self.get_component(component_cls=TstComponent)


class TstUnitSettingsUnitExt(SettingsUnit):
    TST_UNIT_IS_TST_COMPONENT_ENABLED: bool = False

    TST_UNIT_PY_FILE_CONFIG_1: int = 0
    TST_UNIT_PY_FILE_CONFIG_2: bool = False
    TST_UNIT_PY_FILE_CONFIG_3: str = ""
    TST_UNIT_JSON_CONFIG_1: int = 0
    TST_UNIT_JSON_CONFIG_2: bool = False
    TST_UNIT_JSON_CONFIG_3: str = ""
    TST_UNIT_TOML_CONFIG_1: int = 0
    TST_UNIT_TOML_CONFIG_2: bool = False
    TST_UNIT_TOML_CONFIG_3: str = ""


class TstApplication(Application["TstUnit", "TstComponent"]):
    cli_name = "app"
    cli_description = "Test application CLI description"
    env_configs_prefix: str = "TEST"

    @classmethod
    def register_units_classes(cls) -> set[type["TstUnit"]]:
        classes = super().register_units_classes()
        classes.add(TstUnit)
        return classes

    @classmethod
    def register_units_extensions(cls) -> set[type["TstUnit"]]:
        extensions = super().register_units_extensions()
        extensions.add(TstUnitSettingsUnitExt)
        return extensions


class TstApplicationRunner(ApplicationRunner["TstApplication"]):
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

    async def test_enabled(self):
        """Checks instances creating, configuring and shutting down flow."""
        tst_runner = self.build_tst_obj(
            cli_args=[
                # "--help",
                "--config=TST_UNIT_IS_TST_COMPONENT_ENABLED=1",
                "unit",
                "command",
            ]
        )
        await tst_runner.run_test_workflow()
        tst_unit = await tst_runner.application.get_unit(unit_cls=TstUnit)
        assert tst_unit.is_component_created
        assert tst_unit.is_component_configured
        assert tst_unit.is_component_shut_down

    async def test_disabled(self):
        """Checks instances creating, configuring and shutting down flow."""
        tst_runner = self.build_tst_obj()
        await tst_runner.run_test_workflow()
        tst_unit = await tst_runner.application.get_unit(unit_cls=TstUnit)
        assert not tst_unit.is_component_created
        assert not tst_unit.is_component_configured
        assert not tst_unit.is_component_shut_down

    async def test_configs_overrides(self):
        """Checks configs overrides flow.
        *_CONFIG_1 is override in file.
        *_CONFIG_2 is override in env.
        *_CONFIG_# is override in CLI.
        """
        tst_venv = {
            "TEST_TST_UNIT_PY_FILE_CONFIG_2": "",
            "TEST_TST_UNIT_JSON_CONFIG_2": "",
            "TEST_TST_UNIT_TOML_CONFIG_2": "",
        }
        configs_files_path = os.path.dirname(os.path.relpath(__file__))
        py_configs_path = os.path.join(configs_files_path, "tst_settings.py")
        json_configs_path = os.path.join(configs_files_path, "tst_settings.json")
        toml_configs_path = os.path.join(configs_files_path, "tst_settings.toml")
        tst_runner = self.build_tst_obj(
            cli_args=[
                # "--help",
                f"--configs-file={py_configs_path}",
                f"--configs-file={json_configs_path}",
                f"--configs-file={toml_configs_path}",
                "--config=TST_UNIT_PY_FILE_CONFIG_3=py_file_cli",
                "--config=TST_UNIT_JSON_CONFIG_3=json_cli",
                "--config=TST_UNIT_TOML_CONFIG_3=toml_cli",
                "unit",
                "command",
            ]
        )
        with patch.object(os, "environ", tst_venv):
            await tst_runner.run_test_workflow()
        settings = await tst_runner.application.get_unit(unit_cls=SettingsUnit)

        assert settings.TST_UNIT_PY_FILE_CONFIG_1 == 12
        assert settings.TST_UNIT_PY_FILE_CONFIG_2 is False
        assert settings.TST_UNIT_PY_FILE_CONFIG_3 == "py_file_cli"

        assert settings.TST_UNIT_JSON_CONFIG_1 == 123
        assert settings.TST_UNIT_JSON_CONFIG_2 is False
        assert settings.TST_UNIT_JSON_CONFIG_3 == "json_cli"

        assert settings.TST_UNIT_TOML_CONFIG_1 == 1234
        assert settings.TST_UNIT_TOML_CONFIG_2 is False
        assert settings.TST_UNIT_TOML_CONFIG_3 == "toml_cli"
