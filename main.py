from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import os
import openai
from pydantic import BaseModel

from typing import Optional
from sqlmodel import Field, SQLModel


app = FastAPI()


# openai.api_key = os.getenv("OPENAI_API_KEY")
# openai.Model.list()

class Message(BaseModel):
    content: str


# Mount static files directory to serve CSS and JavaScript
app.mount("/static", StaticFiles(directory="static"), name="static")

# Create Jinja2Templates instance
templates = Jinja2Templates(directory="templates")


# Route to serve the index.html template on root URL ("/")
@app.get("/")
async def read_root(request: Request):
    return templates.TemplateResponse("chat_base.html", {"request": request})


@app.post("/chat")
def chat(message: Message):
    # Process the chat message
    response = process_chat_message(message.content)
    return {"response": response}

@app.get("/admin")
async def read_root(request: Request):
    return templates.TemplateResponse("admin_base.html", {"request": request})


def process_chat_message(message: str):
    return "Antwort"
