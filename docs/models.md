# Models & Auth

Models in Tenauth are Pydantic-based wrappers around the auth and access concepts used throughout the project.

## AuthContext
`AuthContext` represents the decoded JWT payload. The `from_token` classmethod:
- Splits the token into header/payload/signature.
- Base64-decodes the payload, enriching the data with strongly typed UUIDs.
- Normalises scopes into a list of strings.
- Converts `plan` or `entitlements` fields into a single attribute.

On failure it logs a warning via the standard library logger and raises `HTTPException(status_code=401)`. Catch the exception in higher layers when you need custom responses.

### Example
```python
from tenauth.models import AuthContext

auth = AuthContext.from_token(encoded_jwt)
print(auth.sub, auth.tid, auth.scopes)
```

## AccessContext
`AccessContext` is a minimal tenant/user pair used by the session helpers.

```python
from tenauth.models import AccessContext

ctx = AccessContext.from_session(session)
```
The `from_session` helper fetches the UUIDs stored in `session.info` and raises `ValueError` when metadata is missing—useful when integrating with third-party session factories or middleware.

## Error Handling Patterns
- Raise `HTTPException` for invalid client requests (missing tokens, malformed payloads).
- Use `RuntimeError` or `ValueError` when asserting internal invariants such as mismatched tenant IDs between a session and request context.
- Configure logging with `logging.basicConfig(level="INFO")` or your preferred setup to surface parsing failures detected by `AuthContext`.
