from abc import ABC, abstractmethod
import asyncio
from navconfig import config
from navconfig.logging import logging
from flowtask.utils import cPrint
from flowtask.hooks.interfaces.mask import MaskSupport


class AbstractEvent(MaskSupport, ABC):
    def __init__(self, *args, **kwargs):
        self.disable_notification: bool = kwargs.pop("disable_notification", False)
        super(AbstractEvent, self).__init__(*args, **kwargs)
        self._environment = config
        try:
            self._name_ = kwargs["name"]
        except KeyError:
            self._name_ = self.__class__.__name__
        self._logger = logging.getLogger(f"FlowTask.Event.{self._name_}")
        # program
        self._program = kwargs.pop("program", "navigator")
        try:
            self._loop = asyncio.get_running_loop()
        except RuntimeError:
            raise RuntimeError("Event must be called from an Asyncio Event Loop")
        self._task = kwargs.pop("task", None)
        self._args = args
        self._kwargs = kwargs
        # set the attributes of Action:
        for arg, val in kwargs.items():
            try:
                setattr(self, arg, val)
            except Exception as err:
                self._logger.warning(f"Wrong Attribute: {arg}={val}")
                self._logger.error(err)

    @abstractmethod
    async def __call__(self):
        """Called when event is dispatched."""

    def echo(self, message: str, level: str = "INFO"):
        cPrint(message, level=level)

    def __repr__(self) -> str:
        return f"Event.{self.__class__.__name__}()"

    def name(self):
        return self._name_
