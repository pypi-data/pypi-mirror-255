"""RESTBase.

Basic component for making RESTful queries to URLs.
"""
import asyncio
from abc import ABC
from typing import List, Dict, Union
from collections.abc import Callable
from ..exceptions import DataNotFound, ComponentError
from .abstract import DtComponent


class BaseAction(DtComponent, ABC):
    """
    BaseAction.

    Overview

         Working with Components with multiple methods.

    .. table:: Properties
       :widths: auto

    """

    def __init__(
        self,
        loop: asyncio.AbstractEventLoop = None,
        job: Callable = None,
        stat: Callable = None,
        **kwargs,
    ) -> None:
        """Init Method."""
        self._result: Union[List, Dict] = None
        self._method: str = kwargs.pop("method", None)
        super(BaseAction, self).__init__(loop=loop, job=job, stat=stat, **kwargs)
        args = self._attrs.get("args", {})
        keys_to_remove = ["loop", "stat", "debug", "memory", "comment", "Group"]
        self._kwargs = {k: v for k, v in args.items() if k not in keys_to_remove}

    async def start(self, **kwargs):
        if not hasattr(self, self._method):
            raise ComponentError(f"{self.__name__} Error: has no Method {self._method}")
        # Getting the method to be called
        self._fn = getattr(self, self._method)
        await super(BaseAction, self).start(**kwargs)
        # Processing Variables:
        self._kwargs = self.var_replacement(self._kwargs)
        return True

    async def close(self):
        pass

    async def run(self):
        try:
            result, error = await self._fn(**self._kwargs)
            if error:
                self._logger.warning(
                    f"Error {self.__name__}.{self._fn.__name__}: {error}"
                )
                return False
            if result is None:
                raise DataNotFound(
                    f"No data found for {self.__name__}.{self._fn.__name__}"
                )
            self._result = result
            self.add_metric(f"{self.__name__}.{self._fn.__name__}", result)
        except DataNotFound:
            raise
        except Exception as e:
            raise ComponentError(f"Error running {self.__name__}: {e}")
        return self._result
