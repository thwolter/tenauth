from __future__ import annotations

from uuid import UUID

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from starlette import status
from starlette.websockets import WebSocket, WebSocketDisconnect

from tenauth.schemas import AuthContext
from tenauth.utils import create_bearer_token
from tenauth.websocket import websocket_access_context


def _make_app():
    app = FastAPI()

    @app.websocket("/ws")
    async def endpoint(websocket: WebSocket):
        ctx = await websocket_access_context(websocket)
        await websocket.accept()
        await websocket.send_json(
            {"tenant_id": str(ctx.tenant_id), "user_id": str(ctx.user_id)}
        )
        await websocket.close()

    return app


def _sample_context() -> AuthContext:
    return AuthContext(
        sub=UUID("aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa"),
        tid=UUID("bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbbb"),
        role="viewer",
        scopes=["datasets:read"],
    )


def test_websocket_access_context_authorization_header():
    app = _make_app()
    ctx = _sample_context()
    token = create_bearer_token(ctx)

    with TestClient(app) as client:
        with client.websocket_connect("/ws", headers={"Authorization": token}) as ws:
            payload = ws.receive_json()

    assert payload == {
        "tenant_id": str(ctx.tid),
        "user_id": str(ctx.sub),
    }


def test_websocket_access_context_query_parameter():
    app = _make_app()
    ctx = _sample_context()
    token = create_bearer_token(ctx).split(" ", 1)[1]

    with TestClient(app) as client:
        with client.websocket_connect(f"/ws?access_token={token}") as ws:
            payload = ws.receive_json()

    assert payload == {
        "tenant_id": str(ctx.tid),
        "user_id": str(ctx.sub),
    }


def test_websocket_access_context_protocol_header():
    app = _make_app()
    ctx = _sample_context()
    token = create_bearer_token(ctx)
    protocol = f"chat, access_token={token}"

    with TestClient(app) as client:
        with client.websocket_connect(
            "/ws", headers={"Sec-WebSocket-Protocol": protocol}
        ) as ws:
            payload = ws.receive_json()

    assert payload == {
        "tenant_id": str(ctx.tid),
        "user_id": str(ctx.sub),
    }


@pytest.mark.parametrize(
    "headers,query",
    [
        ({"Authorization": "Basic something"}, ""),
        ({}, ""),
    ],
)
def test_websocket_access_context_missing_token(headers: dict, query: str):
    app = _make_app()

    with TestClient(app) as client:
        with pytest.raises(WebSocketDisconnect) as exc:
            with client.websocket_connect(f"/ws{query}", headers=headers):
                pass

    assert exc.value.code == status.WS_1008_POLICY_VIOLATION


def test_websocket_access_context_invalid_token():
    app = _make_app()
    invalid = create_bearer_token(_sample_context()).split(" ", 1)[1].replace(".", "")

    with TestClient(app) as client:
        with pytest.raises(WebSocketDisconnect) as exc:
            with client.websocket_connect(
                "/ws", headers={"Authorization": f"Bearer {invalid}"}
            ):
                pass

    assert exc.value.code == status.WS_1008_POLICY_VIOLATION
