# Tenauth Overview

Tenauth provides a focused toolkit for building multi-tenant FastAPI services backed by SQLModel. The package handles JWT decoding, access-context management, and tenant-aware database sessions so your endpoints stay thin and declarative.

## Key Capabilities
- **Bearer Auth Parsing** – `tenauth.models.AuthContext` converts Authorization headers into typed payloads with minimal boilerplate.
- **Tenant-Scoped Sessions** – `tenauth.session.access_scoped_session_ctx` applies Postgres GUCs to each connection, keeping tenant and user scope consistent.
- **FastAPI Dependencies** – `tenauth.fastapi.require_auth` and `build_access_scoped_session_dependency` wire the auth and session layers into your routers.
- **DSN Augmentation** – `tenauth.tenancy.dsn_with_tenant` injects tenant identifiers into connection strings for background jobs or migrations.
- **WebSocket Handshakes** – `tenauth.websocket.websocket_access_context` extracts tenant/user identifiers from websocket headers, query parameters, or negotiated protocols.
- **Testing Utilities** – `tenauth.utils.create_bearer_token` assembles unsigned bearer tokens ready for HTTP or websocket test clients.

## Installation
```bash
uv pip sync
```

If `uv` is not available, create a virtual environment and install the project in editable mode:
```bash
python -m venv .venv
source .venv/bin/activate
pip install -e .[dev]
```

## Project Layout
- `src/tenauth/` – core library modules (FastAPI dependency helpers, session utilities, models, tenancy helpers).
- `tests/` – pytest suite covering JWT parsing and dependency behavior.
- `pyproject.toml` / `uv.lock` – packaging metadata and pinned dependency set.

Continue through the remaining sections for detailed guidance on integrating the components into your service.
