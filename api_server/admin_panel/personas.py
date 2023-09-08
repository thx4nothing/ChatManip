import json
from typing import List

from fastapi import Query, HTTPException, UploadFile, File, APIRouter
from sqlmodel import Session, select

from api_server.database import Persona, engine
from .auth import check_authentication
from .common import list_entities

router = APIRouter()


@router.get("/", response_model=List[Persona])
async def list_personas(token: str = Query(...)):
    return await list_entities(Persona, token)


@router.post("/", response_model=Persona)
async def create_persona(persona: Persona, token: str = Query(...)):
    await check_authentication(token)
    with Session(engine) as db_session:
        new_persona = Persona(
            name=persona.name,
            system_instruction=persona.system_instruction,
            first_message=persona.first_message,
            before_instruction=persona.before_instruction,
            after_instruction=persona.after_instruction
        )

        if not does_persona_exist(db_session, new_persona):
            db_session.add(new_persona)
            db_session.commit()
        return persona


@router.get("/export/")
async def export_persona_database(token: str = Query(...)):
    print(token)
    await check_authentication(token)
    with Session(engine) as db_session:
        statement = select(Persona)
        personas = db_session.exec(statement).all()
        persona_data = [{"name": persona.name,
                         "system_instruction": persona.system_instruction,
                         "first_message": persona.first_message,
                         "before_instruction": persona.before_instruction,
                         "after_instruction": persona.after_instruction} for persona in personas]
        print(persona_data)
        return persona_data


@router.post("/import/")
async def import_persona_database(file: UploadFile = File(...), token: str = Query(...)):
    await check_authentication(token)
    data = await file.read()
    personas_to_import = json.loads(data)

    with Session(engine) as db_session:
        for imported_persona in personas_to_import:
            persona = Persona(**imported_persona)
            if not does_persona_exist(db_session, persona):
                db_session.add(persona)
        db_session.commit()
        return {"message": "Import successful"}


@router.get("/{persona_id}/", response_model=Persona)
async def get_persona(persona_id: int, token: str = Query(...)):
    await check_authentication(token)
    with Session(engine) as db_session:
        statement = select(Persona).where(Persona.persona_id == persona_id)
        persona = db_session.exec(statement).first()
        if not persona:
            raise HTTPException(status_code=404, detail="Persona not found")
        return persona


@router.put("/{persona_id}/", response_model=Persona)
async def update_persona(persona_id: int, persona: Persona, token: str = Query(...)):
    await check_authentication(token)
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


@router.delete("/{persona_id}/", response_model=dict)
async def delete_persona(persona_id: int, token: str = Query(...)):
    await check_authentication(token)
    with Session(engine) as db_session:
        statement = select(Persona).where(Persona.persona_id == persona_id)
        persona = db_session.exec(statement).first()
        if not persona:
            raise HTTPException(status_code=404, detail="Persona not found")
        db_session.delete(persona)
        db_session.commit()
        return {"message": "Persona deleted successfully"}


def does_persona_exist(db_session: Session, new_persona: Persona) -> bool:
    statement = select(Persona).filter(Persona.name == new_persona.name)
    existing_personas = db_session.exec(statement).all()

    for existing_persona in existing_personas:
        if (existing_persona.system_instruction == new_persona.system_instruction and
                existing_persona.before_instruction == new_persona.before_instruction and
                existing_persona.after_instruction == new_persona.after_instruction):
            return True
    return False
