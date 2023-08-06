import os
import openai

from datetime import datetime
from sqlmodel import Session, select
from api_server.database import engine, User, ChatSession


# Error Classes
class Ok:
    def __init__(self, value):
        self.value = value


class Err:
    def __init__(self, error_message):
        self.error_message = error_message


# OpenAI Init
openai.api_key = os.getenv("OPENAI_API_KEY")

# rate limits

bucket_capacity: int = 500
token_rate: float = 0.5
min_time_between_requests: float = 2.0
min_tokens_required = 100


def request_system_response(messages: list[dict[str, str]]) -> str:
    # Make the API request
    completion = openai.ChatCompletion.create(model="gpt-3.5-turbo", messages=messages)
    chat_response = completion.choices[0].message.content

    return chat_response


def request_response(session_id: str, messages: list[dict[str, str]]):
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
            time_since_last_request = (current_time - current_user.last_request_time).total_seconds()
            if time_since_last_request < min_time_between_requests:
                return Err(
                    f"Minimum time between requests not met. Please wait for {min_time_between_requests} seconds.")

            # Calculate the number of tokens that should be added based on the elapsed time
            tokens_to_add = token_rate * time_since_last_request

            # Update the available tokens in the bucket
            current_user.available_tokens = min(current_user.available_tokens + tokens_to_add, bucket_capacity)

            # Check if there are enough tokens available for the request
            # (only using min_tokens_required instead of calculating api calls before hand,
            # because we don't know how many each api call will generate
            if current_user.available_tokens >= min_tokens_required:
                # Update the last request time
                current_user.last_request_time = current_time

                # Make the API request
                completion = openai.ChatCompletion.create(model="gpt-3.5-turbo", messages=messages)
                chat_response = completion.choices[0].message.content

                # Update API token counters in the database
                current_user.api_prompt_tokens += completion.usage.prompt_tokens
                current_user.api_completion_tokens += completion.usage.completion_tokens
                current_user.api_total_tokens += completion.usage.total_tokens

                # Substract tokens from the bucket
                current_user.available_tokens = max(current_user.available_tokens - completion.usage.total_tokens, 0)
                db_session.add(current_user)
                db_session.commit()

                return Ok(chat_response)
            else:
                # rate limit exceeded
                return Err("Rate limit exceeded. Please wait before making another request.")
