import datetime
import os
import shutil
from pathlib import Path

from fastapi import Query, APIRouter
from fastapi.responses import FileResponse
from sqlmodel import Session, select, SQLModel

from api_server.database import engine, Settings
from api_server.logger import logger as logger
from .auth import check_authentication

router = APIRouter()


@router.get("/temperature")
async def read_temperature(token: str = Query(...)):
    await check_authentication(token)
    with Session(engine) as db_session:
        statement = select(Settings)
        settings = db_session.exec(statement).first()
        if settings:
            return settings.temperature
        else:
            return 1.0


@router.post("/temperature")
async def set_temperature(settings: dict, token: str = Query(...)):
    await check_authentication(token)
    temperature = settings["temperature"]
    if 0.0 <= temperature <= 2.0:
        with Session(engine) as db_session:
            statement = select(Settings)
            settings = db_session.exec(statement).first()
            if settings:
                settings.temperature = temperature
            else:
                settings = Settings(temperature=temperature)

            db_session.add(settings)
            db_session.commit()


@router.get("/model")
async def read_model(token: str = Query(...)):
    await check_authentication(token)
    with Session(engine) as db_session:
        statement = select(Settings)
        settings = db_session.exec(statement).first()
        model = ""
        if settings:
            model = settings.model
        else:
            model = "gpt-3.5-turbo"
        print(model)
        return model


@router.post("/model")
async def set_model(settings: dict, token: str = Query(...)):
    await check_authentication(token)
    model = settings["model"]
    if model in ("gpt-3.5-turbo", "gpt-4"):
        with Session(engine) as db_session:
            statement = select(Settings)
            settings = db_session.exec(statement).first()
            if settings:
                settings.model = model
            else:
                settings = Settings(model=model)

            db_session.add(settings)
            db_session.commit()


@router.get("/database/download")
async def download_database(token: str = Query(...)):
    await check_authentication(token)

    database_file_path = Path("data/database.sqlite")
    if database_file_path.exists():
        return FileResponse(database_file_path, headers={
            "Content-Disposition": "attachment; filename=data/database.sqlite"})
    return {"error": "Database file not found"}


def backup_database():
    try:
        current_datetime = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        backup_directory = "data/database_backups"
        if not os.path.exists(backup_directory):
            os.makedirs(backup_directory)
        backup_file_path = os.path.join(backup_directory, f"database_{current_datetime}.sqlite")
        shutil.copyfile('data/database.sqlite', backup_file_path)

        print(f"Database backup completed successfully to {backup_file_path}")
    except Exception as e:
        print(f"Error during database backup: {str(e)}")


def reset_database():
    SQLModel.metadata.drop_all(engine)
    SQLModel.metadata.create_all(engine)


@router.post("/database/reset")
async def request_reset_database(token: str = Query(...)):
    await check_authentication(token)
    try:
        logger.warning("Requested to reset database. Making backup before resetting.")

        backup_database()
        reset_database()

        logger.warning("Database reset completed successfully.")

        return {"message": "Database reset completed successfully."}

    except Exception as e:
        logger.error(f"Error resetting the database: {str(e)}")
        return {"message": f"Error resetting the database: {str(e)}"}
