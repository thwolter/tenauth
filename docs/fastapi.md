# FastAPI Integration

FastAPI dependencies in Tenauth minimise boilerplate for enforcing bearer authentication and tenant scoping.

## Requiring Authentication
```python
from fastapi import Depends, FastAPI
from tenauth.fastapi import require_auth
from tenauth.models import AuthContext

app = FastAPI()

@app.get("/me")
def read_profile(auth: AuthContext = Depends(require_auth)):
    return {"user_id": str(auth.sub), "tenant_id": str(auth.tid)}
```
`require_auth` extracts the bearer token, validates the scheme, and returns an `AuthContext`. Invalid or missing tokens raise `HTTPException(status_code=401)` automatically.

## Tenant-Aware Sessions
```python
from sqlmodel.ext.asyncio.session import AsyncSession
from tenauth.fastapi import build_access_scoped_session_dependency

SessionDep = build_access_scoped_session_dependency(session_factory=my_session_factory)

@app.get("/tenants/{tenant_id}/widgets")
async def list_widgets(session: AsyncSession = Depends(SessionDep)):
    result = await session.execute(...)
    return result.all()
```
`build_access_scoped_session_dependency` combines the auth context with the session factory. It applies tenant and user identifiers via Postgres GUCs for the lifecycle of the request and resets them when complete.

## Customising Verification
When creating the dependency you can disable runtime GUC verification:
```python
SessionDep = build_access_scoped_session_dependency(
    session_factory=my_session_factory,
    verify=False,
)
```
Skipping verification removes the extra roundtrip to confirm the settings—but only use it when you trust the database connection pool configuration.

## WebSocket Authentication
`websocket_access_context` mirrors the HTTP dependency flow for websocket handshakes. It inspects the Authorization header, `access_token` query parameter, or `Sec-WebSocket-Protocol` entries—accepting either raw tokens or `Bearer`-prefixed strings.
```python
from fastapi import FastAPI
from starlette.websockets import WebSocket

from tenauth.websocket import websocket_access_context

app = FastAPI()

@app.websocket("/ws")
async def ws_channel(websocket: WebSocket):
    access_ctx = await websocket_access_context(websocket)
    await websocket.accept()
    await websocket.send_json({
        "tenant": str(access_ctx.tenant_id),
        "user": str(access_ctx.user_id),
    })
```
Tokens rejected by `AuthContext.from_token` become `WebSocketException` errors with the same policy-violation code FastAPI uses for missing or malformed authentication.
