import pytest
from environment.tide_gauge.client import TideGaugeClient
from environment.tide_gauge.models import TideGaugeStation, TideGaugeReading

pytestmark = pytest.mark.vcr()


@pytest.fixture
def client():
    return TideGaugeClient()


@pytest.fixture(scope="module")
def vcr_cassette_dir():
    return "tests/cassettes/tide_gauge"


@pytest.mark.asyncio
async def test_get_tide_gauge_stations(client):
    stations = await client.get_tide_gauge_stations()
    assert isinstance(stations, list)
    assert len(stations) > 0
    assert isinstance(stations[0], TideGaugeStation)


@pytest.mark.asyncio
async def test_get_tide_gauge_station_by_id(client):
    stations = await client.get_tide_gauge_stations()
    station_id = stations[0].id.split("/")[-1]
    station = await client.get_tide_gauge_station_by_id(station_id)
    assert isinstance(station, TideGaugeStation)
    assert station.id.endswith(f"/stations/{station_id}")


@pytest.mark.asyncio
async def test_get_tide_gauge_readings(client):
    readings = await client.get_tide_gauge_readings()
    assert isinstance(readings, list)
    assert len(readings) > 0
    assert isinstance(readings[0], TideGaugeReading)


@pytest.mark.asyncio
async def test_get_tide_gauge_reading_by_id(client):
    readings = await client.get_tide_gauge_readings()
    full_id = readings[0].id
    marker = "/data/readings/"
    reading_suffix = full_id.split(marker)[-1]
    reading = await client.get_tide_gauge_reading_by_id(reading_suffix)
    assert isinstance(reading, TideGaugeReading)
    assert reading.id.endswith(reading_suffix)
