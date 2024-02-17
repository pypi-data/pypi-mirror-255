"""Socket tap class."""

from __future__ import annotations

import typing as t

from singer_sdk import Tap
from singer_sdk import typing as th

from tap_socketdev import streams

if t.TYPE_CHECKING:
    from singer_sdk.streams import RESTStream


class TapSocketDev(Tap):
    """Singer tap for Socket.dev."""

    name = "tap-socketdev"

    config_jsonschema = th.PropertiesList(
        th.Property(
            "api_key",
            th.StringType,
            required=True,
            description="API Key for Socket",
        ),
        th.Property(
            "start_date",
            th.DateTimeType,
            description="Earliest datetime to get data from",
        ),
    ).to_dict()

    def discover_streams(self) -> list[RESTStream]:
        """Return a list of discovered streams.

        Returns:
            A list of Socket streams.
        """
        return [streams.Reports(tap=self), streams.Organizations(tap=self)]
