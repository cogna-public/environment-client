import pytest
import vcr
from environment.bathing_waters.client import BathingWatersClient
from environment.bathing_waters.models import BathingWater


@pytest.mark.asyncio
@pytest.mark.vcr()
async def test_get_bathing_waters():
    client = BathingWatersClient()
    bathing_waters = await client.get_bathing_waters()
    assert isinstance(bathing_waters, list)
    assert isinstance(bathing_waters[0], BathingWater)