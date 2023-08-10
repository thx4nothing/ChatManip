from typing import Optional
import random
import string

from datetime import datetime, timedelta

from sqlalchemy import Column, Boolean, JSON, Integer
from sqlmodel import Field, SQLModel, create_engine

engine = create_engine("sqlite:///database.db")


class User(SQLModel, table=True):
    user_id: Optional[int] = Field(
        sa_column=Column(Integer, primary_key=True, autoincrement=True, unique=True,
                         nullable=False))
    age: Optional[int] = None
    gender: str
    occupation: str
    location: str
    language: str
    api_prompt_tokens: int = Field(default=0)
    api_completion_tokens: int = Field(default=0)
    api_total_tokens: int = Field(default=0)
    # Token bucket variables
    last_token_update_time: datetime = Field(default_factory=datetime.now, nullable=False)
    available_tokens: int = Field(default=500)
    last_request_time: datetime = Field(default_factory=lambda: datetime.now() - timedelta(seconds=5), nullable=False)


class ChatSession(SQLModel, table=True):
    session_id: Optional[str] = Field(unique=True, primary_key=True)
    user_id: int
    start_time: datetime = Field(default_factory=datetime.now, nullable=False)
    end_time: Optional[datetime] = Field(default=None, nullable=True)
    persona_id: Optional[int] = Field(default=None, nullable=True)
    task_id: Optional[int] = Field(default=None, nullable=True)
    rules: str = Field(default='')
    done: bool = Field(default=False)
    message_limit: int = Field(default=20)
    time_limit: timedelta = Field(default=timedelta(minutes=10))


class Messages(SQLModel, table=True):
    message_id: Optional[int] = Field(
        sa_column=Column(Integer, primary_key=True, autoincrement=True, unique=True, nullable=False))
    message: str
    altered_message: str
    response: str
    altered_response: str
    time_stamp: datetime = Field(default_factory=datetime.now, nullable=False)
    session_id: str


class Persona(SQLModel, table=True):
    persona_id: Optional[int] = Field(
        sa_column=Column(Integer, primary_key=True, autoincrement=True, unique=True,
                         nullable=False))
    name: str = Field("")
    system_instruction: dict = Field(sa_column=Column(JSON, default={}))
    before_instruction: dict = Field(sa_column=Column(JSON, default={}))
    after_instruction: dict = Field(sa_column=Column(JSON, default={}))


class Task(SQLModel, table=True):
    task_id: Optional[int] = Field(
        sa_column=Column(Integer, primary_key=True, autoincrement=True, unique=True,
                         nullable=False))
    name: str = Field("")
    task_instruction: dict = Field(sa_column=Column(JSON, default={}))


def generate_invite_code():
    length = 8
    characters = ''.join(
        c for c in string.ascii_letters + string.digits if c not in ['0', 'O', 'I', 'l'])

    invite_code = ''.join(random.choice(characters) for _ in range(length))
    return invite_code


class InviteCode(SQLModel, table=True):
    invite_code: str = Field(unique=True, primary_key=True)
    user_id: int = Field(default=-1)
    used: bool = Field(sa_column=Column(Boolean), default=False)
    persona_id: Optional[int] = Field(default=None, nullable=True)
    task_id: Optional[int] = Field(default=None, nullable=True)
    rules: str = Field(default='')
