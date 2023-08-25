from fastapi import Query, APIRouter
from sqlmodel import Session, select

from api_server.database import engine, Settings
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
    print(type(temperature))
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
