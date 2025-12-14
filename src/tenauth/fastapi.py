import warnings
from collections.abc import AsyncIterator, Callable

from fastapi import Depends, Security
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlmodel.ext.asyncio.session import AsyncSession
from starlette import status

from .schemas import AccessContext, AuthContext
from .session import SessionFactory, access_scoped_session_ctx
from fastapi import HTTPException

AUTHORIZATION_KEY = 'authorization'
BEARER_SCHEME = HTTPBearer(auto_error=False)


async def get_bearer_token(credentials: HTTPAuthorizationCredentials | None = Security(BEARER_SCHEME)) -> str:
    if credentials is None or not credentials.credentials:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Missing Authorization header")
    scheme = (credentials.scheme or "").lower()
    token = credentials.credentials
    if scheme != "bearer" or not token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid authorization scheme")
    return token


async def get_auth_context(
    credentials: HTTPAuthorizationCredentials | None = Security(BEARER_SCHEME),
) -> AuthContext:
    """Require Authorization header and return an AuthContext, else raise 401."""
    token = await get_bearer_token(credentials)
    return AuthContext.from_token(token)


async def get_access_context(
    auth: AuthContext = Depends(get_auth_context),
) -> AccessContext:
    """Resolve tenant/user context from an AuthContext."""
    return AccessContext(tenant_id=auth.tid, user_id=auth.sub)


async def require_auth(
    credentials: HTTPAuthorizationCredentials | None = Security(BEARER_SCHEME),
)-> AuthContext:
    warnings.warn(
        "require_auth is deprecated; use get_auth_context instead",
        DeprecationWarning,
        stacklevel=2,
    )

    return await get_auth_context(credentials)


async def require_access_context(
    auth: AuthContext = Depends(get_access_context),
) -> AccessContext:
    """Resolve tenant/user context from an AuthContext."""
    warnings.warn(
        "require_access_context is deprecated; use get_auth_context instead",
        DeprecationWarning,
        stacklevel=2,
    )
    return await get_access_context(auth)


def build_access_scoped_session_dependency(
    session_factory: SessionFactory,
    *,
    verify: bool = True,
) -> Callable[..., AsyncIterator[AsyncSession]]:
    """Create a FastAPI dependency that yields a scoped session."""

    async def dependency(
        tenant: AccessContext = Depends(get_access_context),
    ) -> AsyncIterator[AsyncSession]:
        async with access_scoped_session_ctx(
            session_factory=session_factory,
            access_context=tenant,
            verify=verify,
        ) as session:
            yield session

    return dependency
