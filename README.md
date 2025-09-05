# Environment Client

A Python client for the environment.data.gov.uk APIs.

## Installation

```bash
uv pip install environment-client
```

## Usage

```python
import asyncio
from environment.flood_monitoring import FloodClient


async def main():
    """
    An example of how to use the FloodClient to get flood warnings.
    """
    async with FloodClient() as client:
        flood_warnings = await client.get_flood_warnings()
        print(f"Found {len(flood_warnings)} flood warnings.")


if __name__ == "__main__":
    asyncio.run(main())
```

## Supported APIs

- Real-time Flood Monitoring (flood warnings, areas, stations, measures, readings)
- Bathing Waters
- Asset Management
- Hydrology
- Rainfall
- Water Quality Data Archive (WQA)

### Important: WQA API Replacement

Note: The Water Quality Archive (WQA) APIs will be replaced later this year, meaning that the existing APIs will no longer work after Spring/Summer 2025. As of now, many `water-quality/view` endpoints return HTTP 404. We’ve:

- Added a `DeprecationWarning` when instantiating `WaterQualityDataArchiveClient`.
- Marked WQA tests as `skipped` until the replacement API is available.

For updates, see DEFRA’s support pages:
https://environment.data.gov.uk/apiportal/support

## Development

This project uses `uv` for dependency management.

- Install dependencies: `uv sync`
- Run tests: `just test`
- Run integration tests: `just test-integration`
- Lint: `just lint`
- Format: `just format`
