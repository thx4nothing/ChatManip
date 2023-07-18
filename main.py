import uuid

from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import os
import openai
from pydantic import BaseModel
from starlette.responses import RedirectResponse

from database import *
from sqlmodel import SQLModel, create_engine, Session, select

engine = create_engine("sqlite:///database.db")


def create_db_and_tables():
    SQLModel.metadata.create_all(engine)


app = FastAPI()

# Mount static files directory to serve CSS and JavaScript
app.mount("/static", StaticFiles(directory="static"), name="static")

# Create Jinja2Templates instance
templates = Jinja2Templates(directory="templates")


@app.on_event("startup")
def on_startup():
    create_db_and_tables()


# openai.api_key = os.getenv("OPENAI_API_KEY")
# openai.Model.list()

class Message(BaseModel):
    content: str


class UserInformation(BaseModel):
    first_name: str
    last_name: str
    age: int


# Route to serve the index.html template on root URL ("/")
@app.get("/")
async def read_root(request: Request):
    return templates.TemplateResponse("user_creation_base.html", {"request": request})


@app.get("/session/{session_id}")
async def session(session_id: int, request: Request):
    with Session(engine) as db_session:
        statement = select(ChatSession).where(ChatSession.session_id == session_id)
        current_session = db_session.exec(statement).first()
        print(current_session)
        if current_session is None:
            return RedirectResponse(url="/")

    return templates.TemplateResponse("chat_base.html", {"request": request})


@app.post("/chat")
async def chat(message: Message):
    # Process the chat message
    response = process_chat_message(message.content)
    return {"response": response}


@app.get("/admin")
async def read_root(request: Request):
    return templates.TemplateResponse("admin_base.html", {"request": request})


@app.post("/create_user")
async def create_user(user: UserInformation):
    with Session(engine) as db_session:
        statement = select(User).where(User.first_name == user.first_name).where(User.last_name == user.last_name).where(User.age == user.age)
        current_user = db_session.exec(statement).first()
        if current_user is None:
            new_user = User(first_name=user.first_name, last_name=user.last_name, age=user.age)
            db_session.add(new_user)
            db_session.commit()
            current_user = db_session.exec(statement).first()
            new_session = ChatSession(user_id=current_user.user_id)
            db_session.add(new_session)
            db_session.commit()
            statement = select(ChatSession).where(ChatSession.user_id == current_user.user_id)
            current_session = db_session.exec(statement).first()
            session_id = str(current_session.session_id)
            redirect_url = f"/session/{session_id}"
            print(redirect_url)
            return RedirectResponse(url=redirect_url, status_code=303)

    return RedirectResponse(url="/")


def process_chat_message(message: str):
    return "Antwort"
