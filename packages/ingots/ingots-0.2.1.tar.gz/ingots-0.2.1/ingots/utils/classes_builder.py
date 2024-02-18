__all__ = (
    "FinalClassesBuilder",
    "BuildClassInterface",
)

import logging
import typing as t

if t.TYPE_CHECKING:
    ...


logger = logging.getLogger(__name__)


class BuildClassInterface:
    build_class_extensions_order: int


BuildClassTypeVar = t.TypeVar("BuildClassTypeVar", bound=BuildClassInterface)


class FinalClassesBuilder(t.Generic[BuildClassTypeVar]):
    def __init__(
        self,
        container: type,
        nested: str,
        base_classes: set[type[BuildClassTypeVar]],
        extensions: set[type["BuildClassTypeVar"]],
        prefix: str = "Final",
    ):
        self.container = container
        self.nested = nested
        self.base_classes = base_classes
        self.extensions = extensions
        self.prefix = prefix

    def build(self) -> dict[type[BuildClassTypeVar], type[BuildClassTypeVar]]:
        extensions_map = self.build_extensions_map()
        logger.debug(
            "Container: %r. %s classes and extensions map: %r.",
            self.container,
            self.nested,
            extensions_map,
        )

        final_classes_map = {}
        for base_cls, cls_extensions in extensions_map.items():
            if cls_extensions:
                final_cls = self.build_final_cls(
                    base_cls=base_cls, extensions=cls_extensions
                )
                final_classes_map[base_cls] = final_cls
            else:
                final_classes_map[base_cls] = base_cls

        return final_classes_map

    def build_extensions_map(
        self,
    ) -> dict[type[BuildClassTypeVar], list[type[BuildClassTypeVar]]]:
        extensions_map: dict[type[BuildClassTypeVar], list[type[BuildClassTypeVar]]] = (
            {}
        )
        for base_cls in self.base_classes:
            extensions_map[base_cls] = []

        for ext_cls in self.extensions:
            for base_cls, cls_extensions in extensions_map.items():
                if issubclass(ext_cls, base_cls):
                    cls_extensions.append(ext_cls)

        return extensions_map

    def build_final_cls(
        self,
        base_cls: type[BuildClassTypeVar],
        extensions: list[type[BuildClassTypeVar]],
    ) -> type[BuildClassTypeVar]:
        extensions.sort(key=lambda i: i.build_class_extensions_order)
        bases = tuple(extensions) + (base_cls,)
        final_cls: type[ClassTypeVar] = type(  # type: ignore
            f"{self.prefix}{base_cls.__name__}", bases, {}
        )
        logger.debug(
            "Generated final class for: %r. MRO: %r.", base_cls, final_cls.__mro__
        )
        return final_cls
