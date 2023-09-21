import random
import string
from typing import List

from fastapi import Query, HTTPException, APIRouter
from sqlmodel import Session, select

from api_server.database import engine, InviteCode
from .auth import check_authentication
from .common import list_entities
from ..logger import logger as logger

router = APIRouter()


@router.post("")
async def generate_invite_codes(num_codes: int = 1, token: str = Query(...)):
    await check_authentication(token)
    with Session(engine) as db_session:
        invite_codes = []
        for _ in range(num_codes):
            new_invite_code_str = generate_invite_code()
            new_invite_code = InviteCode(invite_code=new_invite_code_str)
            db_session.add(new_invite_code)
            invite_codes.append(new_invite_code_str)
        db_session.commit()
        return invite_codes


@router.get("", response_model=List[InviteCode])
async def list_invite_codes(token: str = Query(...)):
    return await list_entities(InviteCode, token)


@router.delete("/{invite_code}", response_model=InviteCode)
async def delete_invite_code(invite_code: str, token: str = Query(...)):
    await check_authentication(token)
    with Session(engine) as db_session:
        statement = select(InviteCode).where(InviteCode.invite_code == invite_code)
        invite_code_obj = db_session.exec(statement).first()
        if not invite_code_obj:
            raise HTTPException(status_code=404, detail="Invite code not found")
        db_session.delete(invite_code_obj)
        db_session.commit()
        return invite_code_obj


@router.patch("/{invite_code}", response_model=InviteCode)
async def update_invite_code(invite_code: str, persona_id: int, task_id: int, rules: str,
                             next_session_id: str, history_id: int, multi_use: bool,
                             token: str = Query(...)):
    await check_authentication(token)
    with Session(engine) as db_session:
        invite_code_obj = db_session.get(InviteCode, invite_code)
        if not invite_code_obj:
            raise HTTPException(status_code=404, detail="Invite code not found")
        if persona_id >= 0:
            invite_code_obj.persona_id = persona_id
        if task_id >= 0:
            invite_code_obj.task_id = task_id
        if history_id >= 0:
            invite_code_obj.history_id = history_id
        invite_code_obj.rules = rules
        invite_code_obj.next_session_id = next_session_id
        invite_code_obj.multi_use = multi_use
        db_session.add(invite_code_obj)
        db_session.commit()
        db_session.refresh(invite_code_obj)
        return invite_code_obj


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
    logger.debug("Created a new Invite code: %s", invite_code)
    return invite_code
