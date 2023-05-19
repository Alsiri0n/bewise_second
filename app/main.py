from fastapi import FastAPI, status, Request
from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

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

@Application.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content=jsonable_encoder({"detail": exc.errors(), "body": exc.body}),
    )