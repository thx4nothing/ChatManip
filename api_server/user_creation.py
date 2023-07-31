from fastapi import APIRouter, Request, HTTPException
from starlette.responses import RedirectResponse

from api_server.database import engine, User, ChatSession, InviteCode, generate_invite_code
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
        statement = select(InviteCode).where(InviteCode.invite_code == user.invite_code)
        invite_code_obj = db_session.exec(statement).first()
        if not invite_code_obj:
            raise HTTPException(status_code=404, detail="Invite code not found")
        if invite_code_obj.used:
            raise HTTPException(status_code=404, detail="Invite already in use")

        statement = select(User).where(User.first_name == user.first_name).where(
            User.last_name == user.last_name).where(User.age == user.age)
        current_user = db_session.exec(statement).first()
        if current_user is None:
            new_user = User(first_name=user.first_name, last_name=user.last_name, age=user.age)
            db_session.add(new_user)
            db_session.commit()
            current_user = db_session.exec(statement).first()
            new_invite_code_str = user.invite_code
            new_session = ChatSession(session_id=new_invite_code_str, user_id=current_user.user_id,
                                      persona_id=invite_code_obj.persona_id,
                                      rules=invite_code_obj.rules)
            db_session.add(new_session)
            db_session.commit()

            invite_code_obj.used = True
            invite_code_obj.user_id = current_user.user_id
            db_session.add(invite_code_obj)
            db_session.commit()

            statement = select(ChatSession).where(ChatSession.user_id == current_user.user_id)
            current_session = db_session.exec(statement).first()
            session_id = str(current_session.session_id)
            redirect_url = f"/session/{session_id}"
            print(redirect_url)
            return RedirectResponse(url=redirect_url, status_code=303)

    return RedirectResponse(url="/")
