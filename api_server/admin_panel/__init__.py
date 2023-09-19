import json

from fastapi import APIRouter, Query
from starlette.requests import Request
from starlette.responses import RedirectResponse

from . import personas, rules, tasks, users, invite_codes, settings, history
from .auth import check_authentication
from ..templates import templates

router = APIRouter()

router.include_router(personas.router, prefix="/personas", tags=["personas"])
router.include_router(rules.router, prefix="/rules", tags=["rules"])
router.include_router(tasks.router, prefix="/tasks", tags=["tasks"])
router.include_router(history.router, prefix="/history", tags=["history"])
router.include_router(invite_codes.router, prefix="/invite_codes", tags=["invite_codes"])
router.include_router(users.router, prefix="/users", tags=["users"])
router.include_router(settings.router, prefix="/settings", tags=["settings"])


@router.get("")
async def read_root(request: Request, token: str = Query(...)):
    redirect_url = f"/admin/en?token={token}"
    return RedirectResponse(url=redirect_url, status_code=303)


@router.get("/{language}")
async def read_root_en(request: Request, language: str, token: str = Query(...)):
    await check_authentication(token)
    if language == "de":
        with open("static/translations/admin_panel_de.json", "r",
                  encoding="utf-8") as translation_file:
            translation_data = json.load(translation_file)
    else:
        with open("static/translations/admin_panel_en.json", "r",
                  encoding="utf-8") as translation_file:
            translation_data = json.load(translation_file)
    return templates.TemplateResponse("admin_panel.html",
                                      {"request": request, "translations": translation_data})


@router.get("/translations/{language}")
async def get_translations(language: str):
    if language == "de":
        with open("static/translations/admin_panel_de.json", "r",
                  encoding="utf-8") as translation_file:
            translation_data = json.load(translation_file)
    else:
        with open("static/translations/admin_panel_en.json", "r",
                  encoding="utf-8") as translation_file:
            translation_data = json.load(translation_file)
    return translation_data
