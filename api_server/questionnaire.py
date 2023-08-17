"""
API Router for Chat Session Questionnaires.

This module defines FastAPI routes to handle reading and submitting questionnaires
associated with chat sessions. It interacts with a SQL database to store and retrieve
questionnaire data for each session.

Author: Marlon Beck
Date: 17/08/2023
"""

from typing import Dict

from fastapi import APIRouter, Request
from sqlmodel import Session, select

from api_server.database import engine, ChatSession, Questionnaire
from api_server.templates import templates

router = APIRouter()


@router.get("/{session_id}")
async def read_root(session_id: str, request: Request):
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
            return templates.TemplateResponse("questionnaire.html", {"request": request})


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
