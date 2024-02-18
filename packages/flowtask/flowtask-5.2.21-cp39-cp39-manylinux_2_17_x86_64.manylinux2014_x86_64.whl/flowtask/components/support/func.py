from typing import Optional
from abc import ABC
import asyncio
import builtins
from navconfig.logging import logging
from ...exceptions import ComponentError, ConfigError
from ...types import SafeDict

## functions
from ...utils import functions as ffunctions  # pylint: disable=W0614,W0401
import querysource.utils.functions as qsfunctions  # pylint: disable=W0401,C0411


class FuncSupport(ABC):
    """
    Interface for adding Add Support for Function Replacement.
    """

    def __init__(self, loop: Optional[asyncio.AbstractEventLoop] = None, **kwargs):
        self._loop = self.event_loop(loop)

    def event_loop(
        self, evt: Optional[asyncio.AbstractEventLoop] = None
    ) -> asyncio.AbstractEventLoop:
        if evt is not None:
            asyncio.set_event_loop(evt)
            return evt
        else:
            try:
                return asyncio.get_event_loop()
            except RuntimeError as exc:
                raise RuntimeError(f"There is no Event Loop: {exc}") from exc

    def _get_function(self, fname):
        fn = None
        try:
            # First: check if function exists on QuerySource:
            fn = getattr(qsfunctions, fname)
        except (TypeError, AttributeError):
            # Second: check if function exists on FlowTask:
            try:
                fn = getattr(ffunctions, fname)
            except (TypeError, AttributeError):
                # Third: check if function exists on builtins:
                try:
                    fn = getattr(builtins, fname)
                except (TypeError, AttributeError):
                    fn = globals()[fname]
        if fn is None:
            # Function doesn't exists:
            raise ConfigError(f"Function {fname} doesn't exists.")
        return fn

    def getFunc(self, val):
        try:
            if isinstance(val, list):
                fname, args = (val + [{}])[:2]  # Safely unpack with default args
                # try:
                #     args = val[1]
                # except IndexError:
                #     args = {}
                fn = self._get_function(fname)
                # if args:
                #     result = fn(**args)
                # else:
                #     result = fn()
                # Call the function with args
                return fn(**args) if args else fn()
            elif val in self._variables:
                return self._variables[val]
            elif val in self._mask:
                return self._mask[val]
            else:
                return val
        except ConfigError:
            pass
        except Exception as err:
            raise ComponentError(
                f"{__name__}: Error parsing Function {val!r}: {err}"
            ) from err

    def get_filepattern(self):
        if not hasattr(self, "file"):
            return None
        fname = self.file["pattern"]
        result = None
        try:
            val = self.file.get("value", fname)
            if isinstance(val, str):
                if val in self._variables:
                    # get from internal variables
                    result = self._variables[val]
            elif isinstance(val, list):
                func = val[0]
                func, args = (val + [{}])[:2]  # Safely unpack with default args
                fn = self._get_function(fname)
                try:
                    result = fn(**args) if args else fn()
                except (TypeError, AttributeError):
                    try:
                        if args:
                            result = globals()[func](**args)
                        else:
                            result = globals()[func]()
                    except (TypeError, ValueError) as e:
                        logging.error(str(e))
            else:
                result = val
        except ConfigError:
            pass
        except (NameError, KeyError) as err:
            logging.warning(f"FilePattern Error: {err}")
        return fname.format_map(SafeDict(value=result))
