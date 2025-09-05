import pytest
from environment.catchment_data.client import CatchmentDataClient


@pytest.fixture
def client():
    return CatchmentDataClient()


@pytest.mark.asyncio
async def test_get_catchment_data(client):
    # Since the actual API endpoint is unknown, we're testing that it returns an empty list.
    # If the API endpoint is determined in the future, this test should be updated.
    catchment_data = await client.get_catchment_data()
    assert isinstance(catchment_data, list)
    assert len(catchment_data) == 0
