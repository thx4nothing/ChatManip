from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from sqlmodel import SQLModel

from api_server import chat, database, user_creation
from api_server.admin_panel import router as admin_panel_router

# Create the FastAPI app
app = FastAPI()

# Mount static files directory to serve CSS and JavaScript files
app.mount("/static", StaticFiles(directory="static"), name="static")

# Route the functions to the main app
app.include_router(admin_panel_router, prefix="/admin", tags=["admin"])
app.include_router(chat.router, prefix="/chat", tags=["chat"])
app.include_router(user_creation.router)


# app.include_router(security.router)


@app.on_event("startup")
def on_startup():
    SQLModel.metadata.create_all(database.engine)
