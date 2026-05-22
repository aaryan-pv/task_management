from fastapi import FastAPI

from app.core.database import Base
from app.core.database import engine

from app.models.user import User
from app.models.task import Task

from app.api.routes.task_routes import (
    router as task_router
)

from app.api.routes.user_routes import (
    router as user_router
)

from app.core.config import settings


Base.metadata.create_all(bind=engine)


app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION
)


app.include_router(task_router)

app.include_router(user_router)


@app.get("/")
def health_check():

    return {
        "message": "API running"
    }