from pydantic import BaseModel, Field
from dataclasses import dataclass, field
from sqlalchemy import BigInteger, Column, Text, Boolean, ForeignKey
from sqlalchemy.orm import declarative_base, relationship
from sqlalchemy.dialects.postgresql import UUID as pgUUID
import uuid

Base = declarative_base()

# Pydantic model for creating user
class UserCreate(BaseModel):
    username: str = Field(min_length=1)
    user_id: uuid.UUID | None = None
    disabled: bool = False


# Dataclass model for user
@dataclass
class User:
    user_id: uuid.UUID
    username: str
    token: str
    disabled: bool

    tracks: list["Track"] = field(default_factory=list)


# Dataclass model for track
@dataclass
class Track:
    track_id: uuid.UUID

    user_id: uuid.UUID


# ORM model for User
class UserModel(Base):
    __tablename__ = "users"

    id = Column(BigInteger, primary_key=True)
    user_id = Column(pgUUID(as_uuid=True), unique=True)
    username = Column(Text)
    token = Column(Text)
    disabled = Column(Boolean, default=False)

    tracks = relationship("TrackModel", back_populates="user", cascade="all, delete")

    def to_dc(self) -> User:
        return User(user_id=self.user_id,
                    username=str(self.username),
                    token=str(self.token),
                    disabled=bool(self.disabled),
                    tracks=[track.to_dc() for track in self.tracks])


# ORM model for Track
class TrackModel(Base):
    __tablename__ = "tracks"

    id = Column(BigInteger, primary_key=True)
    track_id = Column(pgUUID)

    user_id = Column(pgUUID(as_uuid=True), ForeignKey("users.user_id", ondelete="CASCADE"))
    user = relationship("UserModel", back_populates="tracks")

    def to_dc(self) -> Track:
        return Track(
            track_id=uuid.UUID(str(self.track_id)),
            user_id=uuid.UUID(str(self.user_id)),
        )
