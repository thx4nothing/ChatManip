"""
Module: main

This module initializes the FastAPI application and configures routing for various parts
of the application, including chat, user creation, questionnaire, and admin panel.

Functions:
    on_startup: Function to be executed during application startup to create SQLModel metadata.

Usage:
    Run this module to start the FastAPI application and set up
    routing for different parts of the application.

Author: Marlon Beck
Date: 17/08/2023
"""
import os

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from sqlmodel import SQLModel

from api_server import chat, database, user_creation, questionnaire
from api_server.admin_panel import router as admin_panel_router

debug = os.getenv("CHATMANIP_DEBUG").lower() == "true"

# Create the FastAPI app
if debug:
    print("Running in DEBUG mode!")
    app = FastAPI()
else:
    print("Running in PRODUCTION mode!")
    app = FastAPI(
        docs_url=None,  # Disable docs (Swagger UI)
        redoc_url=None,  # Disable redoc
    )

# Mount static files directory to serve CSS and JavaScript files
# app.mount("/static", StaticFiles(directory="static"), name="static")
app.mount("/chatmanip/static", StaticFiles(directory="static"), name="static")

# Route the functions to the main app
app.include_router(admin_panel_router, prefix="/admin", tags=["admin"])
app.include_router(chat.router, prefix="/chat", tags=["chat"])
app.include_router(questionnaire.router, prefix="/questionnaire", tags=["questionnaire"])
app.include_router(user_creation.router)


@app.on_event("startup")
def on_startup():
    """
    Function to be executed during application startup to create SQLModel metadata.
    """
    SQLModel.metadata.create_all(database.engine)
