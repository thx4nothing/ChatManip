from fastapi import APIRouter, Request
from starlette.responses import RedirectResponse

from api_server.database import engine, User, ChatSession
from sqlmodel import Session, select

from api_server.models import UserInformation
from api_server.templates import templates

router = APIRouter()


# Route to serve the index.html template on root URL ("/")
@router.get("/")
async def read_root(request: Request):
    return templates.TemplateResponse("user_creation_base.html", {"request": request})


@router.post("/create_user")
async def create_user(user: UserInformation):
    with Session(engine) as db_session:
        statement = select(User).where(User.first_name == user.first_name).where(
            User.last_name == user.last_name).where(User.age == user.age)
        current_user = db_session.exec(statement).first()
        if current_user is None:
            new_user = User(first_name=user.first_name, last_name=user.last_name, age=user.age)
            db_session.add(new_user)
            db_session.commit()
            current_user = db_session.exec(statement).first()
            new_session = ChatSession(user_id=current_user.user_id)
            db_session.add(new_session)
            db_session.commit()
            statement = select(ChatSession).where(ChatSession.user_id == current_user.user_id)
            current_session = db_session.exec(statement).first()
            session_id = str(current_session.session_id)
            redirect_url = f"/session/{session_id}"
            print(redirect_url)
            return RedirectResponse(url=redirect_url, status_code=303)

    return RedirectResponse(url="/")
