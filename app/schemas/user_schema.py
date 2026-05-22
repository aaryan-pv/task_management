from pydantic import BaseModel
from datetime import datetime


class UserCreate(BaseModel):

    username: str

    email: str


class UserResponse(BaseModel):

    id: int

    username: str

    email: str

    is_active: bool

    created_at: datetime


    class Config:

        from_attributes = True