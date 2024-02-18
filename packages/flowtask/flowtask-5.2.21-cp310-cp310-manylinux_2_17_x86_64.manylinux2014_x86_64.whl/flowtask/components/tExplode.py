import asyncio
from typing import Any
from collections.abc import Callable
import pandas
from pandas import json_normalize
from ..exceptions import ComponentError, DataNotFound
from .abstract import DtComponent


class tExplode(DtComponent):
    """
    tExplode.

    Overview

        Convert a column into several rows.

    .. table:: Properties
       :widths: auto


    +--------------+----------+-----------+-------------------------------------------------------+
    | Name         | Required | Summary                                                           |
    +--------------+----------+-----------+-------------------------------------------------------+
    |  start       |   Yes    | We start by validating if the file exists, then the function      |
    |              |          | to get the data is started                                        |
    +--------------+----------+-----------+-------------------------------------------------------+
    |  run         |   Yes    | This method allows to run the function and change its state       |
    +--------------+----------+-----------+-------------------------------------------------------+
    |  close       |   Yes    | This attribute allows me to close the process                     |
    +--------------+----------+-----------+-------------------------------------------------------+

    """

    def __init__(
        self,
        loop: asyncio.AbstractEventLoop = None,
        job: Callable = None,
        stat: Callable = None,
        **kwargs,
    ):
        """Init Method."""
        self.data: Any = None
        self.column: str = kwargs.pop("column", None)
        self.drop_original: bool = kwargs.pop("drop_original", False)
        super(tExplode, self).__init__(loop=loop, job=job, stat=stat, **kwargs)

    async def start(self, **kwargs):
        # Si lo que llega no es un DataFrame de Pandas se cancela la tarea
        if self.previous:
            self.data = self.input
        else:
            raise ComponentError("Data Not Found", code=404)
        if not isinstance(self.data, pandas.DataFrame):
            raise ComponentError("Incompatible Pandas Dataframe", code=404)
        return True

    async def run(self):
        args = {}
        if self.data.empty:
            raise DataNotFound("Data Was Not Found on Dataframe 1")

        # Explode the Rows:
        try:
            # Step 1: Explode the 'field' column
            exploded_df = self.data.explode(self.column)
            # Reset index to ensure it's unique
            exploded_df = exploded_df.reset_index(drop=True)
            # Step 2: Normalize the JSON data in 'attachments'
            # This will create a new DataFrame where each dictionary key becomes a column
            attachments_df = json_normalize(exploded_df[self.column])
            # Step 3: Concatenate with the original DataFrame
            # Drop the original 'attachments' column from exploded_df and join with attachments_df
            if self.drop_original is True:
                exploded_df.drop(self.column, axis=1)
            df = pandas.concat([exploded_df, attachments_df], axis=1)
        except Exception as err:
            raise ComponentError(f"Error Merging Dataframes: {err}") from err
        numrows = len(df.index)
        if numrows == 0:
            raise DataNotFound("Concat: Cannot make any Explode")
        if hasattr(self, "index"):
            df[self.index] = df["id"]
            df.drop("id", axis="columns", inplace=True)
        self._variables[f"{self.TaskName}_NUMROWS"] = numrows
        self.add_metric("EXPLODE: ", numrows)
        df.is_copy = None
        print(df)
        self._result = df
        if self._debug is True:
            print("::: Printing Column Information === ")
            for column, t in df.dtypes.items():
                print(column, "->", t, "->", df[column].iloc[0])
        return self._result

    async def close(self):
        pass
