from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import BaseModel

from auth.jwt_handler import create_access_token, verify_password
from auth.rbac import CurrentUser, Role, get_current_user

router = APIRouter()


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    role: Role
    name: str


class MeResponse(BaseModel):
    email: str
    role: Role


@router.post("/login", response_model=TokenResponse)
async def login(form: OAuth2PasswordRequestForm = Depends()) -> TokenResponse:
    # Local import: users_repo seeds on first call and re-importing at module
    # load would create a circular dependency with auth.jwt_handler.
    from modules.admin.users_repo import get

    user = get(form.username)
    if not user or user.get("disabled") or not verify_password(form.password, user["password_hash"]):
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "invalid credentials")
    token = create_access_token(form.username.lower(), user["role"].value)
    return TokenResponse(access_token=token, role=user["role"], name=user["name"])


@router.get("/me", response_model=MeResponse)
async def me(user: CurrentUser = Depends(get_current_user)) -> MeResponse:
    return MeResponse(email=user.sub, role=user.role)
