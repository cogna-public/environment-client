PyPI Smoke Test (single-command)

Run
- `just pypi-smoke`

What it does
- Installs `environment-client` from PyPI in an isolated uv run.
- Executes `pypi_smoke/test_smoke.py` (async pytest) against live public APIs.

Notes
- Requires internet access; calls public Environment Agency endpoints.
- Uses `uv run --no-project --isolated --with ...` to avoid picking up the local repo project.
- Import path is `environment`; distribution name is `environment-client`.
