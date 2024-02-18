import asyncio
from collections.abc import Callable
from .interfaces.AzureClient import AzureClient
from .interfaces.http import HTTPService
from .abstract import DtComponent


class Azure(DtComponent, AzureClient, HTTPService):
    accept: str = "application/json"
    no_host: bool = True

    def __init__(
        self,
        loop: asyncio.AbstractEventLoop = None,
        job: Callable = None,
        stat: Callable = None,
        **kwargs,
    ):
        self.credentials: dict = {}
        self.as_dataframe: bool = kwargs.pop("as_dataframe", False)
        # Initialize parent classes explicitly
        DtComponent.__init__(self, loop=loop, job=job, stat=stat, **kwargs)
        HTTPService.__init__(self, **kwargs)
        AzureClient.__init__(self, **kwargs)

    async def close(self, timeout: int = 5):
        """close.
        Closing the connection.
        """
        pass

    async def open(self, host: str, port: int, credentials: dict, **kwargs):
        """open.
        Starts (open) a connection to external resource.
        """
        self.app = self.get_msal_app()
        return self

    def start(self):
        """Start.

        Processing variables and credentials.
        """
        try:
            self.processing_credentials()
            self.client_id, self.tenant_id, self.secret_id = (
                self.credentials.get(key)
                for key in ["client_id", "tenant_id", "secret_id"]
            )
        except Exception as err:
            self._logger.error(err)
            raise
