import pytest
import vcr
import pytest_asyncio
from environment.flood_monitoring.client import FloodClient
from environment.flood_monitoring.models import (
    FloodWarning,
    FloodArea,
    Station,
    Measure,
    Reading,
)

pytestmark = pytest.mark.vcr()


@pytest_asyncio.fixture
async def client():
    async with FloodClient(verbose=True) as client_instance:
        yield client_instance

@pytest.fixture(scope="module")
def vcr_cassette_dir():
    return "tests/cassettes/integration"


@pytest.mark.asyncio
async def test_integration_get_flood_warnings(client):
    flood_warnings = await client.get_flood_warnings()
    assert isinstance(flood_warnings, list)
    assert len(flood_warnings) > 0
    assert isinstance(flood_warnings[0], FloodWarning)


@pytest.mark.asyncio
async def test_integration_get_flood_areas(client):
    flood_areas = await client.get_flood_areas()
    assert isinstance(flood_areas, list)
    assert len(flood_areas) > 0
    assert isinstance(flood_areas[0], FloodArea)


@pytest.mark.asyncio
async def test_integration_get_stations(client):
    stations = await client.get_stations()
    assert isinstance(stations, list)
    assert len(stations) > 0
    assert isinstance(stations[0], Station)


@pytest.mark.asyncio
async def test_integration_get_measures(client):
    measures = await client.get_measures()
    assert isinstance(measures, list)
    assert len(measures) > 0
    assert isinstance(measures[0], Measure)


@pytest.mark.asyncio
async def test_integration_get_readings(client):
    readings = await client.get_readings()
    assert isinstance(readings, list)
    assert len(readings) > 0
    assert isinstance(readings[0], Reading)
