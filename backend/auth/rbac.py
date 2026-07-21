from enum import Enum
from typing import Iterable

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer

from auth.jwt_handler import decode_token


class Role(str, Enum):
    INVESTIGATOR = "INVESTIGATOR"
    ANALYST = "ANALYST"
    ADMIN = "ADMIN"


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login", auto_error=False)


class CurrentUser:
    def __init__(self, sub: str, role: Role):
        self.sub = sub
        self.role = role


def get_current_user(token: str | None = Depends(oauth2_scheme)) -> CurrentUser:
    if not token:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "authentication required")
    try:
        payload = decode_token(token)
        return CurrentUser(sub=payload["sub"], role=Role(payload["role"]))
    except Exception as e:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, str(e)) from e


def require_roles(*allowed: Role):
    def _dep(user: CurrentUser = Depends(get_current_user)) -> CurrentUser:
        if user.role not in allowed:
            raise HTTPException(
                status.HTTP_403_FORBIDDEN,
                f"role {user.role.value} not permitted; need one of {[r.value for r in allowed]}",
            )
        return user

    return _dep


def any_role(roles: Iterable[Role]):
    return require_roles(*roles)
