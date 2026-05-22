from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):

    DATABASE_URL: str

    APP_NAME: str = "Task Management API"

    APP_VERSION: str = "1.0.0"
    REDIS_HOST: str
    REDIS_PORT: int
    REDIS_DB: int
    

    DEBUG: bool = True


    class Config:

        env_file = ".env"


@lru_cache
def get_settings():

    return Settings()


settings = get_settings()