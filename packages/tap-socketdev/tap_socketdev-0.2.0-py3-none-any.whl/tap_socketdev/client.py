"""REST client handling, including SocketDevStream base class."""

from __future__ import annotations

from requests.auth import HTTPBasicAuth
from singer_sdk import RESTStream


class SocketDevStream(RESTStream):
    """Socket stream class."""

    url_base = "https://api.socket.dev"

    @property
    def authenticator(self) -> HTTPBasicAuth:
        """Get an authenticator object.

        Returns:
            The authenticator instance for this REST stream.
        """
        return HTTPBasicAuth(
            username=self.config["api_key"],
            password="",
        )

    @property
    def http_headers(self) -> dict:
        """Return the http headers needed.

        Returns:
            A dictionary of HTTP headers.
        """
        return {"User-Agent": f"{self.tap_name}/{self._tap.plugin_version}"}
