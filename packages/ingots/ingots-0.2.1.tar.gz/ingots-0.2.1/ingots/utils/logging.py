__all__ = (
    "configure_startup_logging",
    "STARTUP_LOGGING_FORMAT",
    "INGOTS_LOGGING_MARKER",
    "ContextVarsFilter",
)

import argparse
import contextvars
import logging
import typing as t

if t.TYPE_CHECKING:
    ...


STARTUP_LOGGING_FORMAT = (
    "%(levelname)s ▶ %(message)s ▶ %(name)s:%(funcName)s:%(lineno)s"
)
INGOTS_LOGGING_MARKER = "◈◈◈"


def configure_startup_logging(
    level_cli_argument: str = "startup-log-level",
    default_level: int = logging.INFO,
    **kwargs,
):
    parser = argparse.ArgumentParser(add_help=False)
    parser.add_argument(
        f"--{level_cli_argument}", dest="startup_log_level", default=default_level
    )
    namespace, _ = parser.parse_known_args()

    kwargs.setdefault("force", True)
    kwargs.setdefault("level", namespace.startup_log_level)
    kwargs.setdefault("format", STARTUP_LOGGING_FORMAT)
    logging.basicConfig(**kwargs)


class ContextVarsFilter(logging.Filter):

    def filter(self, record: "logging.LogRecord") -> bool:
        ctx = contextvars.copy_context()
        record.ctx = dict(ctx.items())
        return True
