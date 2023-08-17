from typing import List

from fastapi import Query, HTTPException, APIRouter
from sqlmodel import Session, select

from api_server.database import User, engine
from .auth import check_authentication
from .common import list_entities

router = APIRouter()


@router.get("/", response_model=List[User])
async def list_users(token: str = Query(...)):
    return await list_entities(User, token)


@router.delete("/delete/{user_id}/")
async def delete_user(user_id: int, token: str = Query(...)):
    await check_authentication(token)
    with Session(engine) as db_session:
        statement = select(User).where(User.user_id == user_id)
        user = db_session.exec(statement).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        db_session.delete(user)
        db_session.commit()
        return {"message": "User deleted successfully"}
