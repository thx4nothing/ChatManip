from fastapi import APIRouter, Request
from pydantic import BaseModel

from sqlmodel import Session, select
from starlette.responses import RedirectResponse

from api_server.database import engine, ChatSession
from api_server.templates import templates
from api_server.models import Message

router = APIRouter()


@router.get("/session/{session_id}")
async def session(session_id: int, request: Request):
    with Session(engine) as db_session:
        statement = select(ChatSession).where(ChatSession.session_id == session_id)
        current_session = db_session.exec(statement).first()
        print(current_session)
        if current_session is None:
            return RedirectResponse(url="/")

    return templates.TemplateResponse("chat_base.html", {"request": request})


@router.post("/chat")
async def chat(message: Message):
    # Process the chat message
    response = process_chat_message(message.content)
    return {"response": response}


def process_chat_message(message: str):
    return "Antwort"
