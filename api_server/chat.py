import os
import sys

import openai
from fastapi import APIRouter, Request
from sqlmodel import Session, select
from starlette.responses import RedirectResponse

from api_server.database import engine, ChatSession, Persona, User, Messages
from api_server.rule import Rule
from api_server.templates import templates
from api_server.models import Message

# FastAPI Routing
router = APIRouter()

# OpenAI Init
openai.api_key = os.getenv("OPENAI_API_KEY")


# openai.Model.list()

@router.get("/session/{session_id}")
async def session(session_id: str, request: Request):
    with Session(engine) as db_session:
        statement = select(ChatSession).where(ChatSession.session_id == session_id)
        current_session = db_session.exec(statement).first()
        if current_session is None:
            return RedirectResponse(url="/")

    return templates.TemplateResponse("chat_base.html", {"request": request})


@router.post("/chat/{session_id}")
async def chat(session_id: str, message: Message):
    # Process the chat message
    print(session_id)
    response = process_chat_message(message.content, session_id)
    return {"response": response}


def process_chat_message(message: str, session_id: str):
    # set variables
    altered_message = message

    with Session(engine) as db_session:
        statement = select(ChatSession).where(ChatSession.session_id == session_id)
        current_session = db_session.exec(statement).first()
        if current_session is not None:
            statement = select(Persona).where(Persona.persona_id == current_session.persona_id)
            persona = db_session.exec(statement).first()

            # post system instruction if its first time
            statement = select(Messages).where(Messages.session_id == session_id)
            all_messages = db_session.exec(statement).all()
            messages = [{"role": "system", "content": persona.system_instruction}]
            for db_message in all_messages:
                messages.append({"role": "user", "content": db_message.altered_message})
                messages.append({"role": "system", "content": db_message.response})

            # pre process message

            for rule in current_session.rules.split(","):
                try:
                    rule_class = getattr(sys.modules["api_server.rule"], rule)
                    if issubclass(rule_class, Rule):
                        rule_instance = rule_class()
                        altered_message = rule_instance.preprocessing(altered_message)
                except AttributeError:
                    print(f"{rule} is not a defined class.")

            # apply persona
            if persona:
                if persona.before_instruction:
                    altered_message = persona.before_instruction + "\n" + altered_message
                if persona.after_instruction:
                    altered_message = altered_message + "\n" + persona.after_instruction

            # send message to api
            messages.append({"role": "user", "content": altered_message})
            completion = openai.ChatCompletion.create(model="gpt-3.5-turbo", messages=messages)
            chat_response = completion.choices[0].message.content
            altered_response = chat_response
            print(chat_response)

            # post process response

            for rule in current_session.rules.split(","):
                try:
                    rule_class = getattr(sys.modules["api_server.rule"], rule)
                    if issubclass(rule_class, Rule):
                        rule_instance = rule_class()
                        altered_response = rule_instance.postprocessing(altered_response)
                except AttributeError:
                    print(f"{rule} is not a defined class.")

            # add message and response into database
            db_message = Messages(message=message, altered_message=altered_message,
                                  response=chat_response, altered_response=altered_response,
                                  session_id=session_id)
            db_session.add(db_message)

            # add api calls to database
            statement = select(User).where(User.user_id == current_session.user_id)
            current_user = db_session.exec(statement).first()
            current_user.api_prompt_tokens += completion.usage.prompt_tokens
            current_user.api_completion_tokens += completion.usage.completion_tokens
            current_user.api_total_tokens += completion.usage.total_tokens
            db_session.add(current_user)

            # commit
            db_session.commit()

            return altered_response