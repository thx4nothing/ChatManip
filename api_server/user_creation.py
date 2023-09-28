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

from api_server.admin_panel.invite_codes import generate_invite_code
from api_server.database import engine, User, ChatSession, InviteCode
from api_server.logger import logger as logger
from api_server.models import UserInformation
from api_server.templates import templates

router = APIRouter()


@router.get("/")
async def read_root(request: Request):
    return await read_root_language(request, "en")


@router.get("/{language}")
async def read_root_language(request: Request, language: str):
    """
    Serves the index.html template on the root URL ("/").

    Args:
        request (Request): The incoming request.
        language (str): The chosen language.

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

        invite_code_obj = handle_multi_use(db_session, invite_code_obj)
        user.invite_code = invite_code_obj.invite_code

        new_user = create_new_user(db_session, age=user.age, gender=user.gender,
                                   occupation=user.occupation,
                                   location=user.location, language=user.language)

        new_session = create_new_session(db_session, user.invite_code, new_user.user_id,
                                         invite_code_obj.persona_id, invite_code_obj.task_id,
                                         invite_code_obj.rules, invite_code_obj.history_id)

        invite_code_obj.used = True
        invite_code_obj.user_id = new_user.user_id
        db_session.add(invite_code_obj)
        db_session.commit()

        redirect_url = f"/chat/{user.invite_code}"
        logger.debug("Redirecting new user %s to: %s", new_user.user_id, redirect_url)
        return RedirectResponse(url=redirect_url, status_code=303)

    return RedirectResponse(url="/")


def create_new_user(db_session, age, gender, occupation, location, language) -> User:
    new_user = User(age=age, gender=gender, occupation=occupation,
                    location=location, language=language)
    db_session.add(new_user)
    db_session.commit()
    db_session.refresh(new_user)
    logger.info("Created a new user: %s", new_user.__dict__)
    return new_user


def create_new_session(db_session, invite_code: str, user_id: int, persona_id: int, task_id: int,
                       rules, history_id: int) -> ChatSession:
    new_session = ChatSession(session_id=invite_code,
                              user_id=user_id,
                              persona_id=persona_id,
                              task_id=task_id,
                              rules=rules,
                              history_id=history_id)
    db_session.add(new_session)
    db_session.commit()
    db_session.refresh(new_session)
    logger.info("Created a new session: %s", new_session.__dict__)
    return new_session


def handle_multi_use(db_session, invite_code_obj):
    if invite_code_obj.multi_use:
        new_invite_code_str = generate_invite_code()
        new_invite_code = InviteCode(invite_code=new_invite_code_str,
                                     persona_id=invite_code_obj.persona_id,
                                     task_id=invite_code_obj.task_id,
                                     rules=invite_code_obj.rules,
                                     history_id=invite_code_obj.history_id,
                                     next_session_id=invite_code_obj.next_session_id)
        db_session.add(new_invite_code)
        db_session.commit()
        db_session.refresh(new_invite_code)
        invite_code_obj = new_invite_code
    return invite_code_obj


@router.get("/{session_id}/next")
async def next_session(session_id: str):
    with Session(engine) as db_session:
        statement = select(ChatSession).where(ChatSession.session_id == session_id)
        current_session = db_session.exec(statement).first()
        if current_session is not None:
            statement = select(InviteCode).where(InviteCode.invite_code == session_id)
            invite_code_obj = db_session.exec(statement).first()
            next_session_id = invite_code_obj.next_session_id
            if next_session_id != "none":
                statement = select(InviteCode).where(InviteCode.invite_code == next_session_id)
                next_invite_code_obj = db_session.exec(statement).first()
                next_invite_code_obj = handle_multi_use(db_session, next_invite_code_obj)
                next_session_id = next_invite_code_obj.invite_code
                statement = select(ChatSession).where(ChatSession.session_id == next_session_id)
                next_session_obj = db_session.exec(statement).first()
                if next_session_obj is None:
                    statement = select(User).where(User.user_id == current_session.user_id)
                    current_user = db_session.exec(statement).first()
                    current_user.available_tokens = 8000
                    new_session = ChatSession(session_id=next_session_id,
                                              user_id=current_user.user_id,
                                              persona_id=next_invite_code_obj.persona_id,
                                              task_id=next_invite_code_obj.task_id,
                                              rules=next_invite_code_obj.rules,
                                              history_id=invite_code_obj.history_id)
                    db_session.add(new_session)
                    db_session.add(current_user)
                    db_session.commit()

                    next_invite_code_obj.used = True
                    next_invite_code_obj.user_id = current_user.user_id
                    db_session.add(next_invite_code_obj)
                    db_session.commit()

                redirect_url = f"/chat/{next_session_id}"
                return RedirectResponse(redirect_url)
            # Default redirect to end
            redirect_url = f"/chat/{session_id}/end"
            return RedirectResponse(redirect_url)
