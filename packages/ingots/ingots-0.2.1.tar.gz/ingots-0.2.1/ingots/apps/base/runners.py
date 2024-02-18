__all__ = ("BaseApplicationRunner",)

import logging
import typing as t

from ingots.apps.interfaces import ApplicationRunnerInterface

if t.TYPE_CHECKING:
    from .applications import BaseApplication


logger = logging.getLogger(__name__)

CreatingParamsTypeVar = t.TypeVar("CreatingParamsTypeVar")
ApplicationTypeVar = t.TypeVar("ApplicationTypeVar", bound="BaseApplication")


class BaseApplicationRunner(
    ApplicationRunnerInterface[CreatingParamsTypeVar, ApplicationTypeVar],
    t.Generic[CreatingParamsTypeVar, ApplicationTypeVar],
):
    def __init__(self, application_cls: type[ApplicationTypeVar]):
        self.application_cls = application_cls
        self.application_cls.prepare_final_classes()

    def create_application(self) -> ApplicationTypeVar:
        instance = self.application_cls.create(params=self.creating_params)
        logger.info(
            "Created application: %r.",
            instance,
        )
        return instance
