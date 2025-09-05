import pytest
from environment.flood_monitoring.client import FloodClient
from environment.flood_monitoring.models import (
    FloodWarning,
    FloodArea,
    Station,
    Measure,
    Reading,
)


@pytest.fixture
def client():
    return FloodClient()


@pytest.mark.asyncio
async def test_get_flood_warnings(client, httpx_mock):
    httpx_mock.add_response(
        url="https://environment.data.gov.uk/flood-monitoring/id/floods",
        json={
            "items": [
                {
                    "@id": "1",
                    "description": "d",
                    "eaAreaName": "ea",
                    "eaRegionName": "ea",
                    "floodArea": {
                        "@id": "1",
                        "county": "c",
                        "notation": "n",
                        "polygon": "p",
                        "riverOrSea": "r",
                    },
                    "floodAreaID": "f",
                    "isTidal": False,
                    "message": "m",
                    "severity": "s",
                    "severityLevel": 1,
                    "timeMessageChanged": "t",
                    "timeRaised": "t",
                    "timeSeverityChanged": "t",
                }
            ]
        },
    )
    flood_warnings = await client.get_flood_warnings()
    assert isinstance(flood_warnings, list)
    assert isinstance(flood_warnings[0], FloodWarning)


@pytest.mark.asyncio
async def test_get_flood_areas(client, httpx_mock):
    httpx_mock.add_response(
        url="https://environment.data.gov.uk/flood-monitoring/id/flood-areas",
        json={
            "items": [
                {
                    "@id": "1",
                    "county": "c",
                    "description": "d",
                    "eaAreaName": "ea",
                    "floodWatchArea": "f",
                    "fwdCode": "f",
                    "label": "l",
                    "lat": 1.0,
                    "long": 1.0,
                    "notation": "n",
                    "polygon": "p",
                    "quickDialNumber": "q",
                    "riverOrSea": "r",
                }
            ]
        },
    )
    flood_areas = await client.get_flood_areas()
    assert isinstance(flood_areas, list)
    assert isinstance(flood_areas[0], FloodArea)


@pytest.mark.asyncio
async def test_get_stations(client, httpx_mock):
    httpx_mock.add_response(
        url="https://environment.data.gov.uk/flood-monitoring/id/stations",
        json={
            "items": [
                {
                    "@id": "1",
                    "RLOIid": "r",
                    "catchmentName": "c",
                    "dateOpened": "d",
                    "easting": 1,
                    "label": "l",
                    "lat": 1.0,
                    "long": 1.0,
                    "measures": [],
                    "northing": 1,
                    "notation": "n",
                    "riverName": "r",
                    "stageScale": "s",
                    "stationReference": "s",
                    "status": "s",
                    "town": "t",
                    "wiskiID": "w",
                }
            ]
        },
    )
    stations = await client.get_stations()
    assert isinstance(stations, list)
    assert isinstance(stations[0], Station)


@pytest.mark.asyncio
async def test_get_measures(client, httpx_mock):
    httpx_mock.add_response(
        url="https://environment.data.gov.uk/flood-monitoring/id/measures",
        json={
            "items": [
                {
                    "@id": "1",
                    "datumType": "d",
                    "label": "l",
                    "latestReading": {
                        "@id": "1",
                        "date": "d",
                        "dateTime": "d",
                        "measure": "m",
                        "value": 1.0,
                    },
                    "notation": "n",
                    "parameter": "p",
                    "parameterName": "p",
                    "period": 1,
                    "qualifier": "q",
                    "station": "s",
                    "stationReference": "s",
                    "unit": "u",
                    "unitName": "u",
                    "valueType": "v",
                }
            ]
        },
    )
    measures = await client.get_measures()
    assert isinstance(measures, list)
    assert isinstance(measures[0], Measure)


@pytest.mark.asyncio
async def test_get_readings(client, httpx_mock):
    httpx_mock.add_response(
        url="https://environment.data.gov.uk/flood-monitoring/data/readings",
        json={"items": [{"@id": "1", "dateTime": "d", "measure": "m", "value": 1.0}]},
    )
    readings = await client.get_readings()
    assert isinstance(readings, list)
    assert isinstance(readings[0], Reading)
