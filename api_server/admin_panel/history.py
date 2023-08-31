import json
from typing import List

from fastapi import APIRouter, Query, UploadFile, File, HTTPException
from sqlmodel import Session, select

from api_server.database import engine, History
from .auth import check_authentication
from .common import list_entities

router = APIRouter()


@router.get("/export")
async def export_histories_database(token: str = Query(...)):
    await check_authentication(token)
    with Session(engine) as db_session:
        statement = select(History)
        histories = db_session.exec(statement).all()
        history_data = [{"name": history.name,
                         "history": history.history} for history in histories]
        return history_data


@router.post("/import")
async def import_histories_database(file: UploadFile = File(...), token: str = Query(...)):
    await check_authentication(token)
    data = await file.read()
    histories_to_import = json.loads(data)

    with Session(engine) as db_session:
        for imported_history in histories_to_import:
            history = History(**imported_history)
            db_session.add(history)
        db_session.commit()
        return {"message": "Import successful"}


@router.get("/", response_model=List[History])
async def list_histories(token: str = Query(...)):
    return await list_entities(History, token)


@router.post("/", response_model=History)
async def create_history(history: History, token: str = Query(...)):
    await check_authentication(token)
    with Session(engine) as db_session:
        new_history = History(name=history.name, history=history.history)
        db_session.add(new_history)
        db_session.commit()
        return history


@router.get("/{history_id}/", response_model=History)
async def get_history(history_id: int, token: str = Query(...)):
    await check_authentication(token)
    with Session(engine) as db_session:
        statement = select(History).where(History.history_id == history_id)
        history = db_session.exec(statement).first()
        if not history:
            raise HTTPException(status_code=404, detail="History not found")
        return history


@router.put("/{history_id}/", response_model=History)
async def update_history(history_id: int, history: History, token: str = Query(...)):
    await check_authentication(token)
    with Session(engine) as db_session:
        statement = select(History).where(History.history_id == history_id)
        existing_history = db_session.exec(statement).first()
        if not existing_history:
            raise HTTPException(status_code=404, detail="History not found")

        history_data = history.dict(exclude_unset=True)
        for key, value in history_data.items():
            setattr(existing_history, key, value)

        db_session.add(existing_history)
        db_session.commit()
        db_session.refresh(existing_history)
        return existing_history


@router.delete("/{history_id}/", response_model=dict)
async def delete_history(history_id: int, token: str = Query(...)):
    await check_authentication(token)
    with Session(engine) as db_session:
        statement = select(History).where(History.history_id == history_id)
        history = db_session.exec(statement).first()
        if not history:
            raise HTTPException(status_code=404, detail="History not found")
        db_session.delete(history)
        db_session.commit()
        return {"message": "History deleted successfully"}
