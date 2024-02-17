"""Stream type classes for tap-socketdev."""

from __future__ import annotations

import typing as t

from singer_sdk import typing as th

from tap_socketdev.client import SocketDevStream

if t.TYPE_CHECKING:
    from requests import Response


class Reports(SocketDevStream):
    """Reports stream."""

    name = "reports"
    path = "/v0/report/list"
    records_jsonpath = "$[*]"
    primary_keys: t.ClassVar[list[str]] = ["id"]
    replication_key = None

    schema = th.PropertiesList(
        th.Property(
            "id",
            th.StringType,
            description="The report's unique identifier",
        ),
        th.Property(
            "url",
            th.StringType,
            description="The URL to the report",
        ),
    ).to_dict()


class Organizations(SocketDevStream):
    """Organizations stream."""

    name = "organizations"
    path = "/v0/organizations"
    primary_keys: t.ClassVar[list[str]] = ["id"]
    replication_key = None

    schema = th.PropertiesList(
        th.Property(
            "id",
            th.StringType,
            description="The organization's unique identifier",
        ),
        th.Property(
            "name",
            th.StringType,
            description="The organization's name",
        ),
        th.Property(
            "image",
            th.StringType,
            description="The organization's image",
        ),
        th.Property(
            "plan",
            th.StringType,
            description="The organization's plan",
        ),
    ).to_dict()

    def parse_response(
        self,
        response: Response,
    ) -> t.Generator[dict, None, None]:
        """Parse the response and return an iterator of result rows.

        Args:
            response: The response object.

        Yields:
            An iterator of parsed records.
        """
        yield from response.json()["organizations"].values()
