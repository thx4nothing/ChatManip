from uuid import uuid4 as uuid4
from typing import Optional
from utcnow import utcnow

from datetime import datetime
from sqlmodel import Field, SQLModel, create_engine
import sqlalchemy as sa


engine = create_engine("sqlite:///database.db")

class User(SQLModel, table=True):
    user_id: Optional[int] = Field(
        sa_column=sa.Column(sa.Integer, primary_key=True, autoincrement=True, unique=True,
                            nullable=False))
    first_name: str
    last_name: str
    age: Optional[int] = None
    api_calls: int = Field(default=0)


class ChatSession(SQLModel, table=True):
    session_id: Optional[int] = Field(
        sa_column=sa.Column(sa.Integer, primary_key=True, autoincrement=True, unique=True,
                            nullable=False))
    user_id: int
    start_time: datetime = Field(default_factory=datetime.now, nullable=False)
    end_time: Optional[datetime] = Field(default=None, nullable=True)
    system_instruction: str = ''
    system_rules: str = ''


class Messages(SQLModel, table=True):
    message_id: Optional[int] = Field(
        sa_column=sa.Column(sa.Integer, primary_key=True, autoincrement=True, unique=True,
                            nullable=False))
    message: str
    altered_message: str
    response: str
    altered_response: str
    time_stamp: datetime = Field(default_factory=datetime.now, nullable=False)
    session_id: int


class Persona(SQLModel, table=True):
    persona_id: Optional[int] = Field(
        sa_column=sa.Column(sa.Integer, primary_key=True, autoincrement=True, unique=True,
                            nullable=False))
    name: str
    system_instruction: str = ''
    before_instruction: str = ''
    after_instruction: str = ''
