from typing import Any, Union, ParamSpec
from abc import ABC, abstractmethod
from navconfig.logging import logging


P = ParamSpec("P")


class BaseDataframe(ABC):
    def __init__(self, *args: P.args, **kwargs: P.kwargs):
        self._debug = kwargs.get("debug", False)
        self.to_string: bool = kwargs.get("to_string", True)
        if not hasattr(self, "_logger"):
            self._logger = logging.getLogger(__name__)
        if not hasattr(self, "_variables"):
            self._variables = {}

    def add_metric(self, name, value):
        try:
            self.stat.add_metric(name, value)
        except AttributeError:
            pass

    @abstractmethod
    async def create_dataframe(
        self, result: Union[dict, bytes, Any], *args: P.args, **kwargs: P.kwargs
    ) -> Any:
        """
        Converts any result into a DataFrame.

        :param result: The result data to be converted into a DataFrame.
        :return: A DataFrame containing the result data.
        """
        pass
