from functools import lru_cache
from pydantic import BaseSettings


# Loading data from config file
class Settings(BaseSettings):
    database_host: str
    database_port: int
    database_user: str
    database_password: str
    database_name: str

    class Config:
        env_file = ".env"


# Saving environment variables in cache
@lru_cache()
def get_settings() -> Settings:
    return Settings()
