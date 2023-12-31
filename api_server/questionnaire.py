"""
API Router for Chat Session Questionnaires.

This module defines FastAPI routes to handle reading and submitting questionnaires
associated with chat sessions. It interacts with a SQL database to store and retrieve
questionnaire data for each session.

Author: Marlon Beck
Date: 17/08/2023
"""
import json
from typing import Dict

from fastapi import APIRouter, Request
from sqlmodel import Session, select
from starlette.responses import JSONResponse

from api_server.database import engine, ChatSession, Questionnaire, Task, Messages, \
    get_session_language, InviteCode
from api_server.logger import logger as logger
from api_server.templates import templates

router = APIRouter()


def read_questionnaire(template: str, session_id: str, request: Request):
    with Session(engine) as db_session:
        statement = select(ChatSession).where(ChatSession.session_id == session_id)
        current_session = db_session.exec(statement).first()
        if current_session is not None:
            statement = select(Task).where(Task.task_id == current_session.task_id)
            current_task = db_session.exec(statement).first()
            if current_task:
                show_discussion_section = current_task.show_discussion_section
                statement = select(Messages).where(
                    Messages.session_id == current_session.session_id)
                intention = db_session.exec(statement).all()[-1].response
            else:
                show_discussion_section = False
                intention = ""
            if get_session_language(db_session, current_session) == "english":
                with open("static/translations/questionnaire_en.json", "r",
                          encoding="utf-8") as translation_file:
                    translation_data = json.load(translation_file)
            else:
                with open("static/translations/questionnaire_de.json", "r",
                          encoding="utf-8") as translation_file:
                    translation_data = json.load(translation_file)
            return templates.TemplateResponse(template, {"request": request,
                                                         "show_discussion_section": show_discussion_section,
                                                         "intention": intention,
                                                         "translations": translation_data})


@router.get("/{session_id}/before")
async def read_before(session_id: str, request: Request):
    return read_questionnaire("questionnaire_before.html", session_id, request)


@router.get("/{session_id}/after")
async def read_after(session_id: str, request: Request):
    return read_questionnaire("questionnaire_after.html", session_id, request)


@router.get("/{session_id}/show_discussion")
async def read_after(session_id: str):
    with Session(engine) as db_session:
        statement = select(ChatSession).where(ChatSession.session_id == session_id)
        current_session = db_session.exec(statement).first()
        if current_session is not None:
            statement = select(Task).where(Task.task_id == current_session.task_id)
            current_task = db_session.exec(statement).first()
            if current_task:
                show_discussion_section = current_task.show_discussion_section
            else:
                show_discussion_section = False
            return JSONResponse(content={"show_discussion_section": show_discussion_section})


@router.get("/{session_id}/has_next")
async def has_next(session_id: str):
    with Session(engine) as db_session:
        statement = select(ChatSession).where(ChatSession.session_id == session_id)
        current_session = db_session.exec(statement).first()
        if current_session is not None:
            statement = select(InviteCode).where(InviteCode.invite_code == session_id)
            invite_code_obj = db_session.exec(statement).first()
            next_session_id = invite_code_obj.next_session_id
            if next_session_id != "none":
                return {"has_next": True}
    return {"has_next": False}


@router.post("/{session_id}")
async def submit_questionnaire(session_id: str, data: Dict[str, str]):
    """
    Submit a questionnaire for a specific session ID.

    Parameters:
    - `session_id` (str): The ID of the chat session.
    - `data` (Dict[str, str]): A dictionary containing questionnaire answers.

    Returns:
    A dictionary with a success message upon successful submission.
    """
    with Session(engine) as db_session:
        questionnaire = Questionnaire(qa=data, session_id=session_id)
        db_session.add(questionnaire)
        db_session.commit()
        db_session.refresh(questionnaire)

        logger.info("Received questionnaire data: %s", data)

        return {"message": "Questionnaire data submitted successfully"}
