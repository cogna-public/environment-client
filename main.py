import asyncio
from environment.flood_monitoring import FloodClient
from environment.bathing_waters import BathingWatersClient
from environment.asset_management import AssetManagementClient
from environment.catchment_data import CatchmentDataClient
from environment.public_register import PublicRegisterClient


async def main():
    """
    An example of how to use the clients to get data from the APIs.
    """
    async with (
        FloodClient() as flood_client,
        BathingWatersClient() as bathing_waters_client,
        AssetManagementClient() as asset_management_client,
        CatchmentDataClient() as catchment_data_client,
        PublicRegisterClient() as public_register_client,
    ):
        flood_warnings = await flood_client.get_flood_warnings()
        print(f"Found {len(flood_warnings)} flood warnings.")

        bathing_waters = await bathing_waters_client.get_bathing_waters()
        print(f"Found {len(bathing_waters)} bathing waters.")

        assets = await asset_management_client.get_assets()
        print(f"Found {len(assets)} assets.")

        catchment_data = await catchment_data_client.get_catchment_data()
        print(f"Found {len(catchment_data)} catchment data.")

        # Search for waste operations registrations
        waste_operations = await public_register_client.get_waste_operations(limit=5)
        print(f"Found {len(waste_operations.items)} waste operations.")

        # Search across all registers
        all_registrations = await public_register_client.search_all_registers(name_search="Limited", limit=5)
        print(f"Found {len(all_registrations.items)} registrations with 'Limited' in the name.")


if __name__ == "__main__":
    asyncio.run(main())
