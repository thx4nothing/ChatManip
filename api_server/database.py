"""
Module: database

This module defines SQLModel classes representing database tables and includes
functions related to database operations.

Classes:
    User: Represents user information in the database.
    ChatSession: Represents chat session details in the database.
    Messages: Represents individual chat messages and responses in the database.
    Persona: Represents persona information for chat sessions.
    Task: Represents task information for chat sessions.
    InviteCode: Represents invite codes for user registration and session creation.
    Questionnaire: Represents questionnaire responses in the database.

Functions:
    generate_invite_code: Generates a random invite code for user registration.

Usage:
    Import the classes and functions from this module to interact with the
    database tables and perform operations.

Author: Marlon Beck
Date: 17/08/2023
"""

import random
import string
from datetime import datetime, timedelta
from typing import Optional

from sqlalchemy import Column, Boolean, JSON, Integer
from sqlmodel import Field, SQLModel, create_engine

engine = create_engine("sqlite:///database.db")


class User(SQLModel, table=True):
    """Represents user information in the database."""
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
    last_request_time: datetime = Field(
        default_factory=lambda: datetime.now() - timedelta(seconds=5), nullable=False)


class ChatSession(SQLModel, table=True):
    """Represents chat session details in the database."""
    session_id: Optional[str] = Field(unique=True, primary_key=True)
    user_id: int
    start_time: datetime = Field(default_factory=datetime.now, nullable=False)
    end_time: Optional[datetime] = Field(default=None, nullable=True)
    persona_id: Optional[int] = Field(default=None, nullable=True)
    task_id: Optional[int] = Field(default=None, nullable=True)
    rules: str = Field(default='')
    done: bool = Field(default=False)
    message_limit: int = Field(default=20)
    min_messages_needed: int = Field(default=2)
    time_limit: timedelta = Field(default=timedelta(minutes=10))
    history_id: Optional[int] = Field(default=None, nullable=True)


class Messages(SQLModel, table=True):
    """Represents individual chat messages and responses in the database."""
    message_id: Optional[int] = Field(
        sa_column=Column(Integer, primary_key=True, autoincrement=True, unique=True,
                         nullable=False))
    message: str
    altered_message: str
    response: str
    altered_response: str
    time_stamp: datetime = Field(default_factory=datetime.now, nullable=False)
    session_id: str


class Persona(SQLModel, table=True):
    """Represents persona information for chat sessions."""
    persona_id: Optional[int] = Field(
        sa_column=Column(Integer, primary_key=True, autoincrement=True, unique=True,
                         nullable=False))
    name: str = Field("")
    system_instruction: dict = Field(sa_column=Column(JSON, default={}))
    first_message: dict = Field(sa_column=Column(JSON, default={}))
    before_instruction: dict = Field(sa_column=Column(JSON, default={}))
    after_instruction: dict = Field(sa_column=Column(JSON, default={}))


class Task(SQLModel, table=True):
    """Represents task information for chat sessions."""
    task_id: Optional[int] = Field(
        sa_column=Column(Integer, primary_key=True, autoincrement=True, unique=True,
                         nullable=False))
    name: str = Field("")
    task_instruction: dict = Field(sa_column=Column(JSON, default={}))
    show_discussion_section: bool = Field(default=False)


class History(SQLModel, table=True):
    """Represents task information for chat sessions."""
    history_id: Optional[int] = Field(
        sa_column=Column(Integer, primary_key=True, autoincrement=True, unique=True,
                         nullable=False))
    name: str = Field("")
    history: dict = Field(sa_column=Column(JSON, default={}))


class InviteCode(SQLModel, table=True):
    """Represents invite codes for user registration and session creation."""
    invite_code: str = Field(unique=True, primary_key=True)
    user_id: int = Field(default=-1)
    used: bool = Field(sa_column=Column(Boolean), default=False)
    persona_id: Optional[int] = Field(default=None, nullable=True)
    task_id: Optional[int] = Field(default=None, nullable=True)
    rules: str = Field(default='')
    next_session_id: Optional[str] = Field(default='none')
    history_id: Optional[int] = Field(default=None, nullable=True)


class Questionnaire(SQLModel, table=True):
    """Represents questionnaire responses in the database."""
    questionnaire_id: Optional[int] = Field(
        sa_column=Column(Integer, primary_key=True, autoincrement=True, unique=True,
                         nullable=False))
    qa: dict = Field(sa_column=Column(JSON, default={}))
    time_stamp: datetime = Field(default_factory=datetime.now, nullable=False)
    session_id: str


class Settings(SQLModel, table=True):
    """Represents the settings in the database."""
    settings_id: Optional[int] = Field(
        sa_column=Column(Integer, primary_key=True, autoincrement=True, unique=True,
                         nullable=False))
    temperature: float = 1.0
    model: str = "gpt-3.5-turbo"


def generate_invite_code():
    """
    Generates a random invite code for user registration.

    Returns:
        str: A randomly generated invite code.
    """
    length = 8
    characters = ''.join(
        c for c in string.ascii_letters + string.digits if c not in ['0', 'O', 'I', 'l'])

    invite_code = ''.join(random.choice(characters) for _ in range(length))
    return invite_code
