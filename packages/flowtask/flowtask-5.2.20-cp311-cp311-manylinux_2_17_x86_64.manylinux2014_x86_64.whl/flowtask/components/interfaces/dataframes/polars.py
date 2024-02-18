from typing import Union, Any, ParamSpec
import orjson
import pandas as pd
import polars as pl
from .abstract import BaseDataframe
from ....exceptions import ComponentError, DataNotFound


P = ParamSpec("P")


def is_empty(obj):
    """check_empty.
    Check if a basic object or a DataFrame (Pandas or Polars) is empty or not.
    """
    if isinstance(obj, pd.DataFrame) or isinstance(obj, pl.DataFrame):
        return obj.shape[0] == 0
    else:
        return bool(not obj)


class PolarsDataframe(BaseDataframe):
    """PolarsDataframe.

    Converts any result into a Polars DataFrame.
    """

    async def create_dataframe(
        self, result: Union[dict, bytes, Any], *args: P.args, **kwargs: P.kwargs
    ) -> Any:
        """
        Converts any result into a Polars DataFrame.

        :param result: The result data to be converted into a Polars DataFrame.
        :return: A DataFrame containing the result data.
        """
        if is_empty(result):
            raise DataNotFound("DataFrame: No Data was Found.")
        try:
            if isinstance(result, str):
                try:
                    result = orjson.loads(result)
                except Exception:
                    pass
            df = pl.DataFrame(result, **kwargs)
            columns = list(df.columns)
            if hasattr(self, "drop_empty"):
                df = df.drop_nulls(how="all", subset=df.columns)
            if hasattr(self, "dropna"):
                df = df.drop_nulls(how="all", subset=self.dropna)
            if self._debug:
                print("::: Printing Column Information ::: ")
                for column in columns:
                    t = df[column].dtype
                    print(column, "->", t, "->", df[column][0])
            numrows = df.height
            self._variables["_numRows_"] = numrows
            self.add_metric("NUM_ROWS", numrows)
            self.add_metric("NUM_COLS", df.width)
            return df
        except Exception as err:
            self._logger.error(f"Error Creating Dataframe {err!s}")
            raise ComponentError(f"Error Creating Dataframe: {err!s}")
