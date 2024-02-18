__all__ = ("BaseUnitTestCase",)

import typing as t
from unittest.mock import AsyncMock, Mock, call, patch

from ingots.apps.base.units import BaseUnit
from ingots.tests.unit.apps import test_interfaces

if t.TYPE_CHECKING:
    ...


TestedClassTypeVar = t.TypeVar("TestedClassTypeVar", bound=BaseUnit)


class BaseUnitTestCase(
    test_interfaces.UnitInterfaceTestCase[TestedClassTypeVar],
    t.Generic[TestedClassTypeVar],
):
    """Contains tests for BaseUnit class."""

    tst_cls: type[TestedClassTypeVar] = BaseUnit

    def get_tst_obj_init_params(self, **kwargs) -> dict:
        kwargs.setdefault("application", Mock())
        kwargs.setdefault("params", Mock())
        return super().get_tst_obj_init_params(**kwargs)

    def test_prepare_final_classes(self):
        """Checks the prepare_class class method."""
        mock_classes_builder_build_components_res = Mock()
        mock_classes_builder_build_commands_res = Mock()
        mock_classes_builder = Mock()
        mock_classes_builder.build = Mock(
            side_effect=[
                mock_classes_builder_build_components_res,
                mock_classes_builder_build_commands_res,
            ]
        )
        mock_classes_builder_cls = Mock(return_value=mock_classes_builder)
        mock_register_components_classes_res = Mock()
        mock_register_components_extensions_res = Mock()
        mock_register_commands_classes_res = Mock()
        mock_register_commands_extensions_res = Mock()
        mock_component_cls = Mock()
        mock_component_cls.prepare_final_classes = Mock()

        tst_cls = self.build_tst_cls()
        tst_cls.register_components_classes = Mock(
            return_value=mock_register_components_classes_res
        )
        tst_cls.register_components_extensions = Mock(
            return_value=mock_register_components_extensions_res
        )
        tst_cls.register_commands_classes = Mock(
            return_value=mock_register_commands_classes_res
        )
        tst_cls.register_commands_extensions = Mock(
            return_value=mock_register_commands_extensions_res
        )
        tst_cls.get_components_classes = Mock(return_value=[mock_component_cls])
        with patch(
            "ingots.apps.base.units.FinalClassesBuilder"
        ) as mock_classes_builder_generic_cls:
            mock_classes_builder_generic_cls.__getitem__ = Mock(
                return_value=mock_classes_builder_cls
            )
            tst_cls.prepare_final_classes()

        tst_cls.register_components_classes.assert_called_once_with()
        tst_cls.register_components_extensions.assert_called_once_with()
        mock_classes_builder_cls.assert_has_calls(
            [
                call(
                    container=tst_cls,
                    nested="Components",
                    base_classes=mock_register_components_classes_res,
                    extensions=mock_register_components_extensions_res,
                ),
                call(
                    container=tst_cls,
                    nested="Commands",
                    base_classes=mock_register_commands_classes_res,
                    extensions=mock_register_commands_extensions_res,
                ),
            ]
        )
        mock_classes_builder.build.assert_has_calls(
            [
                call(),
                call(),
            ]
        )
        assert (
            tst_cls._final_components_classes_map
            == mock_classes_builder_build_components_res
        )
        assert (
            tst_cls._final_commands_classes_map
            == mock_classes_builder_build_commands_res
        )
        tst_cls.get_components_classes.assert_called_once_with()
        mock_component_cls.prepare_final_classes.assert_called_once_with()

    def test_register_components_classes(self):
        """Checks the register_components_classes class method."""
        tst_res = self.tst_cls.register_components_classes()

        assert isinstance(tst_res, set)
        assert len(tst_res) == 0

    def test_register_components_extensions(self):
        """Checks the register_components_extensions class method."""
        tst_res = self.tst_cls.register_components_extensions()

        assert isinstance(tst_res, set)
        assert len(tst_res) == 0

    def test_get_components_classes(self):
        """Checks the get_components_classes class method."""
        mock_base_cls = Mock()
        mock_final_cls = Mock()
        tst_cls = self.build_tst_cls()
        tst_cls._final_components_classes_map = {mock_base_cls: mock_final_cls}

        tst_res = tst_cls.get_components_classes()

        assert tst_res == [mock_final_cls]

    def test_register_commands_classes(self):
        """Checks the register_commands_classes class method."""
        tst_res = self.tst_cls.register_commands_classes()

        assert isinstance(tst_res, set)
        assert len(tst_res) == 0

    def test_register_commands_extensions(self):
        """Checks the register_commands_extensions class method."""
        tst_res = self.tst_cls.register_commands_extensions()

        assert isinstance(tst_res, set)
        assert len(tst_res) == 0

    def test_get_commands_classes(self):
        """Checks the get_commands_classes class method."""
        mock_base_cls = Mock()
        mock_final_cls = Mock()
        tst_cls = self.build_tst_cls()
        tst_cls._final_commands_classes_map = {mock_base_cls: mock_final_cls}

        tst_res = tst_cls.get_commands_classes()

        assert tst_res == [mock_final_cls]

    def test_create(self):
        """Checks the create class method."""
        tst_obj = self.tst_cls.create(application=Mock(), params=Mock())

        assert isinstance(tst_obj, self.tst_cls)

    async def test_get_component(self):
        """Checks get_component async method."""
        mock_cls = Mock()
        mock_instance = Mock()
        mock_instance.configure = AsyncMock()
        tst_obj = self.build_tst_obj()
        tst_obj.create_component = Mock(return_value=mock_instance)

        tst_res = await tst_obj.get_component(component_cls=mock_cls)

        assert tst_res == mock_instance
        tst_obj.create_component.assert_called_once_with(component_cls=mock_cls)
        mock_instance.configure.assert_awaited_once_with()
        assert tst_obj._created_components_map == {mock_cls: mock_instance}

    def test_create_component(self):
        """Checks the create_component method."""
        mock_base_cls = Mock()
        mock_instance = Mock()
        mock_final_cls = Mock()
        mock_final_cls.create = Mock(return_value=mock_instance)
        tst_obj = self.build_tst_obj()
        tst_obj._final_components_classes_map = {mock_base_cls: mock_final_cls}

        tst_res = tst_obj.create_component(component_cls=mock_base_cls)

        assert tst_res == mock_instance
        mock_final_cls.create.assert_called_once_with(
            unit=tst_obj, params=tst_obj.creating_params
        )

    def test_create_component_error(self):
        """Checks the create_component method for unregistered component class case."""
        mock_base_cls = Mock()
        mock_final_cls = Mock()
        tst_obj = self.build_tst_obj()
        tst_obj._final_components_classes_map = {mock_base_cls: mock_final_cls}
        mock_wrong_cls = Mock()
        mock_wrong_cls.__name__ = "Wrong"

        with self.assertRaises(TypeError):
            tst_obj.create_component(component_cls=mock_wrong_cls)

    async def test_shut_down_component(self):
        """Checks the shut_down_component method."""
        mock_cls = Mock()
        mock_instance = Mock()
        mock_instance.shut_down = AsyncMock()
        tst_obj = self.build_tst_obj()
        tst_obj._created_components_map = {mock_cls: mock_instance}

        await tst_obj.shut_down_component(component_cls=mock_cls)

    async def test_shut_down_component_error(self):
        """Checks the shut_down_component method with raising error case."""
        mock_cls = Mock()
        mock_instance = Mock()
        mock_instance.shut_down = AsyncMock(side_effect=Exception("Test"))
        tst_obj = self.build_tst_obj()
        tst_obj._created_components_map = {mock_cls: mock_instance}

        await tst_obj.shut_down_component(component_cls=mock_cls)

    async def test_shut_down_component_missed(self):
        """Checks the shut_down_component method with missed component case."""
        mock_cls = Mock()
        tst_obj = self.build_tst_obj()

        await tst_obj.shut_down_component(component_cls=mock_cls)

    def test_get_components(self):
        """Checks the get_components method."""
        mock_cls = Mock()
        mock_instance = Mock()
        tst_obj = self.build_tst_obj()
        tst_obj._created_components_map = {mock_cls: mock_instance}

        tst_res = tst_obj.get_components()

        assert tst_res == [mock_instance]

    def test_create_command(self):
        """Checks the create_command method."""
        mock_base_cls = Mock()
        mock_instance = Mock()
        mock_final_cls = Mock()
        mock_final_cls.create = Mock(return_value=mock_instance)
        tst_obj = self.build_tst_obj()
        tst_obj._final_commands_classes_map = {mock_base_cls: mock_final_cls}

        tst_res = tst_obj.create_command(command_cls=mock_base_cls)

        assert tst_res == mock_instance
        mock_final_cls.create.assert_called_once_with(
            unit=tst_obj, params=tst_obj.creating_params
        )

    def test_create_command_error(self):
        """Checks the create_command method for unregistered component class case."""
        mock_base_cls = Mock()
        mock_final_cls = Mock()
        tst_obj = self.build_tst_obj()
        tst_obj._final_commands_classes_map = {mock_base_cls: mock_final_cls}
        mock_wrong_cls = Mock()
        mock_wrong_cls.__name__ = "Wrong"

        with self.assertRaises(TypeError):
            tst_obj.create_command(command_cls=mock_wrong_cls)
