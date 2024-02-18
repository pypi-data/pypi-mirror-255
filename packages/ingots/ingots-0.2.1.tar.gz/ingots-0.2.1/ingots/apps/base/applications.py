__all__ = ("BaseApplication",)

import logging
import typing as t
from asyncio.tasks import gather
from collections import defaultdict

from ingots.apps.interfaces import ApplicationInterface
from ingots.utils.classes_builder import FinalClassesBuilder

if t.TYPE_CHECKING:
    from .components import BaseComponent
    from .units import BaseUnit


logger = logging.getLogger(__name__)

CreatingParamsTypeVar = t.TypeVar("CreatingParamsTypeVar")
UnitTypeVar = t.TypeVar("UnitTypeVar", bound="BaseUnit")
ComponentTypeVar = t.TypeVar("ComponentTypeVar", bound="BaseComponent")


class BaseApplication(
    ApplicationInterface[CreatingParamsTypeVar, UnitTypeVar],
    t.Generic[CreatingParamsTypeVar, UnitTypeVar, ComponentTypeVar],
):
    _final_units_classes_map: dict[type[UnitTypeVar], type[UnitTypeVar]]

    @classmethod
    def prepare_final_classes(cls):
        cls._final_units_classes_map = FinalClassesBuilder[UnitTypeVar](
            container=cls,
            nested="Units",
            base_classes=cls.register_units_classes(),
            extensions=cls.register_units_extensions(),
        ).build()
        for unit_cls in cls.get_units_classes():
            unit_cls.prepare_final_classes()

    @classmethod
    def register_units_classes(cls) -> set[type[UnitTypeVar]]:
        return set()

    @classmethod
    def register_units_extensions(cls) -> set[type[UnitTypeVar]]:
        return set()

    @classmethod
    def get_units_classes(cls) -> list[type[UnitTypeVar]]:
        return [i for i in cls._final_units_classes_map.values()]

    @classmethod
    def create(cls, params: CreatingParamsTypeVar) -> t.Self:
        return cls(params=params)

    def __init__(self, params: CreatingParamsTypeVar):
        self.creating_params = params
        self._created_units_map: dict[type[UnitTypeVar], UnitTypeVar] = {}

    async def get_unit(self, unit_cls: type[UnitTypeVar]) -> UnitTypeVar:
        try:
            return self._created_units_map[unit_cls]
        except KeyError:
            instance = self.create_unit(unit_cls=unit_cls)
            await instance.configure()
            self._created_units_map[unit_cls] = instance
            return instance

    def create_unit(self, unit_cls: type[UnitTypeVar]) -> UnitTypeVar:
        try:
            final_cls = self._final_units_classes_map[unit_cls]
        except KeyError:
            logger.error(
                "Unregistered Unit class: %r. Registered: %r.",
                unit_cls,
                self._final_units_classes_map.keys(),
            )
            raise TypeError(f"Unregistered Unit class {unit_cls.__name__}")

        instance = final_cls.create(application=self, params=self.creating_params)
        logger.info("Created unit: %r.", instance)
        return instance

    def get_units(self) -> list[UnitTypeVar]:
        return [i for i in self._created_units_map.values()]

    async def shut_down(self):
        chunks = self.get_components_chunks_for_shutting_down()
        for chunk in chunks:
            logger.debug("Shutting down components chunk: %r.", chunk)
            await self.shut_down_component_chunk(chunk=chunk)

    def get_components_chunks_for_shutting_down(self) -> list[list[ComponentTypeVar]]:
        ordered_components_map: dict[int, list[ComponentTypeVar]] = defaultdict(list)
        for unit in self.get_units():
            for component in unit.get_components():
                ordered_components_map[component.shut_down_order].append(component)

        shut_down_ordered_components = []
        for number in sorted(ordered_components_map):
            shut_down_ordered_components.append(ordered_components_map[number])

        return shut_down_ordered_components

    async def shut_down_component_chunk(self, chunk: list[ComponentTypeVar]):
        results = await gather(
            *[cmp.shut_down() for cmp in chunk], return_exceptions=True
        )
        for cmp, result in zip(chunk, results):
            if isinstance(result, Exception):
                logger.warning(
                    "Shutdown component error: %r. Component: %r.", result, cmp
                )
            else:
                logger.info("Shutdown component: %r.", cmp)
