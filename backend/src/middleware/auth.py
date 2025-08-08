from datetime import datetime, timedelta
from typing import Callable, Optional, Union

from fastapi import HTTPException, Request, status
from fastapi.responses import JSONResponse
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError

from backend.src.auth.jwt import verify_token
from backend.src.database import SessionLocal
from backend.src.models import Permission, User


class JWTBearer(HTTPBearer):
    def __init__(self, auto_error: bool = True):
        super().__init__(auto_error=auto_error)

    async def __call__(
        self, request: Request
    ) -> Optional[HTTPAuthorizationCredentials]:
        credentials: Optional[HTTPAuthorizationCredentials] = await super().__call__(
            request
        )
        if not credentials:
            if self.auto_error:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Invalid authorization code",
                )
            return None

        if credentials.scheme != "Bearer":
            if self.auto_error:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Invalid authentication scheme",
                )
            return None

        try:
            token_data = verify_token(credentials.credentials)
            request.state.user_id = token_data.user_id
            return credentials
        except JWTError as e:
            if self.auto_error:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Invalid or expired token",
                ) from e
            return None


async def check_permissions(
    request: Request, resource_type: str, resource_id: str, required_permission: str
) -> bool:
    db = SessionLocal()
    try:
        user_id = request.state.user_id
        permission = (
            db.query(Permission)
            .filter(
                Permission.user_id == user_id,
                Permission.resource_type == resource_type,
                Permission.resource_id == resource_id,
            )
            .first()
        )

        if not permission:
            return False

        return getattr(permission, f"can_{required_permission}", False)
    finally:
        db.close()


def add_security_headers(request: Request, call_next: Callable):
    response = call_next(request)
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    response.headers[
        "Strict-Transport-Security"
    ] = "max-age=31536000; includeSubDomains"
    return response
