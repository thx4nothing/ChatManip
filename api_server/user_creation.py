"""
Module: user_router

This module defines an API router for user-related actions using the FastAPI framework.
It includes routes for creating users and handling user sessions.

Functions:
    read_root: Serves the index.html template on the root URL ("/").
    create_user: Handles user creation, checks invite codes, and sets up user sessions.

Usage:
    The router is integrated with the FastAPI application to
    handle user-related actions through API endpoints.

Author: Marlon Beck
Date: 17/08/2023
"""
import json

from fastapi import APIRouter, Request, HTTPException
from sqlmodel import Session, select
from starlette.responses import RedirectResponse

from api_server.database import engine, User, ChatSession, InviteCode
from api_server.models import UserInformation
from api_server.templates import templates

router = APIRouter()


@router.get("/")
async def read_root_language(request: Request):
    return await read_root_language(request, "en")


@router.get("/{language}")
async def read_root_language(request: Request, language: str):
    """
    Serves the index.html template on the root URL ("/").

    Args:
        request (Request): The incoming request.

    Returns:
        TemplateResponse: The template response containing the "user_creation.html" template.
    """
    if language == "de":
        with open("static/translations/user_creation_de.json", "r",
                  encoding="utf-8") as translation_file:
            translation_data = json.load(translation_file)
    else:
        with open("static/translations/user_creation_en.json", "r",
                  encoding="utf-8") as translation_file:
            translation_data = json.load(translation_file)
    return templates.TemplateResponse("user_creation.html",
                                      {"request": request, "translations": translation_data})


@router.post("/create_user")
async def create_user(user: UserInformation):
    """
    Handles user creation, checks invite codes, sets up user sessions.

    Args:
        user (UserInformation): User information received in the POST request.

    Returns:
        RedirectResponse: Redirects the user to the chat session page or back to the root URL.
    """
    with Session(engine) as db_session:
        statement = select(InviteCode).where(InviteCode.invite_code == user.invite_code)
        invite_code_obj = db_session.exec(statement).first()
        if not invite_code_obj:
            raise HTTPException(status_code=404, detail="Invite code not found")
        if invite_code_obj.used:
            raise HTTPException(status_code=404, detail="Invite already in use")

        new_user = User(age=user.age, gender=user.gender, occupation=user.occupation,
                        location=user.location, language=user.language)
        db_session.add(new_user)
        db_session.commit()
        db_session.refresh(new_user)

        current_user = new_user
        new_invite_code_str = user.invite_code
        new_session = ChatSession(session_id=new_invite_code_str, user_id=current_user.user_id,
                                  persona_id=invite_code_obj.persona_id,
                                  task_id=invite_code_obj.task_id,
                                  rules=invite_code_obj.rules,
                                  history_id=invite_code_obj.history_id)
        db_session.add(new_session)
        db_session.commit()

        invite_code_obj.used = True
        invite_code_obj.user_id = current_user.user_id
        db_session.add(invite_code_obj)
        db_session.commit()

        statement = select(ChatSession).where(ChatSession.user_id == current_user.user_id)
        current_session = db_session.exec(statement).first()
        session_id = str(current_session.session_id)
        redirect_url = f"/chat/{session_id}"
        print(redirect_url)
        return RedirectResponse(url=redirect_url, status_code=303)

    return RedirectResponse(url="/")
