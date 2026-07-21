from datetime import datetime
from typing import Literal

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel

from audit import audit
from auth.rbac import CurrentUser, Role, require_roles

from .users_repo import create, list_all, set_disabled

router = APIRouter()


class UserCreate(BaseModel):
    email: str
    password: str
    role: Literal["INVESTIGATOR", "ANALYST", "ADMIN"]
    name: str


class UserOut(BaseModel):
    id: str
    email: str
    role: Role
    name: str
    disabled: bool
    created_at: datetime


@router.get("/users", response_model=list[UserOut])
async def list_users(_: CurrentUser = Depends(require_roles(Role.ADMIN))) -> list[UserOut]:
    return [UserOut(**u) for u in list_all()]


@router.post("/users", response_model=UserOut, status_code=status.HTTP_201_CREATED)
async def create_user(
    body: UserCreate,
    user: CurrentUser = Depends(require_roles(Role.ADMIN)),
) -> UserOut:
    try:
        row = create(body.email, body.password, Role(body.role), body.name)
    except ValueError as e:
        raise HTTPException(status.HTTP_409_CONFLICT, str(e)) from e
    audit(user_id=user.sub, action="admin.user.create", entity_type="user",
          entity_id=row["email"], metadata={"role": body.role})
    return UserOut(**row)


@router.post("/users/{email}/disable", response_model=UserOut)
async def disable_user(
    email: str, user: CurrentUser = Depends(require_roles(Role.ADMIN)),
) -> UserOut:
    row = set_disabled(email, True)
    if not row:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "user not found")
    audit(user_id=user.sub, action="admin.user.disable", entity_type="user", entity_id=email)
    return UserOut(**row)


@router.post("/users/{email}/enable", response_model=UserOut)
async def enable_user(
    email: str, user: CurrentUser = Depends(require_roles(Role.ADMIN)),
) -> UserOut:
    row = set_disabled(email, False)
    if not row:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "user not found")
    audit(user_id=user.sub, action="admin.user.enable", entity_type="user", entity_id=email)
    return UserOut(**row)
