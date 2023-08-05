from pydantic import BaseModel


class UserInformation(BaseModel):
    age: int
    gender: str
    occupation: str
    location: str
    language: str
    invite_code: str


class Message(BaseModel):
    content: str


class RuleResponse(BaseModel):
    name: str
    description: str
