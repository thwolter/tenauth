# Session Management

The session utilities ensure every database query runs within the correct tenant and user scope by applying Postgres Grand Unified Configurations (GUCs).

## Applying Access Context
`apply_access_context(session, access_context)` sets `app.tenant_id` and `app.user_id` on the active connection and stores the UUIDs in `session.info`.

```python
from tenauth.models import AccessContext
from tenauth.session import apply_access_context

await apply_access_context(
    session,
    access_context=AccessContext(tenant_id=tenant, user_id=user),
)
```

## Verification
By default `apply_access_context` calls `verify_access_context`, which reads the current settings and compares them to the expected UUIDs. Failures raise `RuntimeError` to surface configuration problems immediately. Toggle verification off when you want to optimise for throughput and already have strong invariants on the pool.

## Resetting Context
`reset_access_context(session)` clears both GUCs and removes stored metadata. This is called automatically inside `access_scoped_session_ctx`, but you can invoke it manually when using sessions outside the context manager.

## Scoped Context Manager
`access_scoped_session_ctx` wraps a provided session factory and yields an `AsyncSession` with the context bound for the duration of the `async with` block. It is the basis for the FastAPI dependency but can be reused in background tasks or scripts.

```python
from tenauth.session import access_scoped_session_ctx

async with access_scoped_session_ctx(
    session_factory=my_session_factory,
    access_context=AccessContext(tenant_id=tenant, user_id=user),
) as session:
    ...
```
