import pytest
from environment.rainfall.client import RainfallClient
from environment.rainfall.models import Station, Measure, Reading


@pytest.fixture
def client():
    return RainfallClient()


@pytest.mark.asyncio
async def test_get_stations(client, httpx_mock):
    httpx_mock.add_response(
        url="https://environment.data.gov.uk/rainfall/id/stations",
        json={
            "items": [
                {
                    "@id": "https://environment.data.gov.uk/rainfall/id/stations/1",
                    "label": "Rainfall Station 1",
                    "notation": "RS1",
                    "easting": 123.45,
                    "northing": 678.90,
                    "lat": 51.0,
                    "long": -1.0,
                    "riverName": "River B",
                    "town": "Town B",
                }
            ]
        },
    )
    stations = await client.get_stations()
    assert isinstance(stations, list)
    assert len(stations) == 1
    assert isinstance(stations[0], Station)
    assert stations[0].id == "https://environment.data.gov.uk/rainfall/id/stations/1"


@pytest.mark.asyncio
async def test_get_station_by_id(client, httpx_mock):
    station_id = "1"
    httpx_mock.add_response(
        url=f"https://environment.data.gov.uk/rainfall/id/stations/{station_id}",
        json={
            "items": [
                {
                    "@id": f"https://environment.data.gov.uk/rainfall/id/stations/{station_id}",
                    "label": "Rainfall Station 1",
                    "notation": "RS1",
                    "easting": 123.45,
                    "northing": 678.90,
                    "lat": 51.0,
                    "long": -1.0,
                    "riverName": "River B",
                    "town": "Town B",
                }
            ]
        },
    )
    station = await client.get_station_by_id(station_id)
    assert isinstance(station, Station)
    assert station.id == f"https://environment.data.gov.uk/rainfall/id/stations/{station_id}"


@pytest.mark.asyncio
async def test_get_measures(client, httpx_mock):
    httpx_mock.add_response(
        url="https://environment.data.gov.uk/rainfall/id/measures",
        json={
            "items": [
                {
                    "@id": "https://environment.data.gov.uk/rainfall/id/measures/1",
                    "label": "Rainfall Measure 1",
                    "notation": "RM1",
                    "parameter": "Rainfall",
                    "parameterName": "Rainfall",
                    "qualifier": "Total",
                    "unitName": "mm",
                    "station": "https://environment.data.gov.uk/rainfall/id/stations/1",
                }
            ]
        },
    )
    measures = await client.get_measures()
    assert isinstance(measures, list)
    assert len(measures) == 1
    assert isinstance(measures[0], Measure)
    assert measures[0].id == "https://environment.data.gov.uk/rainfall/id/measures/1"


@pytest.mark.asyncio
async def test_get_measure_by_id(client, httpx_mock):
    measure_id = "1"
    httpx_mock.add_response(
        url=f"https://environment.data.gov.uk/rainfall/id/measures/{measure_id}",
        json={
            "items": [
                {
                    "@id": f"https://environment.data.gov.uk/rainfall/id/measures/{measure_id}",
                    "label": "Rainfall Measure 1",
                    "notation": "RM1",
                    "parameter": "Rainfall",
                    "parameterName": "Rainfall",
                    "qualifier": "Total",
                    "unitName": "mm",
                    "station": "https://environment.data.gov.uk/rainfall/id/stations/1",
                }
            ]
        },
    )
    measure = await client.get_measure_by_id(measure_id)
    assert isinstance(measure, Measure)
    assert measure.id == f"https://environment.data.gov.uk/rainfall/id/measures/{measure_id}"


@pytest.mark.asyncio
async def test_get_readings(client, httpx_mock):
    httpx_mock.add_response(
        url="https://environment.data.gov.uk/rainfall/id/readings",
        json={
            "items": [
                {
                    "@id": "https://environment.data.gov.uk/rainfall/id/readings/1",
                    "dateTime": "2023-01-01T00:00:00Z",
                    "measure": "https://environment.data.gov.uk/rainfall/id/measures/1",
                    "value": 10.5,
                }
            ]
        },
    )
    readings = await client.get_readings()
    assert isinstance(readings, list)
    assert len(readings) == 1
    assert isinstance(readings[0], Reading)
    assert readings[0].id == "https://environment.data.gov.uk/rainfall/id/readings/1"


@pytest.mark.asyncio
async def test_get_reading_by_id(client, httpx_mock):
    reading_id = "1"
    httpx_mock.add_response(
        url=f"https://environment.data.gov.uk/rainfall/id/readings/{reading_id}",
        json={
            "items": [
                {
                    "@id": f"https://environment.data.gov.uk/rainfall/id/readings/{reading_id}",
                    "dateTime": "2023-01-01T00:00:00Z",
                    "measure": "https://environment.data.gov.uk/rainfall/id/measures/1",
                    "value": 10.5,
                }
            ]
        },
    )
    reading = await client.get_reading_by_id(reading_id)
    assert isinstance(reading, Reading)
    assert reading.id == f"https://environment.data.gov.uk/rainfall/id/readings/{reading_id}"
