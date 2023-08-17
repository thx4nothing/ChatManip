from typing import Type, Any

from fastapi import Query
from sqlmodel import Session, select

from api_server.database import engine
from .auth import check_authentication


async def list_entities(entity_type: Type[Any], token: str = Query(...)):
    await check_authentication(token)
    with Session(engine) as db_session:
        statement = select(entity_type)
        entities = db_session.exec(statement).all()
        return entities
