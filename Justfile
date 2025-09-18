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
	uv version --bump {{bump}} && \
	new_version=$(yq eval '.project.version' pyproject.toml) && \
	echo "New version: ${new_version}" && \
	git add pyproject.toml uv.lock && \
	git commit -m "publish: bump to v${new_version}" || echo "No changes to commit" && \
	git push origin main && \
	git tag "v${new_version}" || echo "Tag already exists" && \
	git push origin "v${new_version}" || echo "Tag push failed (may already exist)" && \
	if [ -z "{{notes}}" ]; then rel_notes="Release v${new_version}"; else rel_notes="{{notes}}"; fi && \
	gh release create "v${new_version}" --title "v${new_version}" --notes "${rel_notes}" --repo cogna-public/environment-client || echo "Release may already exist"
