# DEFRA Environment Client 🌿

[![PyPI version](https://img.shields.io/pypi/v/environment-client.svg)](https://pypi.org/project/environment-client/)
[![GitHub Release](https://img.shields.io/github/v/release/cogna-public/environment-client?display_name=release)](https://github.com/cogna-public/environment-client/releases)
[![Publish Status](https://github.com/cogna-public/environment-client/actions/workflows/publish.yml/badge.svg)](https://github.com/cogna-public/environment-client/actions/workflows/publish.yml)
[![Python Versions](https://img.shields.io/pypi/pyversions/environment-client.svg)](https://pypi.org/project/environment-client/)
[![License: MIT](https://img.shields.io/pypi/l/environment-client.svg)](LICENSE)

Python client for DEFRA’s environment.data.gov.uk APIs — fast, typed, and async‑friendly. 🌟

## Installation 🧰

```bash
uv pip install environment-client
```

## Usage 🐍

```python
import asyncio
from environment.flood_monitoring import FloodClient
from environment.public_register import PublicRegisterClient


async def main():
    """
    An example of how to use the clients to get data from the APIs.
    """
    async with (
        FloodClient() as flood_client,
        PublicRegisterClient() as public_register_client,
    ):
        # Get flood warnings
        flood_warnings = await flood_client.get_flood_warnings()
        print(f"Found {len(flood_warnings)} flood warnings.")
        
        # Search for waste operations registrations
        waste_operations = await public_register_client.get_waste_operations(limit=5)
        print(f"Found {len(waste_operations.items)} waste operations.")
        
        # Search across all registers
        all_registrations = await public_register_client.search_all_registers(name_search="Limited", limit=5)
        print(f"Found {len(all_registrations.items)} registrations with 'Limited' in the name.")


if __name__ == "__main__":
    asyncio.run(main())
```

## Supported APIs 🌐

- Real-time Flood Monitoring (flood warnings, areas, stations, measures, readings)
- Bathing Waters
- Asset Management
- Hydrology
- Rainfall
- Water Quality Data Archive (WQA)
- Public Register (waste operations, end-of-life vehicles, industrial installations, water discharges, radioactive substances, waste carriers/brokers, waste exemptions, water discharge exemptions, scrap metal dealers, enforcement actions, flood risk exemptions)

## Package Name vs Import Path 🔤

- Distribution (PyPI): `environment-client`
- Import path (Python): `environment`

Example:

```python
from environment.flood_monitoring import FloodClient
```

Note: The distribution is named `environment-client` while the import path is `environment`. This keeps imports concise but clarifies the project scope on PyPI.

### ⚠️ Important: WQA API Replacement

Note: The Water Quality Archive (WQA) APIs will be replaced later this year, meaning that the existing APIs will no longer work after Spring/Summer 2025. As of now, many `water-quality/view` endpoints return HTTP 404. We’ve:

- Added a `DeprecationWarning` when instantiating `WaterQualityDataArchiveClient`.
- Marked WQA tests as `skipped` until the replacement API is available.

For updates, see DEFRA’s support pages:
https://environment.data.gov.uk/apiportal/support

## Implementation Status 📊

- Flood Monitoring
  - Base: `https://environment.data.gov.uk/flood-monitoring`
  - Implemented: `get_flood_warnings` (`/id/floods`), `get_flood_areas` (`/id/floodAreas`), `get_stations` (`/id/stations`), `get_station_by_id`, `get_measures` (`/id/measures`), `get_measure_by_id`, `get_readings` (`/data/readings`), `get_reading_by_id`.
  - Notes: Uses canonical `/id` for entities and `/data` for readings. Integration tests use VCR.

- Rainfall
  - Base: Flood Monitoring (parameterised)
  - Implemented: Stations and measures filtered with `parameter=rainfall`; readings via `/data/readings?parameter=rainfall`; reading-by-id via `/data/readings/{measure_id}/{timestamp}`.
  - Notes: Rainfall is part of Flood Monitoring; not a separate base path.

- Tide Gauge
  - Base: Flood Monitoring (typed)
  - Implemented: Stations via `/id/stations?type=TideGauge`, station-by-id, readings via `/data/readings?stationType=TideGauge`, reading-by-id via `/data/readings/{measure_id}/{timestamp}`.

- Hydrology
  - Base: `https://environment.data.gov.uk/hydrology`
  - Implemented: Stations, station-by-id, measures, measure-by-id, readings per-measure via `/id/measures/{id}/readings` (lists do not expose a global `/id/readings`).
  - Notes: Some fields (e.g., `status`, `riverName`, `station`, `unit`) are normalised for model compatibility.

- Bathing Waters
  - Base: `https://environment.data.gov.uk`
  - Implemented: `get_bathing_waters` (`/doc/bathing-water.json`), plus related entity lookups under `/id/*`.

- Asset Management
  - Base: `https://environment.data.gov.uk/asset-management`
  - Implemented: Assets, maintenance activities/tasks/plans, capital schemes (JSON endpoints under `/id/*.json`).

- Catchment Planning (Catchment Data)
  - Base: `https://environment.data.gov.uk/catchment-planning`
  - Status: Placeholder only (`get_catchment_data` returns `[]` until the correct endpoint is confirmed).

- Water Quality Data Archive (WQA)
  - Base: `https://environment.data.gov.uk/water-quality/view`
  - Status: Being replaced by DEFRA; many endpoints currently return HTTP 404. Client issues a `DeprecationWarning`. Tests are skipped until the replacement API is available.

## Testing & VCR 🧪

- Tests are recorded/replayed with `pytest-vcr` (record mode: once).
- Cassettes are stored under `tests/cassettes/` with per-module subfolders (e.g., `rainfall/`, `hydrology/`, `tide_gauge/`, `integration/`).
- To re-record a cassette, delete the corresponding YAML file and re-run the specific test.
- Integration tests also use VCR to avoid live network dependency.

## Development 🛠️

Contributing? See AGENTS.md for full repository guidelines (structure, style, testing, and PR conventions).

This project uses `uv` for dependency management.

- Install dependencies: `uv sync` or `just install`
- Run tests: `just test`
- Run integration tests: `just test-integration`
- Lint (fix): `just lint`
- Format: `just format`
- Example script: `just run-main`

## Contributing 🤝

- Start with AGENTS.md for repository structure, coding style, testing, and PR conventions.
- Open an issue for larger changes; link issues in PRs.
- Follow commit prefixes (e.g., `feat:`, `fix:`, `docs:`) and keep messages concise.
- Run `just lint`, `just format`, and `just test` before pushing. Update or re-record VCR cassettes when tests change network interactions.

## Releasing 🚀

### Automatic Releases (Default)

**Patch versions are released automatically!** Simply merge your PR to `main`:

1. Merge PR to `main`
2. GitHub Actions automatically:
   - Bumps patch version (e.g., 0.5.11 → 0.5.12)
   - Creates git tag and GitHub release
   - Publishes to PyPI via Trusted Publishing

**No manual steps required!** The workflow uses `uv version --bump patch` automatically.

### Manual Releases (Minor/Major versions)

For **minor** or **major** version bumps, use the Justfile recipe:

```bash
just release minor          # bump minor (0.5.x → 0.6.0)
just release major "Notes"  # bump major (0.5.x → 1.0.0)
```

**Requirements:**
- `gh` CLI authenticated (`gh auth status`)
- The recipe runs `uv version --bump`, commits changes, creates tag, and publishes

**Alternatively, run manually:**

```bash
uv version --bump minor  # or major
git add pyproject.toml uv.lock
git commit -m "publish: bump to vX.Y.Z"
git push origin main
git tag vX.Y.Z && git push origin vX.Y.Z
gh release create vX.Y.Z --title "vX.Y.Z" --notes "Release notes"
```

### How It Works

- **Automatic workflow:** `.github/workflows/auto-version.yml` bumps patch on every merge to main
- **Publishing workflow:** `.github/workflows/publish.yml` publishes to PyPI when releases are created
- **No tokens needed:** Uses GitHub's Trusted Publishing for PyPI

**Links:**
- PyPI project: https://pypi.org/project/environment-client/
- Workflow docs: `.github/workflows/README.md`
