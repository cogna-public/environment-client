import asyncio
from environment.flood_monitoring import FloodClient
from environment.bathing_waters import BathingWatersClient
from environment.asset_management import AssetManagementClient
from environment.catchment_data import CatchmentDataClient


async def main():
    """
    An example of how to use the clients to get data from the APIs.
    """
    async with (
        FloodClient() as flood_client,
        BathingWatersClient() as bathing_waters_client,
        AssetManagementClient() as asset_management_client,
        CatchmentDataClient() as catchment_data_client,
    ):
        flood_warnings = await flood_client.get_flood_warnings()
        print(f"Found {len(flood_warnings)} flood warnings.")

        bathing_waters = await bathing_waters_client.get_bathing_waters()
        print(f"Found {len(bathing_waters)} bathing waters.")

        assets = await asset_management_client.get_assets()
        print(f"Found {len(assets)} assets.")

        catchment_data = await catchment_data_client.get_catchment_data()
        print(f"Found {len(catchment_data)} catchment data.")


if __name__ == "__main__":
    asyncio.run(main())
