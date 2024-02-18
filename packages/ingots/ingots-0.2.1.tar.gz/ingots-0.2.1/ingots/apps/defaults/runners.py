__all__ = ("ApplicationRunner",)

import logging
import typing as t
from asyncio.events import set_event_loop_policy

from uvloop import EventLoopPolicy

from ingots.apps.cli import CliApplicationRunner

if t.TYPE_CHECKING:
    from .applications import Application


logger = logging.getLogger(__name__)


ApplicationTypeVar = t.TypeVar("ApplicationTypeVar", bound="Application")


class ApplicationRunner(
    CliApplicationRunner[ApplicationTypeVar],
    t.Generic[ApplicationTypeVar],
):
    def prepare_asyncio(self):
        set_event_loop_policy(EventLoopPolicy())
