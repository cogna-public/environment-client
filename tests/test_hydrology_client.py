import pytest
from environment.hydrology.client import HydrologyClient
from environment.hydrology.models import Station, Measure, Reading


@pytest.fixture
def client():
    return HydrologyClient()


@pytest.mark.asyncio
async def test_get_stations(client, httpx_mock):
    httpx_mock.add_response(
        url="http://environment.data.gov.uk/hydrology/id/stations",
        json={
            "items": [
                {
                    "@id": "http://environment.data.gov.uk/hydrology/id/stations/1",
                    "label": "Station 1",
                    "notation": "S1",
                    "easting": 123.45,
                    "northing": 678.90,
                    "lat": 51.0,
                    "long": -1.0,
                    "riverName": "River A",
                    "town": "Town A",
                }
            ]
        },
    )
    stations = await client.get_stations()
    assert isinstance(stations, list)
    assert len(stations) == 1
    assert isinstance(stations[0], Station)
    assert stations[0].id == "http://environment.data.gov.uk/hydrology/id/stations/1"


@pytest.mark.asyncio
async def test_get_station_by_id(client, httpx_mock):
    station_id = "1"
    httpx_mock.add_response(
        url=f"http://environment.data.gov.uk/hydrology/id/stations/{station_id}",
        json={
            "items": [
                {
                    "@id": f"http://environment.data.gov.uk/hydrology/id/stations/{station_id}",
                    "label": "Station 1",
                    "notation": "S1",
                    "easting": 123.45,
                    "northing": 678.90,
                    "lat": 51.0,
                    "long": -1.0,
                    "riverName": "River A",
                    "town": "Town A",
                }
            ]
        },
    )
    station = await client.get_station_by_id(station_id)
    assert isinstance(station, Station)
    assert station.id == f"http://environment.data.gov.uk/hydrology/id/stations/{station_id}"


@pytest.mark.asyncio
async def test_get_measures(client, httpx_mock):
    httpx_mock.add_response(
        url="http://environment.data.gov.uk/hydrology/id/measures",
        json={
            "items": [
                {
                    "@id": "http://environment.data.gov.uk/hydrology/id/measures/1",
                    "label": "Measure 1",
                    "notation": "M1",
                    "parameter": "Flow",
                    "parameterName": "Flow",
                    "qualifier": "Mean",
                    "unitName": "m3/s",
                    "station": "http://environment.data.gov.uk/hydrology/id/stations/1",
                }
            ]
        },
    )
    measures = await client.get_measures()
    assert isinstance(measures, list)
    assert len(measures) == 1
    assert isinstance(measures[0], Measure)
    assert measures[0].id == "http://environment.data.gov.uk/hydrology/id/measures/1"


@pytest.mark.asyncio
async def test_get_measure_by_id(client, httpx_mock):
    measure_id = "1"
    httpx_mock.add_response(
        url=f"http://environment.data.gov.uk/hydrology/id/measures/{measure_id}",
        json={
            "items": [
                {
                    "@id": f"http://environment.data.gov.uk/hydrology/id/measures/{measure_id}",
                    "label": "Measure 1",
                    "notation": "M1",
                    "parameter": "Flow",
                    "parameterName": "Flow",
                    "qualifier": "Mean",
                    "unitName": "m3/s",
                    "station": "http://environment.data.gov.uk/hydrology/id/stations/1",
                }
            ]
        },
    )
    measure = await client.get_measure_by_id(measure_id)
    assert isinstance(measure, Measure)
    assert measure.id == f"http://environment.data.gov.uk/hydrology/id/measures/{measure_id}"


@pytest.mark.asyncio
async def test_get_readings(client, httpx_mock):
    httpx_mock.add_response(
        url="http://environment.data.gov.uk/hydrology/id/readings",
        json={
            "items": [
                {
                    "@id": "http://environment.data.gov.uk/hydrology/id/readings/1",
                    "dateTime": "2023-01-01T00:00:00Z",
                    "measure": "http://environment.data.gov.uk/hydrology/id/measures/1",
                    "value": 10.5,
                }
            ]
        },
    )
    readings = await client.get_readings()
    assert isinstance(readings, list)
    assert len(readings) == 1
    assert isinstance(readings[0], Reading)
    assert readings[0].id == "http://environment.data.gov.uk/hydrology/id/readings/1"


@pytest.mark.asyncio
async def test_get_reading_by_id(client, httpx_mock):
    reading_id = "1"
    httpx_mock.add_response(
        url=f"http://environment.data.gov.uk/hydrology/id/readings/{reading_id}",
        json={
            "items": [
                {
                    "@id": f"http://environment.data.gov.uk/hydrology/id/readings/{reading_id}",
                    "dateTime": "2023-01-01T00:00:00Z",
                    "measure": "http://environment.data.gov.uk/hydrology/id/measures/1",
                    "value": 10.5,
                }
            ]
        },
    )
    reading = await client.get_reading_by_id(reading_id)
    assert isinstance(reading, Reading)
    assert reading.id == f"http://environment.data.gov.uk/hydrology/id/readings/{reading_id}"
