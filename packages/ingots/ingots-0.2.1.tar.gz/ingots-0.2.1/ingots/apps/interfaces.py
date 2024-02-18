__all__ = (
    "CommandInterface",
    "ComponentInterface",
    "UnitInterface",
    "ApplicationInterface",
    "ApplicationRunnerInterface",
)

import typing as t

if t.TYPE_CHECKING:
    ...


CreatingParamsTypeVar = t.TypeVar("CreatingParamsTypeVar")
CommandTypeVar = t.TypeVar("CommandTypeVar", bound="CommandInterface")
ComponentTypeVar = t.TypeVar("ComponentTypeVar", bound="ComponentInterface")
UnitTypeVar = t.TypeVar("UnitTypeVar", bound="UnitInterface")
ApplicationTypeVar = t.TypeVar("ApplicationTypeVar", bound="ApplicationInterface")


class CommandInterface(
    t.Generic[CreatingParamsTypeVar, ApplicationTypeVar, UnitTypeVar]
):
    creating_params: CreatingParamsTypeVar
    application: ApplicationTypeVar
    unit: UnitTypeVar

    @classmethod
    def create(cls, unit: UnitTypeVar, params: CreatingParamsTypeVar) -> t.Self:
        raise NotImplementedError(f"{cls.__name__}.create")

    async def run(self):
        raise NotImplementedError(f"{self.__class__.__name__}.run")

    async def cancel_running(self):
        raise NotImplementedError(f"{self.__class__.__name__}.cancel_running")


class ComponentInterface(
    t.Generic[CreatingParamsTypeVar, ApplicationTypeVar, UnitTypeVar],
):
    creating_params: CreatingParamsTypeVar
    application: ApplicationTypeVar
    unit: UnitTypeVar
    shut_down_order: int

    @classmethod
    def prepare_final_classes(cls):
        raise NotImplementedError(f"{cls.__name__}.prepare_final_classes")

    @classmethod
    def create(cls, unit: UnitTypeVar, params: CreatingParamsTypeVar) -> t.Self:
        raise NotImplementedError(f"{cls.__name__}.create")

    async def configure(self):
        raise NotImplementedError(f"{self.__class__.__name__}.configure")

    async def shut_down(self):
        raise NotImplementedError(f"{self.__class__.__name__}.shut_down")


class UnitInterface(
    t.Generic[
        CreatingParamsTypeVar,
        ApplicationTypeVar,
        ComponentTypeVar,
        CommandTypeVar,
    ],
):
    creating_params: CreatingParamsTypeVar
    application: ApplicationTypeVar

    @classmethod
    def prepare_final_classes(cls):
        raise NotImplementedError(f"{cls.__name__}.prepare_final_classes")

    @classmethod
    def register_components_classes(cls) -> set[type[ComponentTypeVar]]:
        raise NotImplementedError(f"{cls.__name__}.register_components_classes")

    @classmethod
    def register_components_extensions(cls) -> set[type[ComponentTypeVar]]:
        raise NotImplementedError(f"{cls.__name__}.register_components_extensions")

    @classmethod
    def get_components_classes(cls) -> list[type[ComponentTypeVar]]:
        raise NotImplementedError(f"{cls.__name__}.get_components_classes")

    @classmethod
    def register_commands_classes(cls) -> set[type[CommandTypeVar]]:
        raise NotImplementedError(f"{cls.__name__}.register_commands_classes")

    @classmethod
    def register_commands_extensions(cls) -> set[type[CommandTypeVar]]:
        raise NotImplementedError(f"{cls.__name__}.register_commands_extensions")

    @classmethod
    def get_commands_classes(cls) -> list[type[CommandTypeVar]]:
        raise NotImplementedError(f"{cls.__name__}.get_commands_classes")

    @classmethod
    def create(
        cls, application: ApplicationTypeVar, params: CreatingParamsTypeVar
    ) -> t.Self:
        raise NotImplementedError(f"{cls.__name__}.create")

    async def configure(self):
        raise NotImplementedError(f"{self.__class__.__name__}.configure")

    async def get_component(
        self, component_cls: type[ComponentTypeVar]
    ) -> ComponentTypeVar:
        raise NotImplementedError(f"{self.__class__.__name__}.get_component")

    def create_component(
        self, component_cls: type[ComponentTypeVar]
    ) -> ComponentTypeVar:
        raise NotImplementedError(f"{self.__class__.__name__}.create_component")

    async def shut_down_component(self, component_cls: type[ComponentTypeVar]):
        raise NotImplementedError(f"{self.__class__.__name__}.shut_down_component")

    def get_components(self) -> list[ComponentTypeVar]:
        raise NotImplementedError(f"{self.__class__.__name__}.get_components")

    def create_command(self, command_cls: type[CommandTypeVar]) -> CommandTypeVar:
        raise NotImplementedError(f"{self.__class__.__name__}.create_command")


class ApplicationInterface(
    t.Generic[CreatingParamsTypeVar, UnitTypeVar],
):
    creating_params: CreatingParamsTypeVar

    @classmethod
    def prepare_final_classes(cls):
        raise NotImplementedError(f"{cls.__name__}.prepare_final_classes")

    @classmethod
    def register_units_classes(cls) -> set[type[UnitTypeVar]]:
        raise NotImplementedError(f"{cls.__name__}.register_units_classes")

    @classmethod
    def register_units_extensions(cls) -> set[type[UnitTypeVar]]:
        raise NotImplementedError(f"{cls.__name__}.register_units_extensions")

    @classmethod
    def get_units_classes(cls) -> list[type[UnitTypeVar]]:
        raise NotImplementedError(f"{cls.__name__}.get_units_classes")

    @classmethod
    def create(cls, params: CreatingParamsTypeVar) -> t.Self:
        raise NotImplementedError(f"{cls.__name__}.create")

    async def configure(self):
        raise NotImplementedError(f"{self.__class__.__name__}.configure")

    async def get_unit(self, unit_cls: type[UnitTypeVar]) -> UnitTypeVar:
        raise NotImplementedError(f"{self.__class__.__name__}.get_unit")

    def create_unit(self, unit_cls: type[UnitTypeVar]) -> UnitTypeVar:
        raise NotImplementedError(f"{self.__class__.__name__}.create_unit")

    def get_units(self) -> list[UnitTypeVar]:
        raise NotImplementedError(f"{self.__class__.__name__}.get_units")

    async def shut_down(self):
        raise NotImplementedError(f"{self.__class__.__name__}.shut_down")


class ApplicationRunnerInterface(t.Generic[CreatingParamsTypeVar, ApplicationTypeVar]):
    application: ApplicationTypeVar
    creating_params: CreatingParamsTypeVar

    def prepare_creating_params(self) -> CreatingParamsTypeVar:
        raise NotImplementedError(f"{self.__class__.__name__}.prepare_creating_params")

    def create_application(self) -> ApplicationTypeVar:
        raise NotImplementedError(f"{self.__class__.__name__}.create_application")
