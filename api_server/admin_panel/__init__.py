from fastapi import APIRouter, Query
from starlette.requests import Request

from . import personas, rules, tasks, users, invite_codes, settings
from .auth import check_authentication
from ..templates import templates

router = APIRouter()

router.include_router(personas.router, prefix="/personas", tags=["personas"])
router.include_router(rules.router, prefix="/rules", tags=["rules"])
router.include_router(tasks.router, prefix="/tasks", tags=["tasks"])
router.include_router(invite_codes.router, prefix="/invite_codes", tags=["invite_codes"])
router.include_router(users.router, prefix="/users", tags=["users"])
router.include_router(settings.router, prefix="/settings", tags=["settings"])


@router.get("/")
async def read_root(request: Request, token: str = Query(...)):
    await check_authentication(token)
    return templates.TemplateResponse("admin_panel.html", {"request": request})
