import json
from typing import List

from fastapi import APIRouter, Query, UploadFile, File, HTTPException
from sqlmodel import Session, select

from api_server.database import engine, Task
from .auth import check_authentication
from .common import list_entities

router = APIRouter()


@router.get("/export")
async def export_tasks_database(token: str = Query(...)):
    await check_authentication(token)
    with Session(engine) as db_session:
        statement = select(Task)
        tasks = db_session.exec(statement).all()
        task_data = [{"name": task.name,
                      "task_instruction": task.task_instruction} for task in tasks]
        return task_data


@router.post("/import")
async def import_tasks_database(file: UploadFile = File(...), token: str = Query(...)):
    await check_authentication(token)
    data = await file.read()
    tasks_to_import = json.loads(data)

    with Session(engine) as db_session:
        for imported_task in tasks_to_import:
            task = Task(**imported_task)
            db_session.add(task)
        db_session.commit()
        return {"message": "Import successful"}


@router.get("/", response_model=List[Task])
async def list_tasks(token: str = Query(...)):
    return await list_entities(Task, token)


@router.post("/", response_model=Task)
async def create_task(task: Task, token: str = Query(...)):
    await check_authentication(token)
    with Session(engine) as db_session:
        new_task = Task(name=task.name, task_instruction=task.task_instruction)
        db_session.add(new_task)
        db_session.commit()
        return task


@router.get("/{task_id}/", response_model=Task)
async def get_task(task_id: int, token: str = Query(...)):
    await check_authentication(token)
    with Session(engine) as db_session:
        statement = select(Task).where(Task.task_id == task_id)
        task = db_session.exec(statement).first()
        if not task:
            raise HTTPException(status_code=404, detail="Task not found")
        return task


@router.put("/{task_id}/", response_model=Task)
async def update_task(task_id: int, task: Task, token: str = Query(...)):
    await check_authentication(token)
    with Session(engine) as db_session:
        statement = select(Task).where(Task.task_id == task_id)
        existing_task = db_session.exec(statement).first()
        if not existing_task:
            raise HTTPException(status_code=404, detail="Task not found")

        task_data = task.dict(exclude_unset=True)
        for key, value in task_data.items():
            setattr(existing_task, key, value)

        db_session.add(existing_task)
        db_session.commit()
        db_session.refresh(existing_task)
        return existing_task


@router.delete("/{task_id}/", response_model=dict)
async def delete_task(task_id: int, token: str = Query(...)):
    await check_authentication(token)
    with Session(engine) as db_session:
        statement = select(Task).where(Task.task_id == task_id)
        task = db_session.exec(statement).first()
        if not task:
            raise HTTPException(status_code=404, detail="Task not found")
        db_session.delete(task)
        db_session.commit()
        return {"message": "Task deleted successfully"}
