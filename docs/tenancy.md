# Tenancy Utilities

`tenauth.tenancy` contains helpers that keep tenant identifiers attached to database connections and downstream tooling.

## dsn_with_tenant
This function injects the tenant UUID into the DSN query portion, extending existing connection options when present.

```python
from tenauth.tenancy import dsn_with_tenant

tenant_dsn = dsn_with_tenant(
    "postgresql+psycopg://svc@db.example.com/app?sslmode=require",
    tenant_id=tenant_uuid,
)
```

Internally it uses `urllib.parse` to preserve other connection parameters. If `options` already contain tenant-related flags they are augmented in-place to avoid duplicates.

## Usage Scenarios
- **Background Workers** – Derive per-tenant DSNs when enqueueing tasks or spinning up dedicated workers.
- **Migrations** – Generate tenant-specific connection strings for migration scripts that rely on `psql` command-line arguments.
- **Diagnostics** – Craft diagnostic queries tied to a tenant without mutating your primary configuration files.

Pair the helper with session utilities to ensure the tenant context is represented consistently across service layers.
