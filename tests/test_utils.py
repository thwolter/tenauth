from __future__ import annotations

import base64
import json
from uuid import UUID

from tenauth.schemas import AuthContext
from tenauth.utils import create_bearer_token


def _decode_segment(segment: str) -> dict:
    padded = segment + "=" * (-len(segment) % 4)
    return json.loads(base64.urlsafe_b64decode(padded).decode("utf-8"))


def test_create_bearer_token_encodes_auth_context():
    ctx = AuthContext(
        sub=UUID("aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa"),
        tid=UUID("bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbbb"),
        role="editor",
        scopes=["datasets:read", "datasets:write"],
        plan="pro",
        iat=1700000000,
        exp=1700003600,
        iss="tenauth-tests",
        aud=["svc-api"],
    )

    token = create_bearer_token(ctx)
    assert token.startswith("Bearer ")

    encoded = token.split(" ", 1)[1]
    header_segment, payload_segment, _signature = encoded.split(".")

    assert _decode_segment(header_segment) == {"alg": "none"}

    payload = _decode_segment(payload_segment)
    assert payload["sub"] == str(ctx.sub)
    assert payload["tid"] == str(ctx.tid)
    assert payload["role"] == ctx.role
    assert payload["scopes"] == ctx.scopes
    assert payload["plan"] == ctx.plan
    assert payload["iat"] == ctx.iat
    assert payload["exp"] == ctx.exp
    assert payload["iss"] == ctx.iss
    assert payload["aud"] == ctx.aud


def test_create_bearer_token_omits_empty_fields():
    ctx = AuthContext(
        sub=UUID("aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa"),
        tid=UUID("bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbbb"),
        role=None,
        scopes=None,
        plan=None,
    )

    encoded = create_bearer_token(ctx).split(" ", 1)[1]
    payload_segment = encoded.split(".")[1]
    payload = _decode_segment(payload_segment)

    assert "role" not in payload
    assert "scopes" not in payload
    assert "plan" not in payload
