import sys
from datetime import datetime

from fastapi import APIRouter, Request
from sqlmodel import Session, select
from starlette.responses import RedirectResponse

from api_server.chatgpt_interface import request_response, Ok, Err
from api_server.database import engine, ChatSession, Persona, User, Messages, Task
from api_server.models import Message
from api_server.rule import *
from api_server.templates import templates

router = APIRouter()


@router.get("/{session_id}")
async def session(session_id: str, request: Request):
    with Session(engine) as db_session:
        statement = select(ChatSession).where(ChatSession.session_id == session_id)
        current_session = db_session.exec(statement).first()
        if current_session is None:
            return RedirectResponse(url="/")

    return templates.TemplateResponse("chat.html", {"request": request})


def add_message_to_database(db_session, session_id, message, altered_message, chat_response, altered_response):
    db_message = Messages(message=message, altered_message=altered_message,
                          response=chat_response, altered_response=altered_response,
                          session_id=session_id)
    db_session.add(db_message)
    db_session.commit()


@router.get("/{session_id}/disclaimer")
async def disclaimer(session_id: str):
    return get_session_task(session_id)


def get_session_task(session_id: str):
    with Session(engine) as db_session:
        statement = select(ChatSession).where(ChatSession.session_id == session_id)
        current_session = db_session.exec(statement).first()
        if current_session is not None:
            statement = select(Task).where(Task.task_id == current_session.task_id)
            current_task = db_session.exec(statement).first()
            if current_task:
                language = get_session_language(db_session, current_session)
                return current_task.task_instruction[language]
            else:
                return "Enjoy!"


@router.get("/{session_id}/greetings")
async def get_session_greetings(session_id: str):
    print("Greetings requested.")
    with Session(engine) as db_session:
        statement = select(ChatSession).where(ChatSession.session_id == session_id)
        current_session = db_session.exec(statement).first()
        if current_session is not None:
            persona = get_session_persona(db_session, current_session)
            messages = []
            language = get_session_language(db_session, current_session)
            if persona:
                messages.append({"role": "system", "content": persona.system_instruction[language]})

            task = get_session_task(session_id)
            if task != "Enjoy!":
                if language == "english":
                    message = "I was given this task, please greet me accordingly:\n" + task
                else:
                    message = "Mir wurde diese Aufgabe gegeben, bitte begrüße mich entsprechend:\n" + task
            else:
                if language == "english":
                    message = "Greet me please."
                else:
                    message = "Begrüße mich, bitte."
            messages.append({"role": "user", "content": message})
            chat_response = request_response(session_id, messages)
            if isinstance(chat_response, Ok):
                add_message_to_database(db_session, session_id, "", "", chat_response.value, "")
                return {"response": chat_response.value}
            else:
                print(chat_response.error_message)


@router.get("/{session_id}/history")
async def get_session_history(session_id: str):
    with Session(engine) as db_session:
        statement = select(ChatSession).where(ChatSession.session_id == session_id)
        current_session = db_session.exec(statement).first()
        if current_session is not None:
            persona = get_session_persona(db_session, current_session)
            messages = get_chat_history(db_session, current_session, persona, altered=False)
            return messages


@router.get("/{session_id}/check_done")
def check_session_done(session_id: str):
    with Session(engine) as db_session:
        statement = select(ChatSession).where(ChatSession.session_id == session_id)
        current_session = db_session.exec(statement).first()
        if current_session is not None:
            elapsed_time = datetime.now() - current_session.start_time
            time_limit_reached = elapsed_time >= current_session.time_limit
            statement = select(Messages).where(Messages.session_id == session_id)
            message_count = len(db_session.exec(statement).all())
            message_limit_reached = message_count >= current_session.message_limit

            time_left = (current_session.time_limit - elapsed_time).total_seconds()
            messages_left = current_session.message_limit - message_count

            if time_limit_reached or message_limit_reached:
                return {"session_end": True, "time_left": 0, "messages_left": 0}
            else:
                return {"session_end": False, "time_left": time_left, "messages_left": messages_left}
        else:
            return {"error": "Session not found."}


@router.get("/{session_id}/end")
def end_session(session_id: str):
    with Session(engine) as db_session:
        statement = select(ChatSession).where(ChatSession.session_id == session_id)
        current_session = db_session.exec(statement).first()
        if current_session is not None:
            current_session.done = True
            return {"message": "Chat session ended."}


@router.post("/{session_id}")
async def send_message(session_id: str, message: Message):
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
        if persona.before_instruction[get_session_language(db_session, current_session)]:
            altered_message = persona.before_instruction[
                                  get_session_language(db_session, current_session)] + "\n" + altered_message
        if persona.after_instruction[get_session_language(db_session, current_session)]:
            altered_message = altered_message + "\n" + persona.after_instruction[
                get_session_language(db_session, current_session)]
        print("Altered Message:")
        print(altered_message)
    print("End of Persona.")

    # send message to api
    messages.append({"role": "user", "content": altered_message})
    chat_response = request_response(current_session.session_id, messages)
    if isinstance(chat_response, Err):
        print(chat_response.error_message)
        return chat_response.error_message
    else:
        chat_response = chat_response.value

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


def get_session_language(db_session: Session, current_session: ChatSession):
    statement = select(User).where(User.user_id == current_session.user_id)
    user = db_session.exec(statement).first()
    return user.language


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
        messages.append({"role": "system",
                         "content": persona.system_instruction[get_session_language(db_session, current_session)]})
        print("Persona system instruction:")
        print(persona.system_instruction[get_session_language(db_session, current_session)])
    for db_message in all_messages:
        message = db_message.altered_message if altered else db_message.message
        messages.append({"role": "user", "content": message})
        messages.append({"role": "assistant", "content": db_message.response})
    return messages
