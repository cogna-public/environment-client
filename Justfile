install:
	uv sync

test:
	uv run pytest tests/test_client.py

test-integration:
	uv run pytest tests/integration_test.py

test-bathing-waters:
	uv run pytest tests/test_bathing_waters_client.py

test-asset-management:
	uv run pytest tests/test_asset_management_client.py

test-catchment-data:
	uv run pytest tests/test_catchment_data_client.py

run-main:
	uv run python main.py

pypi-smoke:
	set -euo pipefail
	cd pypi_smoke && uv run --no-project --isolated --with environment-client --with pytest --with pytest-asyncio -m pytest -q

lint:
	uv run ruff check --fix .

format:
	uv run ruff format .


# Release from main by running the Auto Version Bump workflow. Only the release
# app can push the bump commit and v* tags, so this can't run locally.
# Usage examples:
#   just release                 # bump patch
#   just release minor           # bump minor
#   just release major "Notes"   # bump major with notes
release bump="patch" notes="":
	gh workflow run auto-version.yml --repo cogna-public/environment-client --ref main -f bump={{bump}} -f notes="{{notes}}"
