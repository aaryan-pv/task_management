from fastapi import APIRouter
from fastapi import Depends

from sqlalchemy.orm import Session

from app.core.database import get_db

from app.schemas.user_schema import (
    UserCreate,
    UserResponse
)

from app.services.user_service import (
    UserService
)


router = APIRouter(
    prefix="/users",
    tags=["Users"]
)


@router.post(
    "/",
    response_model=UserResponse
)
def create_user(
    payload: UserCreate,
    db: Session = Depends(get_db)
):

    return UserService.create_user(
        db,
        payload
    )


@router.get(
    "/{user_id}",
    response_model=UserResponse
)
def get_user(
    user_id: int,
    db: Session = Depends(get_db)
):

    return UserService.get_user(
        db,
        user_id
    )