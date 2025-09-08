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

lint:
	uv run ruff check --fix .

format:
	uv run ruff format .

