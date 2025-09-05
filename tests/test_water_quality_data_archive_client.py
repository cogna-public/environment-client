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


@pytest.fixture
def client():
    return WaterQualityDataArchiveClient()


@pytest.mark.asyncio
async def test_get_sampling_points(client, httpx_mock):
    httpx_mock.add_response(
        url="https://environment.data.gov.uk/water-quality/view/id/sampling-point",
        json={
            "items": [
                {
                    "@id": "https://environment.data.gov.uk/water-quality/view/id/sampling-point/1",
                    "label": "Sampling Point 1",
                    "easting": 123.45,
                    "northing": 678.90,
                    "lat": 51.0,
                    "long": -1.0,
                    "description": "Description 1",
                }
            ]
        },
    )
    sampling_points = await client.get_sampling_points()
    assert isinstance(sampling_points, list)
    assert len(sampling_points) == 1
    assert isinstance(sampling_points[0], SamplingPoint)
    assert sampling_points[0].id == "https://environment.data.gov.uk/water-quality/view/id/sampling-point/1"


@pytest.mark.asyncio
async def test_get_sampling_point_by_id(client, httpx_mock):
    sampling_point_id = "1"
    httpx_mock.add_response(
        url=f"https://environment.data.gov.uk/water-quality/view/id/sampling-point/{sampling_point_id}",
        json={
            "items": [
                {
                    "@id": f"https://environment.data.gov.uk/water-quality/view/id/sampling-point/{sampling_point_id}",
                    "label": "Sampling Point 1",
                    "easting": 123.45,
                    "northing": 678.90,
                    "lat": 51.0,
                    "long": -1.0,
                    "description": "Description 1",
                }
            ]
        },
    )
    sampling_point = await client.get_sampling_point_by_id(sampling_point_id)
    assert isinstance(sampling_point, SamplingPoint)
    assert sampling_point.id == f"https://environment.data.gov.uk/water-quality/view/id/sampling-point/{sampling_point_id}"


@pytest.mark.asyncio
async def test_get_samples(client, httpx_mock):
    httpx_mock.add_response(
        url="https://environment.data.gov.uk/water-quality/view/data/sample",
        json={
            "items": [
                {
                    "@id": "https://environment.data.gov.uk/water-quality/view/data/sample/1",
                    "sampleDateTime": "2023-01-01T00:00:00Z",
                    "samplingPoint": "https://environment.data.gov.uk/water-quality/view/id/sampling-point/1",
                    "purpose": "Routine",
                }
            ]
        },
    )
    samples = await client.get_samples()
    assert isinstance(samples, list)
    assert len(samples) == 1
    assert isinstance(samples[0], Sample)
    assert samples[0].id == "https://environment.data.gov.uk/water-quality/view/data/sample/1"


@pytest.mark.asyncio
async def test_get_sample_by_id(client, httpx_mock):
    sample_id = "1"
    httpx_mock.add_response(
        url=f"https://environment.data.gov.uk/water-quality/view/data/sample/{sample_id}",
        json={
            "items": [
                {
                    "@id": f"https://environment.data.gov.uk/water-quality/view/data/sample/{sample_id}",
                    "sampleDateTime": "2023-01-01T00:00:00Z",
                    "samplingPoint": "https://environment.data.gov.uk/water-quality/view/id/sampling-point/1",
                    "purpose": "Routine",
                }
            ]
        },
    )
    sample = await client.get_sample_by_id(sample_id)
    assert isinstance(sample, Sample)
    assert sample.id == f"https://environment.data.gov.uk/water-quality/view/data/sample/{sample_id}"


@pytest.mark.asyncio
async def test_get_measurements(client, httpx_mock):
    httpx_mock.add_response(
        url="https://environment.data.gov.uk/water-quality/view/data/measurement",
        json={
            "items": [
                {
                    "@id": "https://environment.data.gov.uk/water-quality/view/data/measurement/1",
                    "measurementDateTime": "2023-01-01T00:00:00Z",
                    "sample": "https://environment.data.gov.uk/water-quality/view/data/sample/1",
                    "determinand": "https://environment.data.gov.uk/water-quality/view/def/determinands/1",
                    "value": 10.5,
                    "unit": "mg/L",
                }
            ]
        },
    )
    measurements = await client.get_measurements()
    assert isinstance(measurements, list)
    assert len(measurements) == 1
    assert isinstance(measurements[0], Measurement)
    assert measurements[0].id == "https://environment.data.gov.uk/water-quality/view/data/measurement/1"


@pytest.mark.asyncio
async def test_get_measurement_by_id(client, httpx_mock):
    measurement_id = "1"
    httpx_mock.add_response(
        url=f"https://environment.data.gov.uk/water-quality/view/data/measurement/{measurement_id}",
        json={
            "items": [
                {
                    "@id": f"https://environment.data.gov.uk/water-quality/view/data/measurement/{measurement_id}",
                    "measurementDateTime": "2023-01-01T00:00:00Z",
                    "sample": "https://environment.data.gov.uk/water-quality/view/data/sample/1",
                    "determinand": "https://environment.data.gov.uk/water-quality/view/def/determinands/1",
                    "value": 10.5,
                    "unit": "mg/L",
                }
            ]
        },
    )
    measurement = await client.get_measurement_by_id(measurement_id)
    assert isinstance(measurement, Measurement)
    assert measurement.id == f"https://environment.data.gov.uk/water-quality/view/data/measurement/{measurement_id}"


@pytest.mark.asyncio
async def test_get_determinands(client, httpx_mock):
    httpx_mock.add_response(
        url="https://environment.data.gov.uk/water-quality/view/def/determinands",
        json={
            "items": [
                {
                    "@id": "https://environment.data.gov.uk/water-quality/view/def/determinands/1",
                    "label": "Determinand 1",
                }
            ]
        },
    )
    determinands = await client.get_determinands()
    assert isinstance(determinands, list)
    assert len(determinands) == 1
    assert isinstance(determinands[0], Determinand)
    assert determinands[0].id == "https://environment.data.gov.uk/water-quality/view/def/determinands/1"


@pytest.mark.asyncio
async def test_get_units(client, httpx_mock):
    httpx_mock.add_response(
        url="https://environment.data.gov.uk/water-quality/view/def/units",
        json={
            "items": [
                {
                    "@id": "https://environment.data.gov.uk/water-quality/view/def/units/1",
                    "label": "Unit 1",
                }
            ]
        },
    )
    units = await client.get_units()
    assert isinstance(units, list)
    assert len(units) == 1
    assert isinstance(units[0], Unit)
    assert units[0].id == "https://environment.data.gov.uk/water-quality/view/def/units/1"


@pytest.mark.asyncio
async def test_get_determinand_groups(client, httpx_mock):
    httpx_mock.add_response(
        url="https://environment.data.gov.uk/water-quality/view/def/determinand-groups",
        json={
            "items": [
                {
                    "@id": "https://environment.data.gov.uk/water-quality/view/def/determinand-groups/1",
                    "label": "Determinand Group 1",
                }
            ]
        },
    )
    determinand_groups = await client.get_determinand_groups()
    assert isinstance(determinand_groups, list)
    assert len(determinand_groups) == 1
    assert isinstance(determinand_groups[0], DeterminandGroup)
    assert determinand_groups[0].id == "https://environment.data.gov.uk/water-quality/view/def/determinand-groups/1"


@pytest.mark.asyncio
async def test_get_purposes(client, httpx_mock):
    httpx_mock.add_response(
        url="https://environment.data.gov.uk/water-quality/view/def/purposes",
        json={
            "items": [
                {
                    "@id": "https://environment.data.gov.uk/water-quality/view/def/purposes/1",
                    "label": "Purpose 1",
                }
            ]
        },
    )
    purposes = await client.get_purposes()
    assert isinstance(purposes, list)
    assert len(purposes) == 1
    assert isinstance(purposes[0], Purpose)
    assert purposes[0].id == "https://environment.data.gov.uk/water-quality/view/def/purposes/1"


@pytest.mark.asyncio
async def test_get_ea_areas(client, httpx_mock):
    httpx_mock.add_response(
        url="https://environment.data.gov.uk/water-quality/view/id/ea-area",
        json={
            "items": [
                {
                    "@id": "https://environment.data.gov.uk/water-quality/view/id/ea-area/1",
                    "label": "EA Area 1",
                }
            ]
        },
    )
    ea_areas = await client.get_ea_areas()
    assert isinstance(ea_areas, list)
    assert len(ea_areas) == 1
    assert isinstance(ea_areas[0], EAArea)
    assert ea_areas[0].id == "https://environment.data.gov.uk/water-quality/view/id/ea-area/1"


@pytest.mark.asyncio
async def test_get_ea_subareas(client, httpx_mock):
    httpx_mock.add_response(
        url="https://environment.data.gov.uk/water-quality/view/id/ea-subarea",
        json={
            "items": [
                {
                    "@id": "https://environment.data.gov.uk/water-quality/view/id/ea-subarea/1",
                    "label": "EA SubArea 1",
                }
            ]
        },
    )
    ea_subareas = await client.get_ea_subareas()
    assert isinstance(ea_subareas, list)
    assert len(ea_subareas) == 1
    assert isinstance(ea_subareas[0], EASubArea)
    assert ea_subareas[0].id == "https://environment.data.gov.uk/water-quality/view/id/ea-subarea/1"


@pytest.mark.asyncio
async def test_get_sampled_material_types(client, httpx_mock):
    httpx_mock.add_response(
        url="https://environment.data.gov.uk/water-quality/view/def/sampled-material-types",
        json={
            "items": [
                {
                    "@id": "https://environment.data.gov.uk/water-quality/view/def/sampled-material-types/1",
                    "label": "Sampled Material Type 1",
                }
            ]
        },
    )
    sampled_material_types = await client.get_sampled_material_types()
    assert isinstance(sampled_material_types, list)
    assert len(sampled_material_types) == 1
    assert isinstance(sampled_material_types[0], SampledMaterialType)
    assert sampled_material_types[0].id == "https://environment.data.gov.uk/water-quality/view/def/sampled-material-types/1"


@pytest.mark.asyncio
async def test_get_sampling_point_types(client, httpx_mock):
    httpx_mock.add_response(
        url="https://environment.data.gov.uk/water-quality/view/def/sampling-point-types",
        json={
            "items": [
                {
                    "@id": "https://environment.data.gov.uk/water-quality/view/def/sampling-point-types/1",
                    "label": "Sampling Point Type 1",
                }
            ]
        },
    )
    sampling_point_types = await client.get_sampling_point_types()
    assert isinstance(sampling_point_types, list)
    assert len(sampling_point_types) == 1
    assert isinstance(sampling_point_types[0], SamplingPointType)
    assert sampling_point_types[0].id == "https://environment.data.gov.uk/water-quality/view/def/sampling-point-types/1"


@pytest.mark.asyncio
async def test_get_sampling_point_type_groups(client, httpx_mock):
    httpx_mock.add_response(
        url="https://environment.data.gov.uk/water-quality/view/def/sampling-point-type-groups",
        json={
            "items": [
                {
                    "@id": "https://environment.data.gov.uk/water-quality/view/def/sampling-point-type-groups/1",
                    "label": "Sampling Point Type Group 1",
                }
            ]
        },
    )
    sampling_point_type_groups = await client.get_sampling_point_type_groups()
    assert isinstance(sampling_point_type_groups, list)
    assert len(sampling_point_type_groups) == 1
    assert isinstance(sampling_point_type_groups[0], SamplingPointTypeGroup)
    assert sampling_point_type_groups[0].id == "https://environment.data.gov.uk/water-quality/view/def/sampling-point-type-groups/1"


@pytest.mark.asyncio
async def test_get_batch_measurements(client, httpx_mock):
    httpx_mock.add_response(
        url="https://environment.data.gov.uk/water-quality/view/batch/measurement",
        json={
            "items": [
                {
                    "@id": "https://environment.data.gov.uk/water-quality/view/data/measurement/1",
                    "measurementDateTime": "2023-01-01T00:00:00Z",
                    "sample": "https://environment.data.gov.uk/water-quality/view/data/sample/1",
                    "determinand": "https://environment.data.gov.uk/water-quality/view/def/determinands/1",
                    "value": 10.5,
                    "unit": "mg/L",
                }
            ]
        },
    )
    batch_measurements = await client.get_batch_measurements()
    assert isinstance(batch_measurements, list)
    assert len(batch_measurements) == 1
    assert isinstance(batch_measurements[0], Measurement)
    assert batch_measurements[0].id == "https://environment.data.gov.uk/water-quality/view/data/measurement/1"
