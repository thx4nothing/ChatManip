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
    get_session_language
from api_server.templates import templates

router = APIRouter()


@router.get("/{session_id}/before")
async def read_before(session_id: str, request: Request):
    """
    Retrieve the questionnaire page template for a given session ID.

    Parameters:
    - `session_id` (str): The ID of the chat session.

    Returns:
    A FastAPI TemplateResponse containing the questionnaire HTML template.
    """
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
            return templates.TemplateResponse("questionnaire_before.html", {"request": request,
                                                                            "show_discussion_section": show_discussion_section,
                                                                            "intention": intention})


@router.get("/{session_id}/after")
async def read_after(session_id: str, request: Request):
    """
    Retrieve the questionnaire page template for a given session ID.

    Parameters:
    - `session_id` (str): The ID of the chat session.

    Returns:
    A FastAPI TemplateResponse containing the questionnaire HTML template.
    """
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
            return templates.TemplateResponse("questionnaire_after.html", {"request": request,
                                                                           "show_discussion_section": show_discussion_section,
                                                                           "intention": intention,
                                                                           "translations": translation_data})


@router.get("/{session_id}/show_discussion")
async def read_after(session_id: str, request: Request):
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
        return {"message": "Questionnaire data submitted successfully"}
