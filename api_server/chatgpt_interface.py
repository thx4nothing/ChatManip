"""
Module: chatgpt_interface

This module contains functions to interact with the OpenAI ChatGPT API for
requesting chat completions, calculating tokens, and managing rate limits.

Functions:
    request_system_response: Requests a chat response from the OpenAI ChatGPT
                                model using provided messages.
    request_response: Manages rate limits, token calculations,
                        and makes requests to the OpenAI ChatGPT model.
    num_tokens_from_string: Returns the number of tokens in a text string.
    num_tokens_from_messages: Returns the number of tokens used by a list of messages.

Usage:
    Import the functions from this module to interact with the
    ChatGPT model and manage rate limits and tokens.

Author: Marlon Beck
Date: 17/08/2023
"""

import os
from datetime import datetime

import openai
import tiktoken
from sqlmodel import Session, select

from api_server.database import engine, User, ChatSession, Settings
from api_server.logger import logger as logger


class Ok:
    """Represents a successful result or value."""

    def __init__(self, value):
        self.value = value


class Err:
    """Represents an error message or failure."""

    def __init__(self, error_message):
        self.error_message = error_message


# OpenAI Init
openai.api_key = os.getenv("OPENAI_API_KEY")

# rate limits
min_time_between_requests: float = 1.0


def get_settings():
    with Session(engine) as db_session:
        statement = select(Settings)
        settings = db_session.exec(statement).first()
        if settings:
            return settings.model, settings.temperature
        return "gpt-3.5-turbo", 1.0  # default values


def request_system_response(messages: list[dict[str, str]]):
    """
    Requests a chat response from the OpenAI GPT-3 model using provided messages.

    Args:
        messages (list): List of messages in the format
        [{"role": "user", "content": "message_text"}, ...].

    Returns:
        str: The generated chat response.
    """
    logger.debug("System response requested. Context: %s", messages)
    # Make the API request
    model, temperature = get_settings()
    completion = openai.ChatCompletion.create(model=model, messages=messages,
                                              temperature=temperature)
    chat_response = completion.choices[0].message.content
    logger.info("System response: %s", chat_response)
    return chat_response


def request_response(session_id: str, messages: list[dict[str, str]]):
    """
    Manages rate limits, token calculations, and makes requests to the OpenAI GPT-3 model.

    Args:
        session_id (str): The session ID associated with the chat session.
        messages (list): List of messages in the format
        [{"role": "user", "content": "message_text"}, ...].

    Returns:
        Ok: If successful, returns Ok instance with the chat response value.
        Err: If an error occurs, returns Err instance with the error message.
    """
    with Session(engine) as db_session:
        statement = select(ChatSession).where(ChatSession.session_id == session_id)
        current_session = db_session.exec(statement).first()
        if current_session:
            statement = select(User).where(User.user_id == current_session.user_id)
            current_user = db_session.exec(statement).first()
            if current_user is None:
                return Err("User not found")

            # Calculate the elapsed time since the last request
            current_time = datetime.now()
            time_since_last_request = (
                    current_time - current_user.last_request_time).total_seconds()
            if time_since_last_request < min_time_between_requests:
                return Err(f"Minimum time between requests not met."
                           f"Please wait for {min_time_between_requests} seconds.")

            logger.info("ChatGPT response requested. Context: %s", messages)

            model, temperature = get_settings()

            # Check if there are enough tokens available for the request
            # (only using min_tokens_required instead of calculating api calls before hand,
            # because we don't know how many each api call will generate
            min_tokens_required = num_tokens_from_messages(messages, model) + 50
            logger.debug("min tokens required: %s", min_tokens_required)
            logger.debug("currently available: %s", current_user.available_tokens)
            if current_user.available_tokens >= min_tokens_required:
                # Update the last request time
                current_user.last_request_time = current_time

                # Make the API request
                logger.debug("using model: %s", model)
                logger.debug("using temperature: %s", temperature)
                completion = openai.ChatCompletion.create(model=model, messages=messages,
                                                          max_tokens=100, temperature=temperature)
                chat_response = completion.choices[0].message.content

                logger.info("ChatGPT response: %s", chat_response)

                # Update API token counters in the database
                current_user.api_prompt_tokens += completion.usage.prompt_tokens
                current_user.api_completion_tokens += completion.usage.completion_tokens
                current_user.api_total_tokens += completion.usage.total_tokens

                # Substract tokens from the bucket
                current_user.available_tokens = max(
                    current_user.available_tokens - completion.usage.total_tokens, 0)
                db_session.add(current_user)
                db_session.commit()

                return Ok(chat_response)

            # rate limit exceeded
            return Err("Rate limit exceeded.")
        return Err("No session found")


def num_tokens_from_string(string: str, model: str) -> int:
    """
    Returns the number of tokens in a text string.

    Args:
        string (str): The text string to count tokens in.
        model (str): model that is used for the token calculations.

    Returns:
        int: The number of tokens in the given string.
    """
    encoding = tiktoken.encoding_for_model(model)
    num_tokens = len(encoding.encode(string))
    return num_tokens


def num_tokens_from_messages(messages, model):
    """
    Returns the number of tokens used by a list of messages.

    Args:
        messages (list): List of messages in the format
        [{"role": "user", "content": "message_text"}, ...].
        model (str): model that is used for the token calculations.

    Returns:
        int: The number of tokens used by the messages.
    """
    num_tokens = 0
    for message in messages:
        num_tokens += 4  # every message follows <im_start>{role/name}\n{content}<im_end>\n
        for key, value in message.items():
            num_tokens += num_tokens_from_string(value, model)
            if key == "name":
                num_tokens += -1  # role is always required and always 1 token
    num_tokens += 2  # every reply is primed with <im_start>assistant
    return num_tokens
