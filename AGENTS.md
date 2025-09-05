# Repository Guidelines

## Project Structure & Module Organization
- Source: `environment/` with per-API modules (e.g., `flood_monitoring/`, `hydrology/`) following `client.py` + `models.py` + `__init__.py`.
- Tests: `tests/` with unit/integration tests and VCR cassettes under `tests/cassettes/<module>/`.
- Entrypoint example: `main.py` demonstrates basic client usage.
- Tooling: `pyproject.toml` (hatch build, pytest), `Justfile` (common tasks), `uv.lock`.

## Build, Test, and Development Commands
- Install deps: `uv sync` or `just install`
- Run all fast tests: `just test`
- Run integration tests: `just test-integration`
- Lint (fix): `just lint`
- Format: `just format`
- Example script: `just run-main`
- Build/Publish: `just publish` (uses `uv build`/`uv publish`)

## Coding Style & Naming Conventions
- Python 3.13, 4‑space indents, type hints required in public APIs.
- Pydantic v2 models with field aliases mirroring API (`@id`, `riverOrSea`, etc.).
- Module layout: `environment/<domain>/{client.py,models.py,__init__.py}`.
- Names: snake_case for functions/vars, PascalCase for models, UPPER_CASE for constants.
- Lint/format with Ruff: `just lint` and `just format` before pushing.

## Testing Guidelines
- Framework: `pytest` with `pytest-asyncio`, `pytest-vcr`, `pytest-httpx`.
- Naming: files `tests/test_<domain>_client.py`; async tests use `@pytest.mark.asyncio`.
- VCR: cassettes in `tests/cassettes/<module>/`; to re-record, delete the YAML and rerun the specific test.
- Skips: WQA tests are `@pytest.mark.skip` until the replacement API is live.
- Run: `just test` for unit; `just test-integration` for end‑to‑end flood monitoring.

## Commit & Pull Request Guidelines
- Commit style: conventional prefixes (`feat:`, `fix:`, `docs:`, `tests:`, `publish:`, `revert:`). Keep subjects imperative and concise.
- PRs must include: clear description, linked issue (if any), scope of changes, test coverage updates, and notes on VCR cassette changes.
- Add/adjust tests for new endpoints or models. Update README/AGENTS when behavior or tooling changes.

## Security & Configuration Tips
- No API keys required; clients call public endpoints. Avoid hitting live APIs in CI—use VCR.
- Respect rate limits when re‑recording cassettes. Do not commit secrets; rely on `uv` for publishing credentials.
