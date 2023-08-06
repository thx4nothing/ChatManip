import sys

from fastapi import APIRouter, Request
from sqlmodel import Session, select
from starlette.responses import RedirectResponse

from api_server.database import engine, ChatSession, Persona, User, Messages
from api_server.rule import *
from api_server.templates import templates
from api_server.models import Message
from api_server.chatgpt_interface import request_response, Ok, Err

# FastAPI Routing
router = APIRouter()


@router.get("/session/{session_id}")
async def session(session_id: str, request: Request):
    with Session(engine) as db_session:
        statement = select(ChatSession).where(ChatSession.session_id == session_id)
        current_session = db_session.exec(statement).first()
        if current_session is None:
            return RedirectResponse(url="/")

    return templates.TemplateResponse("chat_base.html", {"request": request})


def add_message_to_database(db_session, session_id, message, altered_message, chat_response, altered_response):
    db_message = Messages(message=message, altered_message=altered_message,
                          response=chat_response, altered_response=altered_response,
                          session_id=session_id)
    db_session.add(db_message)
    db_session.commit()


@router.get("/chat/{session_id}/greetings")
async def greetings(session_id: str):
    print("Greetings requested.")
    with Session(engine) as db_session:
        statement = select(ChatSession).where(ChatSession.session_id == session_id)
        current_session = db_session.exec(statement).first()
        if current_session is not None:
            persona = get_session_persona(db_session, current_session)
            messages = []
            if persona:
                messages.append({"role": "system", "content": persona.system_instruction})
            greetings_request = "Greet me please."
            messages.append({"role": "user", "content": greetings_request})
            chat_response = request_response(session_id, messages)
            if isinstance(chat_response, Ok):
                add_message_to_database(db_session, session_id, "", "", chat_response.value, "")
                return {"response": chat_response.value}
            else:
                print(chat_response.error_message)


@router.get("/session/{session_id}/history")
async def history(session_id: str):
    with Session(engine) as db_session:
        statement = select(ChatSession).where(ChatSession.session_id == session_id)
        current_session = db_session.exec(statement).first()
        if current_session is not None:
            persona = get_session_persona(db_session, current_session)
            messages = get_chat_history(db_session, current_session, persona, altered=False)
            return messages


@router.post("/chat/{session_id}")
async def chat(session_id: str, message: Message):
    with Session(engine) as db_session:
        statement = select(ChatSession).where(ChatSession.session_id == session_id)
        current_session = db_session.exec(statement).first()
        if current_session is not None:
            # Process the chat message
            print(session_id)
            response = process_user_chat_message(db_session, current_session, message.content)
            # process user input
            # process response
            return {"response": response}


def process_user_chat_message(db_session: Session, current_session: ChatSession, message: str) -> str:
    # get persona
    persona = get_session_persona(db_session, current_session)

    # get chat history
    messages = get_chat_history(db_session, current_session, persona)

    # pre process message

    altered_message = message
    for rule in current_session.rules.split(","):
        try:
            rule_class = getattr(sys.modules["api_server.rule"], rule)
            if issubclass(rule_class, Rule):
                rule_instance = rule_class()
                altered_message = rule_instance.preprocessing(altered_message)
        except AttributeError:
            print(f"{rule} is not a defined class.")

    # apply persona
    print("Start of Persona:")
    if persona:
        print(persona.name)
        if persona.before_instruction:
            altered_message = persona.before_instruction + "\n" + altered_message
        if persona.after_instruction:
            altered_message = altered_message + "\n" + persona.after_instruction
        print("Altered Message:")
        print(altered_message)
    print("End of Persona.")

    # send message to api
    messages.append({"role": "user", "content": altered_message})
    chat_response = request_response(current_session.session_id, messages)
    if isinstance(chat_response, Err):
        print(chat_response.error_message)
    else:
        chat_response = chat_response.value
    print(chat_response)

    # post process response

    altered_response = chat_response
    for rule in current_session.rules.split(","):
        try:
            rule_class = getattr(sys.modules["api_server.rule"], rule)
            if issubclass(rule_class, Rule):
                rule_instance = rule_class()
                altered_response = rule_instance.postprocessing(altered_response)
        except AttributeError:
            print(f"{rule} is not a defined class.")

    # add message and response into database
    add_message_to_database(db_session, current_session.session_id, message, altered_message, chat_response,
                            altered_response)

    return altered_response


def get_session_persona(db_session: Session, current_session: ChatSession):
    statement = select(Persona).where(Persona.persona_id == current_session.persona_id)
    persona = db_session.exec(statement).first()
    return persona


def get_chat_history(db_session: Session, current_session: ChatSession, persona: Persona,
                     altered=True):
    statement = select(Messages).where(Messages.session_id == current_session.session_id)
    all_messages = db_session.exec(statement).all()
    messages = []
    if persona:
        messages.append({"role": "system", "content": persona.system_instruction})
        print("Persona system instruction:")
        print(persona.system_instruction)
    for db_message in all_messages:
        message = db_message.altered_message if altered else db_message.message
        messages.append({"role": "user", "content": message})
        messages.append({"role": "assistant", "content": db_message.response})
    return messages


@router.get("/session/{session_id}/disclaimer")
async def disclaimer(session_id: str):
    return "Hey this is a disclaimer"
