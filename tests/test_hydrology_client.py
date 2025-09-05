import pytest
from environment.hydrology.client import HydrologyClient
from environment.hydrology.models import Station, Measure, Reading

pytestmark = pytest.mark.vcr()


@pytest.fixture
def client():
    return HydrologyClient()


@pytest.fixture(scope="module")
def vcr_cassette_dir():
    return "tests/cassettes/hydrology"


@pytest.mark.asyncio
async def test_get_stations(client):
    stations = await client.get_stations()
    assert isinstance(stations, list)
    assert len(stations) > 0
    assert isinstance(stations[0], Station)


@pytest.mark.asyncio
async def test_get_station_by_id(client):
    stations = await client.get_stations()
    station_id = stations[0].id.split("/")[-1]
    station = await client.get_station_by_id(station_id)
    assert isinstance(station, Station)
    assert station.id.endswith(f"/stations/{station_id}")


@pytest.mark.asyncio
async def test_get_measures(client):
    measures = await client.get_measures()
    assert isinstance(measures, list)
    assert len(measures) > 0
    assert isinstance(measures[0], Measure)


@pytest.mark.asyncio
async def test_get_measure_by_id(client):
    measures = await client.get_measures()
    measure_id = measures[0].id.split("/")[-1]
    measure = await client.get_measure_by_id(measure_id)
    assert isinstance(measure, Measure)
    assert measure.id.endswith(f"/measures/{measure_id}")


@pytest.mark.asyncio
async def test_get_readings(client):
    measures = await client.get_measures()
    measure_id = measures[0].id.split("/")[-1]
    readings = await client.get_readings(measure_id=measure_id)
    assert isinstance(readings, list)
    assert len(readings) > 0
    assert isinstance(readings[0], Reading)


@pytest.mark.asyncio
async def test_get_reading_by_id(client):
    measures = await client.get_measures()
    measure_id = measures[0].id.split("/")[-1]
    readings = await client.get_readings(measure_id=measure_id)
    assert isinstance(readings, list)
    assert len(readings) > 0
    assert isinstance(readings[0], Reading)
