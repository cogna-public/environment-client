import asyncio

import pytest
from environment.flood_monitoring import FloodClient


@pytest.mark.asyncio
async def test_pyppi_install_and_basic_calls():
    # Ensures we can import from the installed PyPI package and make live calls.
    async with FloodClient() as client:
        warnings = await client.get_flood_warnings()
        stations = await client.get_stations()

        assert isinstance(warnings, list)
        assert isinstance(stations, list)
        # Expect non-empty results under normal conditions
        assert len(stations) > 0

