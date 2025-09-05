import pytest
from environment.tide_gauge.client import TideGaugeClient
from environment.tide_gauge.models import TideGaugeStation, TideGaugeReading


@pytest.fixture
def client():
    return TideGaugeClient()


@pytest.mark.asyncio
async def test_get_tide_gauge_stations(client, httpx_mock):
    httpx_mock.add_response(
        url="https://environment.data.gov.uk/flood-monitoring/id/tide-gauge-stations",
        json={
            "items": [
                {
                    "@id": "https://environment.data.gov.uk/flood-monitoring/id/tide-gauge-stations/1",
                    "label": "Tide Gauge Station 1",
                    "notation": "TGS1",
                    "easting": 123.45,
                    "northing": 678.90,
                    "lat": 51.0,
                    "long": -1.0,
                    "town": "Coastal Town A",
                }
            ]
        },
    )
    stations = await client.get_tide_gauge_stations()
    assert isinstance(stations, list)
    assert len(stations) == 1
    assert isinstance(stations[0], TideGaugeStation)
    assert stations[0].id == "https://environment.data.gov.uk/flood-monitoring/id/tide-gauge-stations/1"


@pytest.mark.asyncio
async def test_get_tide_gauge_station_by_id(client, httpx_mock):
    station_id = "1"
    httpx_mock.add_response(
        url=f"https://environment.data.gov.uk/flood-monitoring/id/tide-gauge-stations/{station_id}",
        json={
            "items": [
                {
                    "@id": f"https://environment.data.gov.uk/flood-monitoring/id/tide-gauge-stations/{station_id}",
                    "label": "Tide Gauge Station 1",
                    "notation": "TGS1",
                    "easting": 123.45,
                    "northing": 678.90,
                    "lat": 51.0,
                    "long": -1.0,
                    "town": "Coastal Town A",
                }
            ]
        },
    )
    station = await client.get_tide_gauge_station_by_id(station_id)
    assert isinstance(station, TideGaugeStation)
    assert station.id == f"https://environment.data.gov.uk/flood-monitoring/id/tide-gauge-stations/{station_id}"


@pytest.mark.asyncio
async def test_get_tide_gauge_readings(client, httpx_mock):
    httpx_mock.add_response(
        url="https://environment.data.gov.uk/flood-monitoring/id/tide-gauge-readings",
        json={
            "items": [
                {
                    "@id": "https://environment.data.gov.uk/flood-monitoring/id/tide-gauge-readings/1",
                    "dateTime": "2023-01-01T00:00:00Z",
                    "measure": "https://environment.data.gov.uk/flood-monitoring/id/measures/1",
                    "value": 10.5,
                }
            ]
        },
    )
    readings = await client.get_tide_gauge_readings()
    assert isinstance(readings, list)
    assert len(readings) == 1
    assert isinstance(readings[0], TideGaugeReading)
    assert readings[0].id == "https://environment.data.gov.uk/flood-monitoring/id/tide-gauge-readings/1"


@pytest.mark.asyncio
async def test_get_tide_gauge_reading_by_id(client, httpx_mock):
    reading_id = "1"
    httpx_mock.add_response(
        url=f"https://environment.data.gov.uk/flood-monitoring/id/tide-gauge-readings/{reading_id}",
        json={
            "items": [
                {
                    "@id": f"https://environment.data.gov.uk/flood-monitoring/id/tide-gauge-readings/{reading_id}",
                    "dateTime": "2023-01-01T00:00:00Z",
                    "measure": "https://environment.data.gov.uk/flood-monitoring/id/measures/1",
                    "value": 10.5,
                }
            ]
        },
    )
    reading = await client.get_tide_gauge_reading_by_id(reading_id)
    assert isinstance(reading, TideGaugeReading)
    assert reading.id == f"https://environment.data.gov.uk/flood-monitoring/id/tide-gauge-readings/{reading_id}"
