"""Basic HTTP Connection Request."""
import os
import asyncio
import random

# configuration and settings
from functools import partial
from typing import Union
from collections.abc import Callable
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from urllib.parse import urlencode
import urllib3
import requests
from requests.auth import HTTPBasicAuth
from requests.exceptions import HTTPError
from io import BytesIO
import aiofiles
import aiohttp
from aiohttp import BasicAuth
from navconfig import config
from navconfig.logging import logging
from proxylists.proxies import FreeProxy
from bs4 import BeautifulSoup as bs
from lxml import html, etree
from querysource.types import strtobool
from ..utils.json import JSONContent
from ..utils import cPrint, SafeDict
from ..exceptions import DataNotFound, ComponentError, FileNotFound
from ..conf import HTTPCLIENT_MAX_SEMAPHORE, HTTPCLIENT_MAX_WORKERS
from .DownloadFrom import DownloadFromBase


logging.getLogger("urllib3").setLevel(logging.WARNING)
urllib3.disable_warnings()

ua = [
    "Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1; SV1; .NET CLR 1.1.4322)",
    "Mozilla/5.0 (Linux; Android 4.2.1; en-us; Nexus 5 Build/JOP40D) AppleWebKit/535.19 (KHTML, like Gecko; googleweblight) Chrome/38.0.1025.166 Mobile Safari/535.19",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.97 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/42.0.2311.135 Safari/537.36 Edge/12.10240",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_8_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36",
    "Mozilla/5.0 (X11; Windows NT 10.0; rv:19.0) Gecko/20100101 Firefox/19.0 Iceweasel/19.0.2",
    "Mozilla/5.0 (X11; U; Linux i686; sk; rv:1.9.0.4) Gecko/2008111217 Fedora/3.0.4-1.fc10 Firefox/3.0.4",
]


class HTTPClient(DownloadFromBase):
    """
    HTTPClient.

    Overview

           UserComponent: (abstract) ->

    .. table:: Properties
       :widths: auto


    +-----------+----------+-----------+----------------------------------------------+
    | Name      | Required | Summary                                                  |
    +-----------+----------+-----------+----------------------------------------------+
    | start     |   Yes    | It is executed when the component is "initialized",      |
    |           |          | it MUST return TRUE if it does not fail                  |
    +-----------+----------+-----------+----------------------------------------------+
    | run       |   Yes    | Is the code that will execute the component ,must return TRUE or  |
    |           |          | a content if it does not fail, but fails is declared      |
    +-----------+----------+-----------+-----------------------------------------------+
    | close     |   Yes    | It is used for any cleaning operation                     |
    +-----------+----------+-----------+-----------------------------------------------+


    Return the list of arbitrary days

    """

    accept: str = "application/xhtml+xml"
    port: int = 80

    def __init__(
        self,
        loop: asyncio.AbstractEventLoop = None,
        job: Callable = None,
        stat: Callable = None,
        **kwargs,
    ):
        if "url" in kwargs:
            self.url = kwargs["url"]
            del kwargs["url"]
        else:
            self.url: str = None
        self.use_proxy: bool = False
        self.use_async: bool = bool(kwargs.pop("use_async", True))
        self._proxies: list = []

        self.rotate_ua: bool = kwargs.pop("rotate_ua", False)
        self.timeout: int = 30
        self.headers: dict = {}
        self.auth: dict = {}
        self.auth_type: str = None
        self.token_type: str = "Bearer"
        self._user: str = None
        self._pwd: str = None
        # beautiful soup and html parser:
        self._bs: Callable = None
        self._parser: Callable = None
        self._environment = config
        # calling parent
        super(HTTPClient, self).__init__(loop=loop, job=job, stat=stat, **kwargs)
        try:
            as_dataframe = kwargs["as_dataframe"]
            del kwargs["as_dataframe"]
            if isinstance(as_dataframe, bool):
                self.as_dataframe = as_dataframe
            else:
                self.as_dataframe: bool = strtobool(as_dataframe)
        except KeyError:
            self.as_dataframe: bool = True
        # Credentials:
        self.credentials: dict = kwargs.pop("credentials", {})
        self.method: str = kwargs.pop("method", "get")
        self.parameters = {}
        if self.rotate_ua is True:
            self._ua = random.choice(ua)
        else:
            self._ua: str = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.97 Safari/537.36"
        self.headers = {
            "Accept": self.accept,
            "Accept-Encoding": "gzip, deflate",
            "DNT": "1",
            "Connection": "keep-alive",
            "Upgrade-Insecure-Requests": "1",
            "User-Agent": self._ua,
            **self.headers,
        }
        self._encoder = JSONContent()
        # other arguments:
        self._arguments = kwargs
        # Executor:
        self._executor = ThreadPoolExecutor(max_workers=int(HTTPCLIENT_MAX_WORKERS))
        self._semaphore = asyncio.Semaphore(
            int(HTTPCLIENT_MAX_SEMAPHORE)
        )  # Adjust the number as neededd

    async def get_proxies(self):
        """
        Asynchronously retrieves a list of free proxies.
        """
        return await FreeProxy().get_list()

    async def refresh_proxies(self):
        """
        Asynchronously refreshes the list of proxies if proxy usage is enabled.
        """
        if self.use_proxy is True:
            self._proxies = await self.get_proxies()

    def build_url(self, url, queryparams: str = "", args=None):
        """
        Constructs a full URL with optional query parameters and arguments.

        :param url: The base URL to be formatted.
        :param queryparams: Additional query parameters to be appended to the URL.
        :param args: Arguments to format within the URL.
        :return: The fully constructed URL.
        """
        url = str(url).format_map(SafeDict(**self._variables))
        if args:
            u = url.format(**args)
        else:
            u = url
        if queryparams:
            if "?" in u:
                full_url = u + "&" + queryparams
            else:
                full_url = u + "?" + queryparams
        else:
            full_url = u
        logging.debug(f"Resource URL: {full_url!s}")
        return full_url

    def get_env_value(self, key, default: str = None):
        """
        Retrieves a value from the environment variables or the configuration.

        :param key: The key for the environment variable.
        :param default: The default value to return if the key is not found.
        :return: The value of the environment variable or the default value.
        """
        if val := os.getenv(key):
            return val
        elif val := self._environment.get(key, default):
            return val
        else:
            return key

    async def async_request(
        self, url, method: str = "GET", data: dict = None, use_json: bool = False
    ):
        """
        Asynchronously sends an HTTP request using aiohttp.

        :param url: The URL to send the request to.
        :param method: The HTTP method to use (e.g., 'GET', 'POST').
        :param data: The data to send in the request body.
        :param use_json: Whether to send the data as JSON.
        :return: A tuple containing the result and any error information.
        """
        result = []
        error = {}
        auth = None
        proxies = None
        if self._proxies:
            proxies = random.choice(self._proxies)
        if self.credentials:
            if "apikey" in self.auth:
                self.headers[
                    "Authorization"
                ] = f"{self.token_type} {self.auth['apikey']}"
            elif self.auth_type == "api_key":
                self.headers = {**self.headers, **self.credentials}
            elif self.auth_type == "key":
                url = self.build_url(
                    url, args=self._arguments, queryparams=urlencode(self.credentials)
                )
            elif self.auth_type in ["basic", "auth", "user"]:
                auth = BasicAuth(
                    self.credentials["username"], self.credentials["password"]
                )
        elif self._user and self.auth_type == "basic":
            auth = BasicAuth(self._user, self._pwd)
        cPrint(f"HTTP: Connecting to {url}", level="DEBUG")
        if self._debug is True:
            self.add_metric("HEADERS", self.headers)
        if proxies is not None:
            self.add_metric("Proxies", proxies)
        self.add_metric("URL", url)
        self.add_metric("METHOD", method)
        if auth is not None:
            args = {"auth": auth}
        else:
            args = {}
        if hasattr(self, "download"):
            self.headers["Accept"] = "application/octet-stream"
            self.headers["Content-Type"] = "application/octet-stream"
            if hasattr(self, "use_streams"):
                self.headers["Transfer-Encoding"] = "chunked"
                args["stream"] = True
        timeout = aiohttp.ClientTimeout(total=self.timeout)
        async with aiohttp.ClientSession(
            headers=self.headers, timeout=timeout, auth=auth
        ) as session:
            try:
                if use_json is True:
                    async with session.request(
                        method.upper(), url, json=data, proxy=proxies, **args
                    ) as response:
                        result, error = await self.process_response(response, url)
                else:
                    async with session.request(
                        method.upper(), url, data=data, proxy=proxies, **args
                    ) as response:
                        # Process the response
                        result, error = await self.process_response(response, url)
            except aiohttp.ClientError as e:
                print("FALLA AQUI >>")
                error = str(e)
        return (result, error)

    async def evaluate_error(
        self, response: Union[str, list], message: Union[str, list, dict]
    ) -> tuple:
        """evaluate_response.

        Check Response status and available payloads.
        Args:
            response (_type_): _description_
            url (str): _description_

        Returns:
            tuple: _description_
        """
        if isinstance(response, list):
            # a list of potential errors:
            for msg in response:
                if message in msg:
                    return True
        if isinstance(response, dict) and "errors" in response:
            errors = response["errors"]
            if isinstance(errors, list):
                for error in errors:
                    try:
                        if message in error:
                            return True
                    except TypeError:
                        if message == error:
                            return True
            else:
                if message == errors:
                    return True
        else:
            if message in response:
                return True
        return False

    async def process_response(self, response, url: str) -> tuple:
        """
        Processes the response from an HTTP request.

        :param response: The response object from aiohttp.
        :param url: The URL that was requested.
        :return: A tuple containing the processed result and any error information.
        """
        error = None
        result = None
        # Process the response
        if response.status >= 400:
            # Evaluate response body and headers.
            print(" == ERROR Headers == ")
            print(f"{response.headers}")
            content_type = response.headers.get("Content-Type", "").lower()
            if "application/json" in content_type:
                message = await response.json()
            elif "text/" in content_type:
                message = await response.text()
            elif "X-Error" in response.headers:
                message = response.headers["X-Error"]
            else:
                message = response.reason
            # Log the error or perform other error handling
            self._logger.error(f"Error: {message}, status: {response.status}")
            if hasattr(self, "no_errors"):
                for key, msg in self.no_errors.items():
                    if int(key) == response.status:
                        if await self.evaluate_error(message, msg):
                            return (response, response.status)
            # Raise an exception
            raise ConnectionError(f"HTTP Error {response.status}: {message}")
        else:
            if hasattr(self, "download") and self.download is True:
                filename = os.path.basename(url)
                # Get the filename from the response headers, if available
                content_disposition = response.headers.get("content-disposition")
                if content_disposition:
                    _, params = content_disposition.split(";")
                    try:
                        key, value = params.strip().split("=")
                        if key == "filename":
                            filename = value.strip("'\"")
                    except ValueError:
                        pass
                if "{filename}" in str(self.filename):
                    self.filename = str(self.filename).format_map(
                        SafeDict(filename=filename)
                    )
                if "{" in str(self.filename):
                    self.filename = str(self.filename).format_map(
                        SafeDict(**self._arguments)
                    )
                if isinstance(self.filename, str):
                    self.filename = Path(self.filename)
                # Saving File in Directory:
                total_length = response.headers.get("Content-Length")
                self._logger.info(
                    f"HTTPClient: Saving File {self.filename}, size: {total_length}"
                )
                pathname = self.filename.parent.absolute()
                if not pathname.exists():
                    # Create a new directory
                    pathname.mkdir(parents=True, exist_ok=True)
                transfer = response.headers.get("transfer-encoding", None)
                if transfer is None:
                    chunk_size = int(total_length)
                else:
                    chunk_size = 8192
                # Asynchronous file writing
                if self.filename.exists() and self.filename.is_file():
                    overwrite = self.destination.get("overwrite", True)
                    if overwrite is False:
                        self._logger.warning(
                            f"HTTPClient: File Already exists: {self.filename}"
                        )
                        # Filename already exists
                        result = self.filename
                        return result, error
                    else:
                        self._logger.warning(
                            f"HTTPClient: Overwriting File: {self.filename}"
                        )
                        # Delete the file before downloading again.
                        try:
                            self.filename.unlink()
                        except Exception as e:
                            self._logger.warning(
                                f"HTTPClient: Error Deleting File: {self.filename}, {e}"
                            )
                if hasattr(self, "use_streams") and self.use_streams is True:
                    async with aiofiles.open(self.filename, "wb") as file:
                        async for chunk in response.content.iter_chunked(chunk_size):
                            await file.write(chunk)
                else:
                    with open(self.filename, "wb") as fp:
                        try:
                            fp.write(await response.read())
                        except Exception:
                            pass
                self._logger.debug(f"Filename Saved Successfully: {self.filename}")
                result = self.filename
            elif hasattr(self, "download") and self.download is False:
                data = await response.read()
                buffer = BytesIO(data)
                buffer.seek(0)
                result = buffer
            elif self.accept in ("text/html"):
                result = await response.read()  # Get content of the response as bytes
                try:
                    # html parser for lxml
                    self._parser = html.fromstring(result)
                    # BeautifulSoup parser
                    self._bs = bs(response.text, "html.parser")
                    result = self._bs
                except Exception as e:
                    error = e
            elif self.accept in ("application/xhtml+xml", "application/xml"):
                result = await response.read()  # Get content of the response as bytes
                try:
                    self._parser = etree.fromstring(result)
                except Exception as e:
                    error = e
            elif self.accept == "application/json":
                try:
                    result = await response.json()
                except Exception as e:
                    logging.error(e)
                    # is not an json, try first with beautiful soup:
                    try:
                        self._bs = bs(await response.text(), "html.parser")
                        result = self._bs
                    except Exception:
                        error = e
            else:
                result = await response.text()
        return result, error

    async def request(self, url, method: str = "GET", data: dict = None) -> tuple:
        """
        Sends an HTTP request using the requests library.

        :param url: The URL to send the request to.
        :param method: The HTTP method to use (e.g., 'GET', 'POST').
        :param data: The data to send in the request body.
        :return: A tuple containing the result and any error information.
        """
        result = []
        error = {}
        auth = None
        proxies = None
        if self._proxies:
            proxy = random.choice(self._proxies)
            proxies = {"http": proxy, "https": proxy, "ftp": proxy}
        if self.credentials:
            if "apikey" in self.auth:
                self.headers[
                    "Authorization"
                ] = f"{self.token_type} {self.auth['apikey']}"
            elif "apikey" in self.credentials:
                self.headers[
                    "Authorization"
                ] = f"{self.token_type} {self.credentials['apikey']}"
            elif self.auth_type == "api_key":
                self.headers = {**self.headers, **self.credentials}
            elif self.auth_type == "key":
                url = self.build_url(
                    url, args=self._arguments, queryparams=urlencode(self.credentials)
                )
            elif self.auth_type == "basic":
                auth = HTTPBasicAuth(
                    self.credentials["username"], self.credentials["password"]
                )
            else:
                auth = HTTPBasicAuth(
                    self.credentials["username"], self.credentials["password"]
                )
        elif self._user and self.auth_type == "basic":
            auth = HTTPBasicAuth(self._user, self._pwd)
        cPrint(f"HTTP: Connecting to {url}", level="DEBUG")
        self.add_metric("URL", url)
        self.add_metric("METHOD", method)
        if auth is not None:
            args = {"auth": auth, "verify": False}
        else:
            args = {}
        if hasattr(self, "download"):
            self.headers["Accept"] = "application/octet-stream"
            self.headers["Content-Type"] = "application/octet-stream"
            if hasattr(self, "use_streams"):
                self.headers["Transfer-Encoding"] = "chunked"
                args["stream"] = True
        if self._debug is True:
            self.add_metric("HEADERS", self.headers)
        if proxies is not None:
            self.add_metric("Proxies", proxies)
        args["headers"] = self.headers
        args["timeout"] = self.timeout
        args["proxies"] = proxies
        if method == "get":
            my_request = partial(requests.get, **args)
        elif method == "post":
            my_request = partial(requests.post, data=data, **args)
        elif method == "put":
            my_request = partial(requests.put, data=data, **args)
        elif method == "delete":
            my_request = partial(requests.delete, data=data, **args)
        elif method == "patch":
            my_request = partial(requests.patch, data=data, *args)
        else:
            my_request = partial(requests.post, data=data, **args)
        try:
            # making request
            async with self._semaphore:
                loop = asyncio.get_running_loop()
                future = loop.run_in_executor(self._executor, my_request, url)
                result, error = await self.process_request(future, url)
            if error:
                if isinstance(error, BaseException):
                    raise error
                else:
                    raise ComponentError(f"{error!s}")
            return (result, error)
        except requests.exceptions.ReadTimeout as err:
            self._logger.warning(f"Timeout Error: {err!r}")
            # TODO: retrying
            raise ComponentError(f"Timeout: {err}") from err
        except Exception as err:
            self._logger.exception(str(err), stack_info=True)
            raise ComponentError(f"Error: {err}") from err

    async def process_request(self, future, url: str):
        """
        Processes the result of an asynchronous HTTP request.

        :param future: The future object representing the asynchronous operation.
        :param url: The URL that was requested.
        :return: A tuple containing the result and any error information.
        """
        # getting the result, based on the Accept logic
        error = None
        result = None
        loop = asyncio.get_running_loop()
        asyncio.set_event_loop(loop)
        done, _ = await asyncio.wait([future], return_when=asyncio.FIRST_COMPLETED)
        for f in done:
            response = f.result()
            # for response in await asyncio.gather(*future):
            # Check for HTTP errors
            try:
                response.raise_for_status()
            except HTTPError as http_err:
                # Handle HTTP errors here
                error = http_err
                # Log the error or perform other error handling
                self._logger.error(f"HTTP error occurred: {http_err}")
                # You can choose to continue, break, or return based on your logic
                continue
            try:
                if hasattr(self, "download"):
                    # Filename:
                    filename = os.path.basename(url)
                    # Get the filename from the response headers, if available
                    content_disposition = response.headers.get("content-disposition")
                    if content_disposition:
                        _, params = content_disposition.split(";")
                        try:
                            key, value = params.strip().split("=")
                            if key == "filename":
                                filename = value.strip("'\"")
                        except ValueError:
                            pass
                    if "{filename}" in str(self.filename):
                        self.filename = str(self.filename).format_map(
                            SafeDict(filename=filename)
                        )
                    if "{" in str(self.filename):
                        self.filename = str(self.filename).format_map(
                            SafeDict(**self._arguments)
                        )
                    if isinstance(self.filename, str):
                        self.filename = Path(self.filename)
                    # Saving File in Directory:
                    total_length = response.headers.get("Content-Length")
                    self._logger.info(
                        f"HTTPClient: Saving File {self.filename}, size: {total_length}"
                    )
                    pathname = self.filename.parent.absolute()
                    if not pathname.exists():
                        # Create a new directory
                        pathname.mkdir(parents=True, exist_ok=True)
                    response.raise_for_status()
                    transfer = response.headers.get("transfer-encoding", None)
                    if transfer is None:
                        chunk_size = int(total_length)
                    else:
                        chunk_size = 8192
                    if self.filename.exists() and self.filename.is_file():
                        overwrite = self.destination.get("overwrite", True)
                        if overwrite is False:
                            self._logger.warning(
                                f"HTTPClient: File Already exists: {self.filename}"
                            )
                            # Filename already exists
                            result = self.filename
                            continue
                        else:
                            self._logger.warning(
                                f"HTTPClient: Overwriting File: {self.filename}"
                            )
                            # Delete the file before downloading again.
                            try:
                                self.filename.unlink()
                            except Exception as e:
                                self._logger.warning(
                                    f"HTTPClient: Error Deleting File: {self.filename}, {e}"
                                )
                    with open(self.filename, "wb") as fp:
                        try:
                            for chunk in response.iter_content(chunk_size=chunk_size):
                                fp.write(chunk)
                            fp.flush()
                        except Exception:
                            pass
                    self._logger.debug(f"Filename Saved Successfully: {self.filename}")
                    result = self.filename
                elif self.accept in ("text/html"):
                    result = response.content  # Get content of the response as bytes
                    try:
                        # html parser for lxml
                        self._parser = html.fromstring(result)
                        # BeautifulSoup parser
                        self._bs = bs(response.text, "html.parser")
                        result = self._bs
                    except Exception as e:
                        error = e
                elif self.accept in ("application/xhtml+xml", "application/xml"):
                    result = response.content  # Get content of the response as bytes
                    try:
                        self._parser = etree.fromstring(result)
                    except Exception as e:
                        error = e
                elif self.accept == "application/json":
                    try:
                        result = response.json()
                    except Exception as e:
                        logging.error(e)
                        # is not an json, try first with beautiful soup:
                        try:
                            self._bs = bs(response.text, "html.parser")
                            result = self._bs
                        except Exception:
                            error = e
                else:
                    result = response.text
            except requests.exceptions.ProxyError as err:
                raise ComponentError(f"Proxy Connection Error: {err!r}") from err
            except requests.ReadTimeout as err:
                return (result, err)
            except requests.exceptions.HTTPError as e:
                # Log the error or perform other error handling
                self._logger.error(f"HTTP error occurred: {error}")
                raise ComponentError(f"HTTP Error: {error!r}, ex: {e!s}") from e
            except Exception as e:
                logging.exception(e)
                return (result, e)
        # returning results
        return (result, error)

    def var_replacement(self):
        """
        Replaces variables in the arguments with their corresponding values.
        """
        for key, _ in self._arguments.items():
            if key in self._variables:
                self._arguments[key] = self._variables[key]

    async def start(self, **kwargs):
        """
        Initializes the HTTPClient component, including fetching proxies if necessary.

        :param kwargs: Additional keyword arguments.
        :return: True if initialization is successful.
        """
        if self.use_proxy is True:
            self._proxies = await self.get_proxies()
        self.var_replacement()
        super(HTTPClient, self).start()
        return True

    async def close(self):
        pass

    async def run(self):
        """
        Executes the HTTPClient component, handling multiple URLs if provided.

        :return: The result of the HTTP request(s).
        """
        if isinstance(self.url, list):
            ## iterate over a list of URLs:
            results = {}
            for url in self.url:
                uri = self.build_url(
                    url, args=self._arguments, queryparams=urlencode(self.parameters)
                )
                try:
                    if self.use_async is True:
                        result, err = await self.async_request(uri, self.method)
                    else:
                        result, error = await self.request(uri, self.method)
                    if not result:
                        raise DataNotFound(f"Data was not found on: {uri}")
                    if error is not None:
                        if isinstance(error, BaseException):
                            raise error
                        else:
                            raise ComponentError(f"HTTPClient Error: {error}")
                    ## processing results:
                    if hasattr(self, "download"):
                        ## add result to resultset
                        results[result] = True
                        if self._debug:
                            self._logger.debug(f"File Exists > {result}")
                    else:
                        results[result] = result
                except Exception as err:
                    self._logger.exception(err, stack_info=True)
                    raise ComponentError(f"HTTPClient Error: {err}") from err
            ##
            self.add_metric("FILENAME", results)
            self._result = results
            return self._result
        else:
            self.url = self.build_url(
                self.url, args=self._arguments, queryparams=urlencode(self.parameters)
            )
            try:
                if self.use_async is True:
                    result, error = await self.async_request(self.url, self.method)
                else:
                    result, error = await self.request(self.url, self.method)
                if not result:
                    raise DataNotFound(f"Data was not found on: {self.url}")
                elif error is not None:
                    if hasattr(self, "no_errors"):
                        # check if error is in no_errors
                        return False
                    if isinstance(error, BaseException):
                        raise error
                    else:
                        raise ComponentError(f"HTTPClient Error: {error}")
                # at here, processing Result
                if self.as_dataframe is True:
                    try:
                        result = await self.create_dataframe(result)
                    except Exception as err:
                        raise ComponentError(f"RESTClient Error: {err}") from err
                elif hasattr(self, "download"):
                    # File downloaded, return same as FileExists
                    file = result
                    self._logger.debug(f" ::: Checking for File: {file}")
                    result = {}
                    if file.exists() and file.is_file():
                        result[file] = True
                        self.setTaskVar("DIRECTORY", file.parent)
                        self.setTaskVar("FILENAME", str(file.name))
                        self.setTaskVar("FILEPATH", file)
                        self.add_metric("FILENAME", file)
                    else:
                        raise FileNotFound(f"FileExists: File Doesn't exists: {file}")
                self._result = result
                return self._result
            except DataNotFound:
                raise
            except Exception as err:
                self._logger.exception(err, stack_info=True)
                raise ComponentError(f"HTTPClient: {err}") from err
