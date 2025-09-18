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


# Create a release: bump version with uv, tag, push, and create GitHub Release
# Usage examples:
#   just release                 # bump patch
#   just release minor           # bump minor
#   just release major "Notes"   # bump major with notes
release bump="patch" notes="":
	set -euo pipefail
	# Bump version using uv
	uv version --bump {{bump}}
	# Extract new version from pyproject.toml
	new_version=$(rg '^version\s*=\s*"([^"]+)"' -or '$1' pyproject.toml | head -n1)
	# Commit and push
	git add pyproject.toml uv.lock
	git commit -m "publish: bump to v${new_version}" || echo "No changes to commit"
	git push origin main
	# Tag and push
	git tag "v${new_version}" || echo "Tag already exists"
	git push origin "v${new_version}" || echo "Tag push failed (may already exist)"
	# Prepare notes
	if [ -z "{{notes}}" ]; then rel_notes="Release v${new_version}"; else rel_notes="{{notes}}"; fi
	# Create GitHub Release
	gh release create "v${new_version}" --title "v${new_version}" --notes "${rel_notes}" --repo cogna-public/environment-client || echo "Release may already exist"
