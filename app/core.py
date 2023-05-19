from fastapi import FastAPI

from .config import Settings
from .database import db


# Auxiliary function for db work
def create_start_app_handler(
    app: FastAPI,
    settings: Settings,
):
    async def start_app() -> None:
        await db.connect(app, settings)

    return start_app


# Auxiliary function for db work
def create_stop_app_handler(app: FastAPI):
    async def stop_app() -> None:
        await db.disconnect()

    return stop_app
