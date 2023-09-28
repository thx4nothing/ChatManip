import json
import sys
from datetime import datetime

from fastapi import APIRouter, Request
from sqlmodel import Session, select
from starlette.responses import RedirectResponse

from api_server.chatgpt_interface import request_response, Err
from api_server.database import engine, ChatSession, Persona, Messages, Task, History, \
    get_session_language, User
from api_server.logger import logger as logger
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

        if get_session_language(db_session, current_session) == "german":
            with open("static/translations/chat_de.json", "r",
                      encoding="utf-8") as translation_file:
                translation_data = json.load(translation_file)
        else:
            with open("static/translations/chat_en.json", "r",
                      encoding="utf-8") as translation_file:
                translation_data = json.load(translation_file)
    return templates.TemplateResponse("chat.html",
                                      {"request": request, "translations": translation_data})


def add_message_to_database(db_session, session_id, message, altered_message, chat_response,
                            altered_response):
    db_message = Messages(message=message, altered_message=altered_message,
                          response=chat_response, altered_response=altered_response,
                          session_id=session_id)
    db_session.add(db_message)
    db_session.commit()


@router.get("/{session_id}/task")
async def get_session_task(session_id: str):
    with Session(engine) as db_session:
        statement = select(ChatSession).where(ChatSession.session_id == session_id)
        current_session = db_session.exec(statement).first()
        if current_session is not None:
            language = get_session_language(db_session, current_session)
            statement = select(Task).where(Task.task_id == current_session.task_id)
            current_task = db_session.exec(statement).first()
            if current_task:
                return current_task.task_instruction[language]
            # Default value
            if language == "german":
                return "Viel Spaß!"
            return "Enjoy!"


@router.get("/{session_id}/history")
async def get_session_history(session_id: str):
    with Session(engine) as db_session:
        statement = select(ChatSession).where(ChatSession.session_id == session_id)
        current_session = db_session.exec(statement).first()
        if current_session is not None:
            persona = get_session_persona(db_session, current_session)
            messages = get_chat_history(db_session, current_session, persona,
                                        requested_by_user=True)
            return messages


@router.get("/{session_id}/check_done")
async def check_session_done(session_id: str):
    with Session(engine) as db_session:
        statement = select(ChatSession).where(ChatSession.session_id == session_id)
        current_session = db_session.exec(statement).first()
        if current_session is not None:
            # time limit
            elapsed_time = datetime.now() - current_session.start_time
            time_limit_reached = elapsed_time >= current_session.time_limit

            # message limit
            statement = select(User).where(User.user_id == current_session.user_id)
            current_user = db_session.exec(statement).first()

            time_left = (current_session.time_limit - elapsed_time).total_seconds()

            can_end_session = current_user.available_tokens <= 9000

            if time_limit_reached or current_session.done:
                return {"session_end": True, "time_left": time_left,
                        "available_tokens": current_user.available_tokens,
                        "can_end_session": can_end_session}

            return {"session_end": False, "time_left": time_left,
                    "available_tokens": current_user.available_tokens,
                    "can_end_session": can_end_session}
        else:
            return {"error": "Session not found."}


@router.get("/{session_id}/session_end")
async def end_session(session_id: str, request: Request):
    with Session(engine) as db_session:
        statement = select(ChatSession).where(ChatSession.session_id == session_id)
        current_session = db_session.exec(statement).first()
        if current_session is not None and not current_session.done:
            current_session.done = True

            messages = get_chat_history(db_session, current_session)

            if get_session_language(db_session, current_session) == "german":
                ask_intention = ("Bitte beschreibe, was die Absicht des Nutzers über den gesamten "
                                 "Verlauf des Chatgesprächs hinweg war.")
            else:
                ask_intention = ("What was the user's likely intention behind the entire chat "
                                 "history?")

            messages.append({"role": "user", "content": ask_intention})
            chat_response = request_system_response(messages)
            add_message_to_database(db_session, current_session.session_id, ask_intention,
                                    ask_intention, chat_response, chat_response)


@router.get("/{session_id}/end")
async def end(session_id: str, request: Request):
    with Session(engine) as db_session:
        statement = select(ChatSession).where(ChatSession.session_id == session_id)
        current_session = db_session.exec(statement).first()
        if current_session is not None:
            if get_session_language(db_session, current_session) == "german":
                with open("static/translations/end_de.json", "r",
                          encoding="utf-8") as translation_file:
                    translation_data = json.load(translation_file)
            else:
                with open("static/translations/end_en.json", "r",
                          encoding="utf-8") as translation_file:
                    translation_data = json.load(translation_file)
            return templates.TemplateResponse("end.html",
                                              {"request": request,
                                               "translations": translation_data})


@router.post("/{session_id}")
async def send_message(session_id: str, message: Message):
    with Session(engine) as db_session:
        statement = select(ChatSession).where(ChatSession.session_id == session_id)
        current_session = db_session.exec(statement).first()
        if current_session is not None:
            response = process_user_chat_message(db_session, current_session, message.content)
            return {"response": response}


def process_user_chat_message(db_session: Session, current_session: ChatSession,
                              message: str) -> str:
    logger.debug("Starting to process user message. Message: %s", message)

    # get language
    language = get_session_language(db_session, current_session)

    # get persona
    persona = get_session_persona(db_session, current_session)

    # get chat history
    messages = get_chat_history(db_session, current_session, persona)

    # pre process message

    altered_message = message
    for rule in current_session.rules.split(","):
        if rule:
            try:
                rule_class = getattr(sys.modules["api_server.rule"], rule)
                if issubclass(rule_class, Rule):
                    rule_instance = rule_class()
                    altered_message = rule_instance.preprocessing(altered_message)
            except AttributeError:
                logger.warning(f"{rule} is not a defined class.")

    # apply persona
    if persona:
        if persona.before_instruction[language]:
            altered_message = persona.before_instruction[language] + "\n" + altered_message
        if persona.after_instruction[language]:
            altered_message = altered_message + "\n" + persona.after_instruction[language]
        logger.debug("Applying persona. Name: %s, Altered Message: %s", persona.name,
                     altered_message)

    # send message to api
    messages.append({"role": "user", "content": altered_message})
    chat_response = request_response(current_session.session_id, messages)
    if isinstance(chat_response, Err):
        logger.warning(chat_response.error_message)
        return chat_response.error_message

    chat_response = chat_response.value

    # post process response

    altered_response = chat_response
    for rule in current_session.rules.split(","):
        if rule:
            try:
                rule_class = getattr(sys.modules["api_server.rule"], rule)
                if issubclass(rule_class, Rule):
                    rule_instance = rule_class()
                    altered_response = rule_instance.postprocessing(altered_response)
            except AttributeError:
                logger.warning(f"{rule} is not a defined class.")

    # add message and response into database
    add_message_to_database(db_session, current_session.session_id, message, altered_message,
                            chat_response,
                            altered_response)

    return altered_response


def get_session_persona(db_session: Session, current_session: ChatSession):
    statement = select(Persona).where(Persona.persona_id == current_session.persona_id)
    persona = db_session.exec(statement).first()
    return persona


def get_chat_history(db_session: Session, current_session: ChatSession, persona: Persona = None,
                     requested_by_user=False):
    statement = select(Messages).where(Messages.session_id == current_session.session_id)
    all_messages = db_session.exec(statement).all()
    messages = []

    language = get_session_language(db_session, current_session)

    if not requested_by_user:
        statement = select(History).where(History.history_id == current_session.history_id)
        history_obj = db_session.exec(statement).first()
        if history_obj:
            history = history_obj.history[language]
            messages = history

    if persona:
        messages.append({"role": "system",
                         "content": persona.system_instruction[language]})
        if persona.first_message and not requested_by_user:
            messages.append({"role": "user",
                             "content": persona.first_message[language]})
            messages.append({"role": "assistant",
                             "content": "Okay."})

    for db_message in all_messages:
        message = db_message.altered_message if not requested_by_user else db_message.message
        response = db_message.altered_response if requested_by_user else db_message.response
        messages.append({"role": "user", "content": message})
        messages.append({"role": "assistant", "content": response})
    return messages
