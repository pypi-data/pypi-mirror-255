__all__ = ("BaseUnit",)

import logging
import typing as t

from ingots.apps.interfaces import UnitInterface
from ingots.utils.classes_builder import BuildClassInterface, FinalClassesBuilder

if t.TYPE_CHECKING:
    from .applications import BaseApplication
    from .commands import BaseCommand
    from .components import BaseComponent


logger = logging.getLogger(__name__)

CreatingParamsTypeVar = t.TypeVar("CreatingParamsTypeVar")
ApplicationTypeVar = t.TypeVar("ApplicationTypeVar", bound="BaseApplication")
ComponentTypeVar = t.TypeVar("ComponentTypeVar", bound="BaseComponent")
CommandTypeVar = t.TypeVar("CommandTypeVar", bound="BaseCommand")


class BaseUnit(
    BuildClassInterface,
    UnitInterface[
        CreatingParamsTypeVar,
        ApplicationTypeVar,
        ComponentTypeVar,
        CommandTypeVar,
    ],
    t.Generic[
        CreatingParamsTypeVar,
        ApplicationTypeVar,
        ComponentTypeVar,
        CommandTypeVar,
    ],
):
    build_class_extensions_order = 5
    _final_components_classes_map: dict[type[ComponentTypeVar], type[ComponentTypeVar]]
    _final_commands_classes_map: dict[type[CommandTypeVar], type[CommandTypeVar]]

    @classmethod
    def prepare_final_classes(cls):
        cls._final_components_classes_map = FinalClassesBuilder[ComponentTypeVar](
            container=cls,
            nested="Components",
            base_classes=cls.register_components_classes(),
            extensions=cls.register_components_extensions(),
        ).build()
        cls._final_commands_classes_map = FinalClassesBuilder[CommandTypeVar](
            container=cls,
            nested="Commands",
            base_classes=cls.register_commands_classes(),
            extensions=cls.register_commands_extensions(),
        ).build()
        for component_cls in cls.get_components_classes():
            component_cls.prepare_final_classes()

    @classmethod
    def register_components_classes(cls) -> set[type[ComponentTypeVar]]:
        return set()

    @classmethod
    def register_components_extensions(cls) -> set[type[ComponentTypeVar]]:
        return set()

    @classmethod
    def get_components_classes(cls) -> list[type[ComponentTypeVar]]:
        return [i for i in cls._final_components_classes_map.values()]

    @classmethod
    def register_commands_classes(cls) -> set[type[CommandTypeVar]]:
        return set()

    @classmethod
    def register_commands_extensions(cls) -> set[type[CommandTypeVar]]:
        return set()

    @classmethod
    def get_commands_classes(cls) -> list[type[CommandTypeVar]]:
        return [i for i in cls._final_commands_classes_map.values()]

    @classmethod
    def create(
        cls, application: ApplicationTypeVar, params: CreatingParamsTypeVar
    ) -> t.Self:
        return cls(application=application, params=params)

    def __init__(self, application: ApplicationTypeVar, params: CreatingParamsTypeVar):
        self.application = application
        self.creating_params = params
        self._created_components_map: dict[type[ComponentTypeVar], ComponentTypeVar] = (
            {}
        )

    async def get_component(
        self, component_cls: type[ComponentTypeVar]
    ) -> ComponentTypeVar:
        try:
            return self._created_components_map[component_cls]
        except KeyError:
            instance = self.create_component(component_cls=component_cls)
            await instance.configure()
            self._created_components_map[component_cls] = instance
            return instance

    def create_component(
        self, component_cls: type[ComponentTypeVar]
    ) -> ComponentTypeVar:
        try:
            final_cls = self._final_components_classes_map[component_cls]
        except KeyError:
            logger.error(
                "Unregistered Component class: %r. Registered: %r.",
                component_cls,
                self._final_components_classes_map.keys(),
            )
            raise TypeError(f"Unregistered Component class {component_cls.__name__}")

        instance = final_cls.create(unit=self, params=self.creating_params)
        logger.info("Created component: %r.", instance)
        return instance

    async def shut_down_component(self, component_cls: type[ComponentTypeVar]):
        instance = self._created_components_map.pop(component_cls, None)
        if not instance:
            return

        try:
            await instance.shut_down()
        except Exception as err:
            logger.warning(
                "Shutdown component error: %r. Component: %r.", err, instance
            )
        else:
            logger.info("Shutdown component: %r.", instance)

    def get_components(self) -> list[ComponentTypeVar]:
        return [i for i in self._created_components_map.values()]

    def create_command(self, command_cls: type[CommandTypeVar]) -> CommandTypeVar:
        try:
            final_cls = self._final_commands_classes_map[command_cls]
        except KeyError:
            logger.error(
                "Unregistered Command class: %r. Registered: %r.",
                command_cls,
                self._final_commands_classes_map.keys(),
            )
            raise TypeError(f"Unregistered Command class {command_cls.__name__}")

        instance = final_cls.create(unit=self, params=self.creating_params)
        logger.info("Created command: %r.", instance)
        return instance
