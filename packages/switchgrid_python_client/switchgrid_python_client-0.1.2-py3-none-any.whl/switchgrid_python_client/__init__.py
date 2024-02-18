"""
Class for checking the status of London Underground tube lines, as well as the Overground, DLR and Elizabeth Line.
"""

from aiohttp import ClientSession
from datetime import datetime
from dataclasses import dataclass
from typing import TypedDict

API_URL = "https://licarth.eu.ngrok.io/api/homeassistant/events"
# API_URL = "https://app.switchgrid.tech/api/homeassistant/events"


@dataclass
class Event:
    eventId: str
    startUtc: datetime
    endUtc: datetime
    summary: str
    description: str


@dataclass
class SwitchgridEventsResponse:
    events: list[Event]


def parse_api_response(response):
    try:
        events = list(
            map(
                lambda event: Event(
                    eventId=event["eventId"],
                    startUtc=datetime.fromisoformat(event["startUtc"]),
                    endUtc=datetime.fromisoformat(event["endUtc"]),
                    summary=event["summary"],
                    description=event["description"],
                ),
                response["events"],
            )
        )
        return SwitchgridEventsResponse(events=events)

    except Exception as e:
        print(e)
        return None


class SwitchgridData:
    _last_response: SwitchgridEventsResponse
    _session: ClientSession

    def __init__(self, session: ClientSession):
        """Initialize the SwitchgridData object."""
        self._data = {}
        self._last_updated = None
        self._session = session
        self._last_response = None

    async def update(self):
        """Get the latest data from Switchgrid."""
        async with self._session.get(API_URL) as response:
            if response.status != 200:
                return
            json_data = await response.json()
            self._last_response = parse_api_response(json_data)
            self._last_updated = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    @property
    def data(self):
        """Return the data."""
        return self._last_response

    @property
    def last_updated(self):
        """Return the time data was last updated."""
        return self._last_updated
