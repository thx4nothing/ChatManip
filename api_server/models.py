from pydantic import BaseModel


class UserInformation(BaseModel):
    first_name: str
    last_name: str
    age: int


class Message(BaseModel):
    content: str
