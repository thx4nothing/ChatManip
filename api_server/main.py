from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from api_server import admin_panel, chat, database, user_creation
from sqlmodel import SQLModel

# Create the FastAPI app
app = FastAPI()

# Mount static files directory to serve CSS and JavaScript files
app.mount("/static", StaticFiles(directory="static"), name="static")

# Route the functions to the main app
app.include_router(admin_panel.router)
app.include_router(chat.router)
app.include_router(user_creation.router)


@app.on_event("startup")
def on_startup():
    SQLModel.metadata.create_all(database.engine)

# openai.api_key = os.getenv("OPENAI_API_KEY")
# openai.Model.list()
