import asyncio

from environment.flood_monitoring import FloodClient


async def main() -> None:
    # Minimal smoke: hit a couple of endpoints and print counts.
    async with FloodClient(verbose=True) as client:
        flood_warnings = await client.get_flood_warnings()
        print(f"Flood warnings: {len(flood_warnings)}")

        stations = await client.get_stations()
        print(f"Stations: {len(stations)}")


if __name__ == "__main__":
    asyncio.run(main())

