from abc import abstractmethod
from urllib.parse import urljoin

from bs4 import BeautifulSoup
import httpx

from flowtask.components.interfaces.http import HTTPService
from flowtask.exceptions import ComponentError
from ..abstract import DtComponent


class ASPX(DtComponent, HTTPService):
    _credentials: dict = {"username": str, "password": str}

    def _set_views(self, soup: BeautifulSoup):
        """Extract state VIEWS from hidden inputs inside html

        Args:
            soup (BeautifulSoup): soup object with the html tree

        Returns:
            dict[str, str]: state VIEWS
        """
        viewstate = soup.find(id="__VIEWSTATE")["value"]
        soup_eventvalidation = soup.find(id="__EVENTVALIDATION")
        eventvalidation = soup_eventvalidation["value"] if soup_eventvalidation else ""
        viewstategenerator = soup.find(id="__VIEWSTATEGENERATOR")["value"]

        self._views = {
            "__EVENTTARGET": "",
            "__EVENTARGUMENT": "",
            "__VIEWSTATE": viewstate,
            "__VIEWSTATEGENERATOR": viewstategenerator,
            "__EVENTVALIDATION": eventvalidation,
        }

    def check_keys_exists(self, *args, **kwargs):
        """Validate that specified keys are present in the kwargs dict"""
        for _key in args:
            if _key not in kwargs:
                raise ComponentError(f"{_key} must be set!")

    def _get_payload_with_views(self, **kwargs):
        payload = {
            **self._views,
            **kwargs,
        }

        return payload

    async def start(self, **kwargs):
        # handle login and set initial views
        self._proxies = False
        self._user = None
        self.auth_type = None
        self.auth = ""
        self.download = None
        self.headers = None
        self._views: dict = {}
        self.timeout = 120.0
        self._client = httpx.AsyncClient(timeout=self.timeout)

        self.processing_credentials()

        login_url = urljoin(self.base_url, "/Login.aspx")

        self.accept = "text/html"
        await self.aspx_session(login_url)

        payload = {
            **self._views,
            self.login_user_payload_key: self.credentials["username"],
            self.login_password_payload_key: self.credentials["password"],
            self.login_button_payload_key: self.login_button_payload_value,
        }

        await self.aspx_session(
            login_url, method="post", data=payload, follow_redirects=True
        )

        if ".ASPXAUTH" not in self._client.cookies:
            raise ComponentError("Login Failed. Please, check credentials!")
        self._logger.info("Login successful")

        return True

    @abstractmethod
    async def run(self):
        """
        Extend this method: Call super() after your code to make sure
        the client session is closed.
        """
        if hasattr(self, "_client"):
            await self._client.aclose()

    async def close(self):
        pass

    def processing_credentials(self):
        if self.credentials:
            for value, dtype in self._credentials.items():
                try:
                    if type(self.credentials[value]) == dtype:
                        # can process the credentials, extracted from environment or variables:
                        default = getattr(self, value, self.credentials[value])
                        val = self.get_env_value(
                            self.credentials[value], default=default
                        )
                        self.credentials[value] = val
                except (TypeError, KeyError) as ex:
                    self._logger.error(f"{__name__}: Wrong or missing Credentials")
                    raise ComponentError(
                        f"{__name__}: Wrong or missing Credentials"
                    ) from ex

    async def aspx_session(
        self,
        url: str,
        method: str = "get",
        data: dict = None,
        **kwargs: dict,
    ):
        result, error = await self.session(
            url,
            method=method,
            data=data,
            **kwargs,
        )

        if error:
            raise ComponentError(error)

        if "text/html" in self.accept:
            self._set_views(result)

        return result
