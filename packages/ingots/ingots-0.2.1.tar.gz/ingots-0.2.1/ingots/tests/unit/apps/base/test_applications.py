__all__ = ("BaseApplicationTestCase",)

import typing as t
from unittest.mock import AsyncMock, Mock, patch

from ingots.apps.base.applications import BaseApplication
from ingots.tests.unit.apps import test_interfaces

if t.TYPE_CHECKING:
    ...


TestedClassTypeVar = t.TypeVar("TestedClassTypeVar", bound=BaseApplication)


class BaseApplicationTestCase(
    test_interfaces.ApplicationInterfaceTestCase[TestedClassTypeVar],
    t.Generic[TestedClassTypeVar],
):
    """Contains tests for BaseApplication class."""

    tst_cls: type[TestedClassTypeVar] = BaseApplication

    def get_tst_obj_init_params(self, **kwargs) -> dict:
        kwargs.setdefault("params", Mock())
        return super().get_tst_obj_init_params(**kwargs)

    def test_prepare_final_classes(self):
        """Checks the prepare_class class method."""
        mock_classes_builder_build_res = Mock()
        mock_classes_builder = Mock()
        mock_classes_builder.build = Mock(return_value=mock_classes_builder_build_res)
        mock_classes_builder_cls = Mock(return_value=mock_classes_builder)
        mock_register_units_classes_res = Mock()
        mock_register_units_extensions_res = Mock()
        mock_unit_cls = Mock()
        mock_unit_cls.prepare_final_classes = Mock()

        tst_cls = self.build_tst_cls()
        tst_cls.register_units_classes = Mock(
            return_value=mock_register_units_classes_res
        )
        tst_cls.register_units_extensions = Mock(
            return_value=mock_register_units_extensions_res
        )
        tst_cls.get_units_classes = Mock(return_value=[mock_unit_cls])
        with patch(
            "ingots.apps.base.applications.FinalClassesBuilder"
        ) as mock_classes_builder_generic_cls:
            mock_classes_builder_generic_cls.__getitem__ = Mock(
                return_value=mock_classes_builder_cls
            )
            tst_cls.prepare_final_classes()

        tst_cls.register_units_classes.assert_called_once_with()
        tst_cls.register_units_extensions.assert_called_once_with()
        mock_classes_builder_cls.assert_called_once_with(
            container=tst_cls,
            nested="Units",
            base_classes=mock_register_units_classes_res,
            extensions=mock_register_units_extensions_res,
        )
        mock_classes_builder.build.assert_called_once_with()
        assert tst_cls._final_units_classes_map == mock_classes_builder_build_res
        tst_cls.get_units_classes.assert_called_once_with()
        mock_unit_cls.prepare_final_classes.assert_called_once_with()

    def test_register_units_classes(self):
        """Checks the register_units_classes class method."""
        tst_res = self.tst_cls.register_units_classes()

        assert isinstance(tst_res, set)
        assert len(tst_res) == 0

    def test_register_units_extensions(self):
        """Checks the register_units_extensions class method."""
        tst_res = self.tst_cls.register_units_extensions()

        assert isinstance(tst_res, set)
        assert len(tst_res) == 0

    def test_get_units_classes(self):
        """Checks the get_units_classes class method."""
        mock_base_cls = Mock()
        mock_final_cls = Mock()
        tst_cls = self.build_tst_cls()
        tst_cls._final_units_classes_map = {mock_base_cls: mock_final_cls}

        tst_res = tst_cls.get_units_classes()

        assert tst_res == [mock_final_cls]

    def test_create(self):
        """Checks the create class method."""
        tst_obj = self.tst_cls.create(params=Mock())

        assert isinstance(tst_obj, self.tst_cls)

    def test_init(self):
        """Checks the __init__ method."""
        mock_params = Mock()

        tst_obj = self.build_tst_obj(params=mock_params)

        assert tst_obj.creating_params == mock_params
        assert tst_obj._created_units_map == {}

    async def test_get_unit(self):
        """Checks get_unit async method."""
        mock_cls = Mock()
        mock_instance = Mock()
        mock_instance.configure = AsyncMock()
        tst_obj = self.build_tst_obj()
        tst_obj.create_unit = Mock(return_value=mock_instance)

        tst_res = await tst_obj.get_unit(unit_cls=mock_cls)

        assert tst_res == mock_instance
        tst_obj.create_unit.assert_called_once_with(unit_cls=mock_cls)
        mock_instance.configure.assert_awaited_once_with()
        assert tst_obj._created_units_map == {mock_cls: mock_instance}

    def test_create_unit(self):
        """Checks the create_unit method."""
        mock_base_cls = Mock()
        mock_instance = Mock()
        mock_final_cls = Mock()
        mock_final_cls.create = Mock(return_value=mock_instance)
        tst_obj = self.build_tst_obj()
        tst_obj._final_units_classes_map = {mock_base_cls: mock_final_cls}

        tst_res = tst_obj.create_unit(unit_cls=mock_base_cls)

        assert tst_res == mock_instance
        mock_final_cls.create.assert_called_once_with(
            application=tst_obj, params=tst_obj.creating_params
        )

    def test_create_unit_error(self):
        """Checks the create_unit method for unregistered unit class case."""
        mock_base_cls = Mock()
        mock_final_cls = Mock()
        tst_obj = self.build_tst_obj()
        tst_obj._final_units_classes_map = {mock_base_cls: mock_final_cls}
        mock_wrong_cls = Mock()
        mock_wrong_cls.__name__ = "Wrong"

        with self.assertRaises(TypeError):
            tst_obj.create_unit(unit_cls=mock_wrong_cls)

    def test_get_units(self):
        """Checks the get_units method."""
        mock_cls = Mock()
        mock_instance = Mock()
        tst_obj = self.build_tst_obj()
        tst_obj._created_units_map = {mock_cls: mock_instance}

        tst_res = tst_obj.get_units()

        assert tst_res == [mock_instance]

    async def test_shut_down(self):
        """Checks the shut_down async method."""
        mock_chunk = Mock()
        tst_obj = self.build_tst_obj()
        tst_obj.get_components_chunks_for_shutting_down = Mock(
            return_value=[mock_chunk]
        )
        tst_obj.shut_down_component_chunk = AsyncMock()

        await tst_obj.shut_down()

        tst_obj.get_components_chunks_for_shutting_down.assert_called_once_with()
        tst_obj.shut_down_component_chunk.assert_awaited_once_with(chunk=mock_chunk)

    def test_get_components_chunks_for_shutting_down(self):
        """Checks the get_components_chunks_for_shutting_down method."""
        mock_component_1 = Mock(shut_down_order=0)
        mock_component_2 = Mock(shut_down_order=1)
        mock_unit = Mock()
        mock_unit.get_components = Mock(
            return_value=[mock_component_2, mock_component_1]
        )

        tst_obj = self.build_tst_obj()
        tst_obj.get_units = Mock(return_value=[mock_unit])

        tst_res = tst_obj.get_components_chunks_for_shutting_down()

        tst_obj.get_units.assert_called_once_with()
        mock_unit.get_components.assert_called_once_with()
        assert tst_res == [[mock_component_1], [mock_component_2]]

    async def test_shut_down_component_chunk(self):
        """Checks the shut_down_component_chunk async method."""
        mock_component_1_shut_down_coro = Mock()
        mock_component_1 = Mock()
        mock_component_1.shut_down = Mock(return_value=mock_component_1_shut_down_coro)
        mock_component_2_shut_down_coro = Mock()
        mock_component_2 = Mock()
        mock_component_2.shut_down = Mock(return_value=mock_component_2_shut_down_coro)
        tst_obj = self.build_tst_obj()
        mock_gather = AsyncMock(return_value=[None, Exception("Test")])

        with patch("ingots.apps.base.applications.gather", mock_gather):
            await tst_obj.shut_down_component_chunk(
                chunk=[mock_component_1, mock_component_2]
            )

        mock_component_1.shut_down.assert_called_once_with()
        mock_component_2.shut_down.assert_called_once_with()
        mock_gather.assert_called_once_with(
            mock_component_1_shut_down_coro,
            mock_component_2_shut_down_coro,
            return_exceptions=True,
        )
