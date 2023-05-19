import os
import shutil
import uuid

from pathlib import Path
from pydub import AudioSegment
from typing import Annotated

from fastapi import APIRouter, Security, BackgroundTasks, UploadFile, Request, status, Form, HTTPException
from fastapi.responses import FileResponse
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from .dbaccessor import DBAccessor
from .models import UserCreate, User
from .auth import Auth


api = APIRouter()

security = HTTPBearer()
auth_handler = Auth()


async def wav_to_mp3(filename: Path):
    path_to_file, filename_and_ext = os.path.split(filename)
    fn = filename_and_ext.split(".")[0]

    new_file = os.path.join(path_to_file, fn + ".mp3")
    AudioSegment.from_wav(filename).export(new_file, format="mp3")
    os.remove(filename)


# User request to internal API
@api.post("/login")
async def qnt_questions(user: UserCreate) -> dict:
    access_token = auth_handler.encode_token(user.username)
    db_accessor = DBAccessor()
    cur_user: User = await db_accessor.save_user_to_db(user, access_token)
    return {"uuid": cur_user.user_id, "access_token": access_token, }


# Uploading wav-file to server
@api.post("/record")
async def add_track(r: Request, user_id: Annotated[str, Form()], upload_file: UploadFile,
                    background_tasks: BackgroundTasks, credentials: HTTPAuthorizationCredentials = Security(security)):
    token = credentials.credentials
    user_id = uuid.UUID(user_id)
    if auth_handler.decode_token(token):
        db_accessor = DBAccessor()
        filename = await db_accessor.save_track_to_db(user_id)

        try:
            my_path = os.path.join(os.getcwd(), "app", "tracks", filename + ".wav")
            with open(my_path, "wb") as tmp:
                shutil.copyfileobj(upload_file.file, tmp)
                tmp_path = Path(tmp.name)
        finally:
            upload_file.file.close()
        # convert wav to mp3 file
        background_tasks.add_task(wav_to_mp3, tmp_path)
        # http://host:port/record?id=id_записи&user=id_пользователя.
        return {"url": f"{r.url}?id={filename}&user={user_id}"}
    else:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Invalid Token"
        )


# Downloading mp3 file from server
@api.get("/record")
async def response_file(id: uuid.UUID, user: uuid.UUID):
    db_accessor = DBAccessor()
    valid = await db_accessor.get_tracks_for_user(id, user)
    if valid:
        return FileResponse(os.path.join(os.getcwd(), "app", "tracks", str(id) + ".mp3"),
                            filename="bewise.mp3",
                            media_type="application/octet-stream")
    else:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Incorrect data"
        )
