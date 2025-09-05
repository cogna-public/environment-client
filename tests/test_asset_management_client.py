import pytest
from environment.asset_management.client import AssetManagementClient
from environment.asset_management.models import Asset


@pytest.mark.asyncio
@pytest.mark.vcr()
async def test_get_assets():
    client = AssetManagementClient()
    assets = await client.get_assets()
    assert isinstance(assets, list)
    assert isinstance(assets[0], Asset)
