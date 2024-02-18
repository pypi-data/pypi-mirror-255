__all__ = ("BaseApplicationRunnerTestCase",)

import typing as t
from unittest.mock import Mock

from ingots.apps.base.runners import BaseApplicationRunner
from ingots.tests.unit.apps import test_interfaces

if t.TYPE_CHECKING:
    ...


TestedClassTypeVar = t.TypeVar("TestedClassTypeVar", bound=BaseApplicationRunner)


class BaseApplicationRunnerTestCase(
    test_interfaces.ApplicationRunnerInterfaceTestCase[TestedClassTypeVar],
    t.Generic[TestedClassTypeVar],
):
    """Contains tests for BaseApplicationRunner class."""

    tst_cls: type[TestedClassTypeVar] = BaseApplicationRunner

    def get_tst_obj_init_params(self, **kwargs) -> dict:
        kwargs.setdefault("application_cls", Mock())
        return super().get_tst_obj_init_params(**kwargs)

    def test_init(self):
        """Checks the __init__ method."""
        mock_application_cls = Mock()
        mock_application_cls.prepare_final_classes = Mock()

        tst_obj = self.build_tst_obj(application_cls=mock_application_cls)

        assert tst_obj.application_cls == mock_application_cls
        mock_application_cls.prepare_final_classes.assert_called_once_with()

    def test_create_application(self):
        """Checks the create_application method."""
        mock_application = Mock()
        mock_application_cls = Mock()
        mock_application_cls.create = Mock(return_value=mock_application)
        tst_obj = self.build_tst_obj()
        tst_obj.application_cls = mock_application_cls
        tst_obj.creating_params = Mock()

        tst_res = tst_obj.create_application()

        assert tst_res == mock_application
        mock_application_cls.create.assert_called_once_with(
            params=tst_obj.creating_params
        )
