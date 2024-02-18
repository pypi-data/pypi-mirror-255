__all__ = ()

import logging
import typing as t
from unittest import TestCase

from ingots.tests.helpers import ClassTestingTestCase
from ingots.utils.logging import ContextVarsFilter, configure_startup_logging


class ConfigureStartupLoggingTestCase(TestCase):
    """Contains tests for configure_startup_logging function."""

    def test(self):
        """Checks the configure_startup_logging function."""
        configure_startup_logging()


TestedClassTypeVar = t.TypeVar("TestedClassTypeVar", bound=ContextVarsFilter)


class ContextVarsFilterTestCase(ClassTestingTestCase[TestedClassTypeVar]):
    """Contains tests for ContextVarsFilter class."""

    tst_cls = ContextVarsFilter

    def test_filter(self):
        """Checks the filter method."""
        tst_obj = self.build_tst_obj()
        tst_log_record = logging.makeLogRecord({})

        tst_res = tst_obj.filter(record=tst_log_record)

        assert tst_res is True
        assert hasattr(tst_log_record, "ctx")
        assert tst_log_record.ctx == {}
