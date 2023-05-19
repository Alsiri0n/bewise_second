import uuid

from sqlalchemy import select, desc, and_
from sqlalchemy.orm import subqueryload
from sqlalchemy.engine import Result

from .database import db
from .models import User, UserModel, UserCreate, TrackModel


# Helper for work with DB and keeping query for db
class DBAccessor:
    async def save_user_to_db(self, u: UserCreate, token: str) -> User:
        user_model = UserModel(user_id=uuid.uuid1(), username=u.username, token=token)
        async with db.session() as session:
            async with session.begin():
                session.add(user_model)
                await session.commit()
            q = select(UserModel).\
                where(UserModel.token == token).\
                options(subqueryload(UserModel.tracks))
            result: Result = await session.execute(q)
        user_model_full: UserModel = result.scalar()
        user: User = user_model_full.to_dc()
        return user

    async def save_track_to_db(self, u: uuid.UUID) -> str:
        filename = uuid.uuid1()
        track_model = TrackModel(track_id=filename, user_id=u)
        async with db.session() as session:
            async with session.begin():
                session.add(track_model)
            await session.commit()
        return str(filename)

    async def get_tracks_for_user(self, track_id: uuid.UUID, user_id: uuid.UUID) -> bool:
        full_result = False
        async with db.session() as session:
            q = select(UserModel). \
                where(UserModel.user_id == user_id). \
                options(subqueryload(UserModel.tracks))
            result: Result = await session.execute(q)
            user_model_full: UserModel = result.scalar()
            if user_model_full:
                q = select(TrackModel). \
                    where(and_(TrackModel.user_id == user_id, TrackModel.track_id == track_id))
                result: Result = await session.execute(q)
                track_model: UserModel = result.scalar()
                if track_model:
                    full_result = True
            else:
                return full_result
        return full_result
