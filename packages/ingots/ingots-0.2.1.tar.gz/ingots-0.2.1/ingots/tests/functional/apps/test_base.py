import typing as t

from ingots.apps.base import (
    BaseApplication,
    BaseApplicationRunner,
    BaseCommand,
    BaseComponent,
    BaseUnit,
)
from ingots.tests import helpers

if t.TYPE_CHECKING:
    ...


class TstCreatingParams:
    pass


class TstCommand(BaseCommand["TstCreatingParams", "TstApplication", "TstUnit"]):
    is_run_called: bool = False

    async def run(self):
        self.is_run_called = True


class TstComponent(BaseComponent["TstCreatingParams", "TstApplication", "TstUnit"]):
    is_prepare_final_classes_called: bool = False
    is_configure_called: bool = False
    is_shut_down_called: bool = False

    @classmethod
    def prepare_final_classes(cls):
        cls.is_prepare_final_classes_called = True

    async def configure(self):
        self.is_configure_called = True

    async def shut_down(self):
        self.is_shut_down_called = True


class TstUnit(
    BaseUnit["TstCreatingParams", "TstApplication", "TstComponent", "TstCommand"]
):
    is_prepare_final_classes_called: bool = False
    is_configure_called: bool = False

    @classmethod
    def prepare_final_classes(cls):
        super().prepare_final_classes()
        cls.is_prepare_final_classes_called = True

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
        self.is_configure_called = True


class TstCommandExt(TstCommand):
    is_run_ext_called: bool = False

    async def run(self):
        await super().run()
        self.is_run_ext_called = True


class TstComponentExt(TstComponent):
    is_prepare_final_classes_ext_called: bool = False
    is_configure_ext_called: bool = False
    is_shut_down_ext_called: bool = False

    @classmethod
    def prepare_final_classes(cls):
        super().prepare_final_classes()
        cls.is_prepare_final_classes_ext_called = True

    async def configure(self):
        await super().configure()
        self.is_configure_ext_called = True

    async def shut_down(self):
        await super().shut_down()
        self.is_shut_down_ext_called = True


class TstUnitExt(TstUnit):
    is_prepare_final_classes_ext_called: bool = False
    is_configure_ext_called: bool = False

    @classmethod
    def prepare_final_classes(cls):
        super().prepare_final_classes()
        cls.is_prepare_final_classes_ext_called = True

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

    async def configure(self):
        await super().configure()
        self.is_configure_ext_called = True


class TstCommandAppExt(TstCommand):
    build_class_extensions_order = 0
    is_run_app_ext_called: bool = False

    async def run(self):
        await super().run()
        self.is_run_app_ext_called = True


class TstComponentAppExt(TstComponent):
    build_class_extensions_order = 0
    is_prepare_final_classes_app_ext_called: bool = False
    is_configure_app_ext_called: bool = False
    is_shut_down_app_ext_called: bool = False

    @classmethod
    def prepare_final_classes(cls):
        super().prepare_final_classes()
        cls.is_prepare_final_classes_app_ext_called = True

    async def configure(self):
        await super().configure()
        self.is_configure_app_ext_called = True

    async def shut_down(self):
        await super().shut_down()
        self.is_shut_down_app_ext_called = True


class TstUnitAppExt(TstUnit):
    build_class_extensions_order = 0
    is_prepare_final_classes_app_ext_called: bool = False
    is_configure_app_ext_called: bool = False

    @classmethod
    def prepare_final_classes(cls):
        super().prepare_final_classes()
        cls.is_prepare_final_classes_app_ext_called = True

    @classmethod
    def register_components_extensions(cls) -> set[type["TstComponent"]]:
        extensions = super().register_components_extensions()
        extensions.add(TstComponentAppExt)
        return extensions

    @classmethod
    def register_commands_extensions(cls) -> set[type["TstCommand"]]:
        extensions = super().register_commands_extensions()
        extensions.add(TstCommandAppExt)
        return extensions

    async def configure(self):
        await super().configure()
        self.is_configure_app_ext_called = True


class TstApplication(BaseApplication["TstCreatingParams", "TstUnit", "TstComponent"]):
    is_prepare_final_classes_called: bool = False
    is_configure_called: bool = False

    @classmethod
    def prepare_final_classes(cls):
        super().prepare_final_classes()
        cls.is_prepare_final_classes_called = True

    @classmethod
    def register_units_classes(cls) -> set[type["TstUnit"]]:
        classes = super().register_units_classes()
        classes.add(TstUnit)
        return classes

    @classmethod
    def register_units_extensions(cls) -> set[type["TstUnit"]]:
        extensions = super().register_units_extensions()
        extensions.add(TstUnitExt)
        extensions.add(TstUnitAppExt)
        return extensions

    async def configure(self):
        self.is_configure_called = True


class TstApplicationRunner(
    BaseApplicationRunner["TstCreatingParams", "TstApplication"]
):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.creating_params = self.prepare_creating_params()

    def prepare_creating_params(self) -> "TstCreatingParams":
        return TstCreatingParams()


class MainFlowTestCase(helpers.ClassTestingTestCase[TstApplicationRunner]):
    """Contains tests for base apps feature."""

    tst_cls = TstApplicationRunner
    tst_application_cls: type["TstApplication"] = TstApplication

    def get_tst_obj_init_params(self, **kwargs) -> dict:
        kwargs.setdefault("application_cls", self.tst_application_cls)
        return super().get_tst_obj_init_params(**kwargs)

    def test_final_classes(self):
        """Checks final classes generating flow."""
        self.tst_application_cls.prepare_final_classes()
        assert self.tst_application_cls.is_prepare_final_classes_called

        tst_units_classes = self.tst_application_cls.get_units_classes()
        assert len(tst_units_classes) == 1

        final_unit_cls = tst_units_classes[0]
        assert issubclass(final_unit_cls, TstUnitExt)
        assert issubclass(final_unit_cls, TstUnitAppExt)
        assert final_unit_cls.__mro__[1:5] == (
            TstUnitAppExt,
            TstUnitExt,
            TstUnit,
            BaseUnit,
        )
        assert final_unit_cls.is_prepare_final_classes_called
        assert final_unit_cls.is_prepare_final_classes_ext_called
        assert final_unit_cls.is_prepare_final_classes_app_ext_called

        tst_components_classes = final_unit_cls.get_components_classes()
        assert len(tst_components_classes) == 1

        final_component_cls = tst_components_classes[0]
        assert issubclass(final_component_cls, TstComponentExt)
        assert issubclass(final_component_cls, TstComponentAppExt)
        assert final_component_cls.__mro__[1:5] == (
            TstComponentAppExt,
            TstComponentExt,
            TstComponent,
            BaseComponent,
        )
        assert final_component_cls.is_prepare_final_classes_called
        assert final_component_cls.is_prepare_final_classes_ext_called
        assert final_component_cls.is_prepare_final_classes_app_ext_called

        tst_commands_classes = final_unit_cls.get_commands_classes()
        assert len(tst_commands_classes) == 1

        final_command_cls = tst_commands_classes[0]
        assert issubclass(final_command_cls, TstCommandExt)
        assert issubclass(final_command_cls, TstCommandAppExt)
        assert final_command_cls.__mro__[1:5] == (
            TstCommandAppExt,
            TstCommandExt,
            TstCommand,
            BaseCommand,
        )

    async def test_instances(self):
        """Checks instances creating, configuring and shutting down flow."""
        tst_runner = self.build_tst_obj()
        tst_app = tst_runner.create_application()

        await tst_app.configure()
        assert tst_app.is_configure_called

        tst_unit = await tst_app.get_unit(unit_cls=TstUnit)
        assert tst_unit.is_configure_called
        assert tst_unit.is_configure_ext_called
        assert tst_unit.is_configure_app_ext_called

        tst_component = await tst_unit.get_component(component_cls=TstComponent)
        assert tst_component.is_configure_called
        assert tst_component.is_configure_ext_called
        assert tst_component.is_configure_app_ext_called

        tst_command = tst_unit.create_command(command_cls=TstCommand)

        await tst_command.run()
        assert tst_command.is_run_called
        assert tst_command.is_run_ext_called
        assert tst_command.is_run_app_ext_called

        await tst_app.shut_down()
        assert tst_component.is_shut_down_called
        assert tst_component.is_shut_down_app_ext_called
