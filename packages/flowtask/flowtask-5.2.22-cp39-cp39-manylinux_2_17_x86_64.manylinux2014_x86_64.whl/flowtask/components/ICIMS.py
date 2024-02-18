from navconfig.logging import logging
from querysource.exceptions import DataNotFound as QSNotFound
from ..exceptions import ComponentError, DataNotFound
from .QSBase import QSBase


class ICIMS(QSBase):
    """ICIMS."""

    type = "form_data"
    _driver = "icims"
    _metrics: dict = {
        "requestedby": "requested_by",
        "updatedby": "updated_by",
        "formname": "form_name",
        "updateddate": "updated_date",
        "completeddate": "completed_date",
        "completedby": "completed_by",
    }

    async def people(self):
        try:
            row = await self._qs.people()
            if row:
                return row
            else:
                return []
        except QSNotFound as err:
            raise DataNotFound(f"ICIMS Not Found: {err}") from err
        except Exception as err:
            logging.exception(err)
            raise ComponentError(f"ICIMS ERROR: {err!s}") from err

    async def person(self):
        try:
            row = await self._qs.person()
            if row:
                row["person_id"] = self._variables["person_id"]
                return [row]
            else:
                return []
        except QSNotFound as err:
            raise DataNotFound(f"ICIMS Not Found: {err}") from err
        except Exception as err:
            logging.exception(err)
            raise ComponentError(f"ICIMS ERROR: {err!s}") from err

    async def forms_list(self):
        try:
            row = await self._qs.forms_list()
            if row:
                return row["forms"]
            else:
                return []
        except QSNotFound as err:
            raise DataNotFound(f"ICIMS Not Found: {err}") from err
        except Exception as err:
            logging.exception(err)
            raise ComponentError(f"ICIMS ERROR: {err!s}") from err

    async def form_data(self):
        try:
            row = await self._qs.form_data()
            if row:
                for key, name in self._metrics.items():
                    try:
                        row[name] = row[key]
                        del row[key]
                    except (TypeError, KeyError):
                        pass
                return [row]
            else:
                return []
        except QSNotFound as err:
            raise DataNotFound(f"ICIMS Not Found: {err}") from err
        except Exception as err:
            logging.exception(err)
            raise ComponentError(f"ICIMS ERROR: {err!s}") from err
