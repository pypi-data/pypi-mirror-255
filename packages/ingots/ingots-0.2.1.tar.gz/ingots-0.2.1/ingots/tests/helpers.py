"""Helpers for preparing unit tests.

The package contains utils and extensions for unittest package.
"""

__all__ = (
    "AwaitMock",
    "ClassTesting",
    "ClassTestingTestCase",
)

import typing as t
from unittest import IsolatedAsyncioTestCase
from unittest.mock import NonCallableMagicMock

if t.TYPE_CHECKING:
    ...

TestedClassTypeVar = t.TypeVar("TestedClassTypeVar")


class ClassTesting(t.Generic[TestedClassTypeVar]):
    tst_meta = type
    tst_cls: type[TestedClassTypeVar]

    def build_tst_cls(
        self,
        tst_meta: t.Optional[type] = None,
        name: t.Optional[str] = None,
        bases: t.Optional[tuple] = None,
        namespace: t.Optional[dict] = None,
    ) -> type[TestedClassTypeVar]:
        """Builds a test class.
        Use in setUp methods for building default tests classes.
        Use in any test methods for creating a custom test class.
        """
        tst_meta = tst_meta or self.tst_meta
        name = name or self.tst_cls.__name__
        bases = bases or (self.tst_cls,)
        namespace = namespace or {}
        return tst_meta(name, bases, namespace)

    def build_tst_obj(
        self, tst_cls: t.Optional[type[TestedClassTypeVar]] = None, **kwargs
    ) -> TestedClassTypeVar:
        """Creates a test instance.
        Use in setUp methods building default tests instances.
        Use in any test methods for creating a custom test instance.
        """
        tst_cls = tst_cls or self.tst_cls
        return tst_cls(**self.get_tst_obj_init_params(**kwargs))

    def get_tst_obj_init_params(self, **kwargs) -> dict:
        return kwargs


class ClassTestingTestCase(
    ClassTesting[TestedClassTypeVar],
    IsolatedAsyncioTestCase,
    t.Generic[TestedClassTypeVar],
):
    """Provides generic approach for creating tests for classes and instances in test
    cases."""


class AwaitMock(NonCallableMagicMock):
    def __await__(self):
        self.call_count += 1
        return self.await_return_value().__await__()

    async def await_return_value(self):
        if self.side_effect:
            raise self.side_effect
        return self.return_value
