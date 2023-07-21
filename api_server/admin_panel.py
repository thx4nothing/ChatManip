from typing import List

from fastapi import APIRouter, Request, HTTPException

from api_server.database import User, Persona, engine
from sqlmodel import Session, select

from api_server.templates import templates

router = APIRouter()


@router.get("/admin")
async def read_root(request: Request):
    return templates.TemplateResponse("admin_panel_base.html", {"request": request})


@router.get("/admin/users/", response_model=List[User])
async def list_users():
    with Session(engine) as db_session:
        statement = select(User)
        users = db_session.exec(statement).all()
        return users


@router.delete("/admin/users/delete/{user_id}/")
async def delete_user(user_id: int):
    with Session(engine) as db_session:
        statement = select(User).where(User.user_id == user_id)
        user = db_session.exec(statement).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        db_session.delete(user)
        db_session.commit()
        return {"message": "User deleted successfully"}


@router.get("/admin/personas/", response_model=List[Persona])
async def list_personas():
    with Session(engine) as db_session:
        statement = select(Persona)
        personas = db_session.exec(statement).all()
        return personas


# Route to create a new persona
@router.post("/admin/personas/", response_model=Persona)
async def create_persona(persona: Persona):
    with Session(engine) as db_session:
        new_persona = Persona(
            name=persona.name,
            system_instruction=persona.system_instruction,
            before_instruction=persona.before_instruction,
            after_instruction=persona.after_instruction
        )
        db_session.add(new_persona)
        db_session.commit()
        return persona


# Route to get a persona by ID
@router.get("/admin/personas/{persona_id}/", response_model=Persona)
async def get_persona(persona_id: int):
    with Session(engine) as db_session:
        statement = select(Persona).where(Persona.persona_id == persona_id)
        persona = db_session.exec(statement).first()
        if not persona:
            raise HTTPException(status_code=404, detail="Persona not found")
        return persona


# Route to update a persona by ID
@router.put("/admin/personas/{persona_id}/", response_model=Persona)
async def update_persona(persona_id: int, persona: Persona):
    with Session(engine) as db_session:
        existing_persona = db_session.get(Persona, persona_id)
        if not existing_persona:
            raise HTTPException(status_code=404, detail="Persona not found")

        persona_data = persona.dict(exclude_unset=True)
        for key, value in persona_data.items():
            setattr(existing_persona, key, value)

        db_session.add(existing_persona)
        db_session.commit()
        db_session.refresh(existing_persona)
        return existing_persona


# Route to delete a persona by ID
@router.delete("/admin/personas/{persona_id}/", response_model=dict)
async def delete_persona(persona_id: int):
    with Session(engine) as db_session:
        statement = select(Persona).where(Persona.persona_id == persona_id)
        persona = db_session.exec(statement).first()
        if not persona:
            raise HTTPException(status_code=404, detail="Persona not found")
        db_session.delete(persona)
        db_session.commit()
        return {"message": "Persona deleted successfully"}
