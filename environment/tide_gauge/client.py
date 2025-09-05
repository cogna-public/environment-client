"""
An async client for the UK Environment Agency's Tide Gauge API.
"""

import httpx
from .models import TideGaugeStation, TideGaugeReading


async def log_request(request):
    print(f">>> Request: {request.method} {request.url}")


async def log_response(response):
    await response.aread()
    print(f"<<< Response: {response.status_code}")
    print(response.text)


class TideGaugeClient(httpx.AsyncClient):
    """
    An async client for the UK Environment Agency's Tide Gauge API.
    """

    def __init__(self, timeout=30.0, verbose=False, **kwargs):
        """
        Initializes the client.

        Args:
            timeout (float, optional): The timeout for requests in seconds. Defaults to 30.0.
            verbose (bool, optional): If True, logs requests and responses. Defaults to False.
            **kwargs: Additional keyword arguments to pass to the httpx.AsyncClient constructor.
        """
        super().__init__(
            base_url="https://environment.data.gov.uk/flood-monitoring",
            timeout=timeout,
            **kwargs,
        )
        if verbose:
            self.event_hooks["request"].append(log_request)
            self.event_hooks["response"].append(log_response)

    async def get_tide_gauge_stations(self, **params) -> list[TideGaugeStation]:
        """
        Returns a list of tide gauge stations.

        Returns:
            list[TideGaugeStation]: A list of tide gauge stations.
        """
        response = await self.get("/id/tide-gauge-stations", params=params)
        response.raise_for_status()
        return [TideGaugeStation(**item) for item in response.json()["items"]]

    async def get_tide_gauge_station_by_id(self, station_id: str) -> TideGaugeStation:
        """
        Returns details of a single tide gauge station by ID.

        Args:
            station_id (str): The ID of the tide gauge station.

        Returns:
            TideGaugeStation: Details of the tide gauge station.
        """
        response = await self.get(f"/id/tide-gauge-stations/{station_id}")
        response.raise_for_status()
        return TideGaugeStation(**response.json()["items"][0])

    async def get_tide_gauge_readings(self, **params) -> list[TideGaugeReading]:
        """
        Returns a list of tide gauge readings.

        Returns:
            list[TideGaugeReading]: A list of tide gauge readings.
        """
        response = await self.get("/id/tide-gauge-readings", params=params)
        response.raise_for_status()
        return [TideGaugeReading(**item) for item in response.json()["items"]]

    async def get_tide_gauge_reading_by_id(self, reading_id: str) -> TideGaugeReading:
        """
        Returns details of a single tide gauge reading by ID.

        Args:
            reading_id (str): The ID of the tide gauge reading.

        Returns:
            TideGaugeReading: Details of the tide gauge reading.
        """
        response = await self.get(f"/id/tide-gauge-readings/{reading_id}")
        response.raise_for_status()
        return TideGaugeReading(**response.json()["items"][0])
