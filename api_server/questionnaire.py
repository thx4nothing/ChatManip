from typing import Dict

from fastapi import APIRouter, Request
from sqlmodel import Session, select

from api_server.database import engine, ChatSession, Questionnaire
from api_server.templates import templates

router = APIRouter()


@router.get("/{session_id}")
async def read_root(session_id: str, request: Request):
    with Session(engine) as db_session:
        statement = select(ChatSession).where(ChatSession.session_id == session_id)
        current_session = db_session.exec(statement).first()
        if current_session is not None:
            return templates.TemplateResponse("questionnaire.html", {"request": request})


@router.post("/{session_id}")
async def submit_questionnaire(session_id: str, data: Dict[str, str]):
    with Session(engine) as db_session:
        questionnaire = Questionnaire(qa=data, session_id=session_id)
        db_session.add(questionnaire)
        db_session.commit()
        return {"message": "Questionnaire data submitted successfully"}
