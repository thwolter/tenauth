# Development Guide

## Environment Setup
- Install dependencies with `uv pip sync`. This ensures versions locked in `uv.lock` are applied.
- If `uv` is unavailable, create a virtual environment and run `pip install -e .[dev]`.
- Target Python 3.12 to align with the `pyproject.toml` specification.

## Running Tests
- Execute the full suite with `uv run pytest`.
- Use markers or keyword selection for focused runs, e.g. `uv run pytest -k auth`.
- Add async tests with `pytest.mark.asyncio` when asserting session or FastAPI behaviours.

## Coding Standards
- Follow four-space indentation and `snake_case` for functions/variables; models stay in `PascalCase`.
- Keep modules cohesive: FastAPI dependencies in `fastapi.py`, session utilities in `session.py`, models in `models.py`.
- Prefer raising `HTTPException` for user-facing errors and domain-specific exceptions (`ValueError`, `RuntimeError`) for invariants.
- Configure logging with the stdlib `logging` module; the package initialises `logger = logging.getLogger(__name__)` where needed.

## Contributing
- Review `AGENTS.md` for repository guidelines on commit messages, PR requirements, and expected test evidence.
- Scope commits to a single logical change and keep messages in the imperative mood.
- Document behaviour changes and new configuration steps within the relevant Markdown pages before requesting review.
