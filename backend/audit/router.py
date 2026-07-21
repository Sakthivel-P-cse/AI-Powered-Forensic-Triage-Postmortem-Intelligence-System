from dataclasses import asdict
from fastapi import APIRouter, Depends

from auth.rbac import CurrentUser, Role, require_roles
from .logger import recent

router = APIRouter()


@router.get("/recent")
async def get_recent(
    n: int = 100,
    _: CurrentUser = Depends(require_roles(Role.ADMIN)),
):
    return [asdict(r) for r in recent(n)]
