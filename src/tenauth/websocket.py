from fastapi import HTTPException
from starlette import status
from starlette.websockets import WebSocket, WebSocketDisconnect

from tenauth.schemas import AccessContext, AuthContext


async def websocket_access_context(websocket: WebSocket) -> AccessContext:
    token: str | None = None
    authorization = websocket.headers.get("Authorization")

    if authorization:
        scheme, _, credentials = authorization.partition(" ")
        if scheme.lower() != "bearer" or not credentials:
            raise WebSocketDisconnect(code=status.WS_1008_POLICY_VIOLATION)
        token = credentials.strip()
    else:
        query_token = websocket.query_params.get(
            "access_token"
        ) or websocket.query_params.get("token")
        if query_token:
            token = query_token.strip()
        else:
            protocols = websocket.headers.get("Sec-WebSocket-Protocol", "")
            for candidate in protocols.split(","):
                candidate = candidate.strip()
                if candidate.startswith("access_token="):
                    token = candidate.split("=", 1)[1].strip()
                    break

    if not token:
        raise WebSocketDisconnect(code=status.WS_1008_POLICY_VIOLATION)

    if token.lower().startswith("bearer "):
        token = token.split(" ", 1)[1].strip()

    try:
        auth_context = AuthContext.from_token(token)
    except HTTPException as exc:
        raise WebSocketDisconnect(code=status.WS_1008_POLICY_VIOLATION) from exc

    return AccessContext(tenant_id=auth_context.tid, user_id=auth_context.sub)
