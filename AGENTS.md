# Repository Guidelines

## Project Structure & Module Organization
- `src/tenauth/fastapi.py` publishes FastAPI dependencies (`require_auth`, `build_access_scoped_session_dependency`) for wiring auth and database access into routes.
- `src/tenauth/session.py` owns tenant-aware session management, including helpers to apply and reset Postgres GUCs.
- `src/tenauth/models.py` contains the Pydantic models (`AuthContext`, `AccessContext`) shared across the API surface.
- `src/tenauth/tenancy.py` offers DSN utilities for injecting tenant metadata into connection strings.
- Tests live in `tests/`, mirroring module names (for example `tests/test_auth_jwt.py`), and packaging metadata lives in `pyproject.toml`.

## Build, Test, and Development Commands
- Install and sync dependencies pinned in `uv.lock`:
  ```shell
  uv pip sync
  ```
- Run the test suite (includes FastAPI client checks and async cases):
  ```shell
  uv run pytest
  ```
- Launch ad-hoc scripts with project dependencies:
  ```shell
  uv run python -m tenauth.fastapi
  ```
- If `uv` is unavailable, fall back to `python -m venv .venv && source .venv/bin/activate` followed by `pip install -e .[dev]`.

## Coding Style & Naming Conventions
- Target Python 3.12, four-space indentation, and `from __future__ import annotations` for future-proof typing.
- Keep modules focused and functions pure where possible; surface FastAPI dependencies through injectable callables.
- Use `snake_case` for functions/variables, `PascalCase` for Pydantic models, and persist UUIDs as `UUID` objects (avoid stringly-typed helpers).
- Prefer raising `HTTPException` for client-facing errors and `RuntimeError` for internal assertion failures; reuse `logger` for diagnostic logging.

## Testing Guidelines
- Write tests beside peers in `tests/` using the `test_*.py` pattern and `pytest` style asserts.
- Mark async tests with `pytest.mark.asyncio`; leverage the provided signed JWT fixture when exercising auth flows.
- Validate coverage of both positive and failure paths (e.g., missing headers, malformed JWTs, tenant mismatches).
- Run `uv run pytest -k name` to focus on a module while iterating.

## Commit & Pull Request Guidelines
- Craft commits that scope to one logical change; start messages with a concise imperative verb (`add`, `refactor`, `fix`) and keep the subject ≤72 characters.
- Reference relevant modules in the body when touching session/auth code, and note migrations or contract changes explicitly.
- Pull requests should include: purpose summary, test evidence (`uv run pytest` output or reasoning when skipped), and links to related issues or design notes.
- Attach screenshots or request logs only when they materially aid reviewers (for example, proving a FastAPI route contract).
