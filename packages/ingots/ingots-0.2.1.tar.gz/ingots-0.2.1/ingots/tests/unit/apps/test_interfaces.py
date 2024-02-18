__all__ = (
    "CommandInterfaceTestCase",
    "ComponentInterfaceTestCase",
    "UnitInterfaceTestCase",
    "ApplicationInterfaceTestCase",
    "ApplicationRunnerInterfaceTestCase",
)

import typing as t
from unittest.mock import Mock

from ingots.apps.interfaces import (
    ApplicationInterface,
    ApplicationRunnerInterface,
    CommandInterface,
    ComponentInterface,
    UnitInterface,
)
from ingots.tests import helpers

if t.TYPE_CHECKING:
    ...


CommandInterfaceTypeVar = t.TypeVar("CommandInterfaceTypeVar", bound=CommandInterface)


class CommandInterfaceTestCase(
    helpers.ClassTestingTestCase[CommandInterfaceTypeVar],
    t.Generic[CommandInterfaceTypeVar],
):
    """Contains tests for CommandInterface class."""

    tst_cls: type[CommandInterfaceTypeVar] = CommandInterface

    def test_create(self):
        """Checks the create class method."""
        with self.assertRaises(NotImplementedError):
            self.tst_cls.create(unit=Mock(), params=Mock())

    async def test_run(self):
        """Checks the run async method."""
        tst_obj = self.build_tst_obj()

        with self.assertRaises(NotImplementedError):
            await tst_obj.run()

    async def test_cancel_running(self):
        """Checks the cancel_running async method."""
        tst_obj = self.build_tst_obj()

        with self.assertRaises(NotImplementedError):
            await tst_obj.cancel_running()


ComponentInterfaceTypeVar = t.TypeVar(
    "ComponentInterfaceTypeVar", bound=ComponentInterface
)


class ComponentInterfaceTestCase(
    helpers.ClassTestingTestCase[ComponentInterfaceTypeVar],
    t.Generic[ComponentInterfaceTypeVar],
):
    """Contains tests for ComponentInterface class."""

    tst_cls: type[ComponentInterfaceTypeVar] = ComponentInterface

    def test_prepare_final_classes(self):
        """Checks the prepare_final_classes class method."""
        with self.assertRaises(NotImplementedError):
            self.tst_cls.prepare_final_classes()

    def test_create(self):
        """Checks the create class method."""
        with self.assertRaises(NotImplementedError):
            self.tst_cls.create(unit=Mock(), params=Mock())

    async def test_configure(self):
        """Checks the configure async method."""
        tst_obj = self.build_tst_obj()

        with self.assertRaises(NotImplementedError):
            await tst_obj.configure()

    async def test_shut_down(self):
        """Checks the shut_down async method."""
        tst_obj = self.build_tst_obj()

        with self.assertRaises(NotImplementedError):
            await tst_obj.shut_down()


UnitInterfaceTypeVar = t.TypeVar("UnitInterfaceTypeVar", bound=UnitInterface)


class UnitInterfaceTestCase(
    helpers.ClassTestingTestCase[UnitInterfaceTypeVar],
    t.Generic[UnitInterfaceTypeVar],
):
    """Contains tests for UnitInterface class."""

    tst_cls: type[UnitInterfaceTypeVar] = UnitInterface

    def test_prepare_final_classes(self):
        """Checks the prepare_final_classes class method."""
        with self.assertRaises(NotImplementedError):
            self.tst_cls.prepare_final_classes()

    def test_register_components_classes(self):
        """Checks the register_components_classes class method."""
        with self.assertRaises(NotImplementedError):
            self.tst_cls.register_components_classes()

    def test_register_components_extensions(self):
        """Checks the register_components_extensions class method."""
        with self.assertRaises(NotImplementedError):
            self.tst_cls.register_components_extensions()

    def test_get_components_classes(self):
        """Checks the get_components_classes class method."""
        with self.assertRaises(NotImplementedError):
            self.tst_cls.get_components_classes()

    def test_register_commands_classes(self):
        """Checks the register_commands_classes class method."""
        with self.assertRaises(NotImplementedError):
            self.tst_cls.register_commands_classes()

    def test_register_commands_extensions(self):
        """Checks the register_commands_extensions class method."""
        with self.assertRaises(NotImplementedError):
            self.tst_cls.register_commands_extensions()

    def test_get_commands_classes(self):
        """Checks the get_commands_classes class method."""
        with self.assertRaises(NotImplementedError):
            self.tst_cls.get_commands_classes()

    def test_create(self):
        """Checks the create class method."""
        with self.assertRaises(NotImplementedError):
            self.tst_cls.create(application=Mock(), params=Mock())

    async def test_configure(self):
        """Checks the configure async method."""
        tst_obj = self.build_tst_obj()

        with self.assertRaises(NotImplementedError):
            await tst_obj.configure()

    async def test_get_component(self):
        """Checks the get_component async method."""
        tst_obj = self.build_tst_obj()

        with self.assertRaises(NotImplementedError):
            await tst_obj.get_component(component_cls=Mock())

    def test_create_component(self):
        """Checks the create_component method."""
        tst_obj = self.build_tst_obj()

        with self.assertRaises(NotImplementedError):
            tst_obj.create_component(component_cls=Mock())

    async def test_shut_down_component(self):
        """Checks the shut_down_component async method."""
        tst_obj = self.build_tst_obj()

        with self.assertRaises(NotImplementedError):
            await tst_obj.shut_down_component(component_cls=Mock())

    def test_get_components(self):
        """Checks the get_components method."""
        tst_obj = self.build_tst_obj()

        with self.assertRaises(NotImplementedError):
            tst_obj.get_components()

    def test_create_command(self):
        """Checks the create_command method."""
        tst_obj = self.build_tst_obj()

        with self.assertRaises(NotImplementedError):
            tst_obj.create_command(command_cls=Mock())


ApplicationInterfaceTypeVar = t.TypeVar(
    "ApplicationInterfaceTypeVar", bound=ApplicationInterface
)


class ApplicationInterfaceTestCase(
    helpers.ClassTestingTestCase[ApplicationInterfaceTypeVar],
    t.Generic[ApplicationInterfaceTypeVar],
):
    """Contains tests for ApplicationInterface class."""

    tst_cls: type[ApplicationInterfaceTypeVar] = ApplicationInterface

    def test_prepare_final_classes(self):
        """Checks the prepare_final_classes class method."""
        with self.assertRaises(NotImplementedError):
            self.tst_cls.prepare_final_classes()

    def test_register_units_classes(self):
        """Checks the register_units_classes class method."""
        with self.assertRaises(NotImplementedError):
            self.tst_cls.register_units_classes()

    def test_register_units_extensions(self):
        """Checks the register_units_extensions class method."""
        with self.assertRaises(NotImplementedError):
            self.tst_cls.register_units_extensions()

    def test_get_units_classes(self):
        """Checks the get_units_classes class method."""
        with self.assertRaises(NotImplementedError):
            self.tst_cls.get_units_classes()

    def test_create(self):
        """Checks the create class method."""
        with self.assertRaises(NotImplementedError):
            self.tst_cls.create(params=Mock())

    async def test_configure(self):
        """Checks the configure async method."""
        tst_obj = self.build_tst_obj()

        with self.assertRaises(NotImplementedError):
            await tst_obj.configure()

    async def test_get_unit(self):
        """Checks the get_unit async method."""
        tst_obj = self.build_tst_obj()

        with self.assertRaises(NotImplementedError):
            await tst_obj.get_unit(unit_cls=Mock())

    def test_create_unit(self):
        """Checks the create_unit method."""
        tst_obj = self.build_tst_obj()

        with self.assertRaises(NotImplementedError):
            tst_obj.create_unit(unit_cls=Mock())

    def test_get_units(self):
        """Checks the get_units method."""
        tst_obj = self.build_tst_obj()

        with self.assertRaises(NotImplementedError):
            tst_obj.get_units()

    async def test_shut_down(self):
        """Checks the shut_down async method."""
        tst_obj = self.build_tst_obj()

        with self.assertRaises(NotImplementedError):
            await tst_obj.shut_down()


ApplicationRunnerInterfaceTypeVar = t.TypeVar(
    "ApplicationRunnerInterfaceTypeVar", bound=ApplicationRunnerInterface
)


class ApplicationRunnerInterfaceTestCase(
    helpers.ClassTestingTestCase[ApplicationRunnerInterfaceTypeVar],
    t.Generic[ApplicationRunnerInterfaceTypeVar],
):
    """Contains tests for ApplicationRunnerInterface class."""

    tst_cls: type[ApplicationRunnerInterfaceTypeVar] = ApplicationRunnerInterface

    def test_prepare_creating_params(self):
        """Checks the prepare_creating_params method."""
        tst_obj = self.build_tst_obj()

        with self.assertRaises(NotImplementedError):
            tst_obj.prepare_creating_params()

    def test_create_application(self):
        """Checks the create_application method."""
        tst_obj = self.build_tst_obj()

        with self.assertRaises(NotImplementedError):
            tst_obj.create_application()
