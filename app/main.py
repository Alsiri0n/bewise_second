from fastapi import FastAPI

from .config import get_settings
from .core import create_stop_app_handler, create_start_app_handler
from .views import api


# Main class for run application
def init_app():
    settings = get_settings()

    cur_app = FastAPI()
    cur_app.add_event_handler(
        "startup",
        create_start_app_handler(cur_app, settings),
    )
    cur_app.add_event_handler(
        "shutdown",
        create_stop_app_handler(cur_app),
    )

    cur_app.include_router(api)

    return cur_app


Application = init_app()
