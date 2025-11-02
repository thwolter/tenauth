import base64
import json

from tenauth.schemas import AuthContext


def create_bearer_token(ctx: AuthContext) -> str:
    """Return a JWT-like Bearer token (no signature) from an AuthContext."""
    header = {"alg": "none"}
    payload = {
        "sub": str(ctx.sub),
        "tid": str(ctx.tid),
        "role": ctx.role,
        "scopes": ctx.scopes,
        "plan": ctx.plan,
        "iat": ctx.iat,
        "exp": ctx.exp,
        "iss": ctx.iss,
        "aud": ctx.aud,
    }
    # remove None values
    payload = {k: v for k, v in payload.items() if v is not None}

    def b64(data: dict) -> str:
        raw = json.dumps(data, separators=(",", ":")).encode()
        return base64.urlsafe_b64encode(raw).decode().rstrip("=")

    token = f"{b64(header)}.{b64(payload)}."
    return f"Bearer {token}"
