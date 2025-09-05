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

## Development

This project uses `uv` for dependency management.

- Install dependencies: `uv sync`
- Run tests: `just test`
- Run integration tests: `just test-integration`
- Lint: `just lint`
- Format: `just format`
