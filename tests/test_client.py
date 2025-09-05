import pytest
from environment.flood_monitoring.client import FloodClient
from environment.flood_monitoring.models import (
    FloodWarning,
    FloodArea,
    Station,
    Measure,
    Reading,
)


@pytest.mark.asyncio
@pytest.mark.vcr()
async def test_get_flood_warnings():
    client = FloodClient()
    flood_warnings = await client.get_flood_warnings()
    assert isinstance(flood_warnings, list)
    assert isinstance(flood_warnings[0], FloodWarning)


@pytest.mark.asyncio
@pytest.mark.vcr()
async def test_get_flood_areas():
    client = FloodClient()
    flood_areas = await client.get_flood_areas()
    assert isinstance(flood_areas, list)
    assert isinstance(flood_areas[0], FloodArea)


@pytest.mark.asyncio
@pytest.mark.vcr()
async def test_get_stations():
    client = FloodClient()
    stations = await client.get_stations()
    assert isinstance(stations, list)
    assert isinstance(stations[0], Station)


@pytest.mark.asyncio
@pytest.mark.vcr()
async def test_get_measures():
    client = FloodClient()
    measures = await client.get_measures()
    assert isinstance(measures, list)
    assert isinstance(measures[0], Measure)


@pytest.mark.asyncio
@pytest.mark.vcr()
async def test_get_readings():
    client = FloodClient()
    readings = await client.get_readings()
    assert isinstance(readings, list)
    assert isinstance(readings[0], Reading)
