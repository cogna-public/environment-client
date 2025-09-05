import pytest
from environment.water_quality_data_archive.client import WaterQualityDataArchiveClient
from environment.water_quality_data_archive.models import (
    SamplingPoint,
    Sample,
    Measurement,
    Determinand,
    Unit,
    DeterminandGroup,
    Purpose,
    EAArea,
    EASubArea,
    SampledMaterialType,
    SamplingPointType,
    SamplingPointTypeGroup,
)


pytestmark = pytest.mark.vcr()

# As of Sept 2025, the Water Quality Data Archive endpoints at
# https://environment.data.gov.uk/water-quality/view/* return 404.
# Skipping these VCR tests until replacement API is available.
pytestmark = [
    pytestmark,
    pytest.mark.skip(reason="Water Quality Data Archive API unavailable (404)"),
]


@pytest.fixture
def client():
    return WaterQualityDataArchiveClient()


@pytest.fixture(scope="module")
def vcr_cassette_dir():
    return "tests/cassettes/water_quality_data_archive"


@pytest.mark.asyncio
async def test_get_sampling_points(client):
    sampling_points = await client.get_sampling_points()
    assert isinstance(sampling_points, list)
    assert len(sampling_points) > 0
    assert isinstance(sampling_points[0], SamplingPoint)


@pytest.mark.asyncio
async def test_get_sampling_point_by_id(client):
    sps = await client.get_sampling_points()
    sampling_point_id = sps[0].id.split("/")[-1]
    sampling_point = await client.get_sampling_point_by_id(sampling_point_id)
    assert isinstance(sampling_point, SamplingPoint)
    assert sampling_point.id.endswith(f"/sampling-point/{sampling_point_id}")


@pytest.mark.asyncio
async def test_get_samples(client):
    samples = await client.get_samples()
    assert isinstance(samples, list)
    assert len(samples) > 0
    assert isinstance(samples[0], Sample)


@pytest.mark.asyncio
async def test_get_sample_by_id(client):
    samples = await client.get_samples()
    sample_id = samples[0].id.split("/")[-1]
    sample = await client.get_sample_by_id(sample_id)
    assert isinstance(sample, Sample)
    assert sample.id.endswith(f"/sample/{sample_id}")


@pytest.mark.asyncio
async def test_get_measurements(client):
    measurements = await client.get_measurements()
    assert isinstance(measurements, list)
    assert len(measurements) > 0
    assert isinstance(measurements[0], Measurement)


@pytest.mark.asyncio
async def test_get_measurement_by_id(client):
    ms = await client.get_measurements()
    measurement_id = ms[0].id.split("/")[-1]
    measurement = await client.get_measurement_by_id(measurement_id)
    assert isinstance(measurement, Measurement)
    assert measurement.id.endswith(f"/measurement/{measurement_id}")


@pytest.mark.asyncio
async def test_get_determinands(client):
    determinands = await client.get_determinands()
    assert isinstance(determinands, list)
    assert len(determinands) > 0
    assert isinstance(determinands[0], Determinand)


@pytest.mark.asyncio
async def test_get_units(client):
    units = await client.get_units()
    assert isinstance(units, list)
    assert len(units) > 0
    assert isinstance(units[0], Unit)


@pytest.mark.asyncio
async def test_get_determinand_groups(client):
    determinand_groups = await client.get_determinand_groups()
    assert isinstance(determinand_groups, list)
    assert len(determinand_groups) > 0
    assert isinstance(determinand_groups[0], DeterminandGroup)


@pytest.mark.asyncio
async def test_get_purposes(client):
    purposes = await client.get_purposes()
    assert isinstance(purposes, list)
    assert len(purposes) > 0
    assert isinstance(purposes[0], Purpose)


@pytest.mark.asyncio
async def test_get_ea_areas(client):
    ea_areas = await client.get_ea_areas()
    assert isinstance(ea_areas, list)
    assert len(ea_areas) > 0
    assert isinstance(ea_areas[0], EAArea)


@pytest.mark.asyncio
async def test_get_ea_subareas(client):
    ea_subareas = await client.get_ea_subareas()
    assert isinstance(ea_subareas, list)
    assert len(ea_subareas) > 0
    assert isinstance(ea_subareas[0], EASubArea)


@pytest.mark.asyncio
async def test_get_sampled_material_types(client):
    sampled_material_types = await client.get_sampled_material_types()
    assert isinstance(sampled_material_types, list)
    assert len(sampled_material_types) > 0
    assert isinstance(sampled_material_types[0], SampledMaterialType)


@pytest.mark.asyncio
async def test_get_sampling_point_types(client):
    sampling_point_types = await client.get_sampling_point_types()
    assert isinstance(sampling_point_types, list)
    assert len(sampling_point_types) > 0
    assert isinstance(sampling_point_types[0], SamplingPointType)


@pytest.mark.asyncio
async def test_get_sampling_point_type_groups(client):
    sampling_point_type_groups = await client.get_sampling_point_type_groups()
    assert isinstance(sampling_point_type_groups, list)
    assert len(sampling_point_type_groups) > 0
    assert isinstance(sampling_point_type_groups[0], SamplingPointTypeGroup)


@pytest.mark.asyncio
async def test_get_batch_measurements(client):
    batch_measurements = await client.get_batch_measurements()
    assert isinstance(batch_measurements, list)
    assert len(batch_measurements) > 0
    assert isinstance(batch_measurements[0], Measurement)
