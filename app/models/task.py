from sqlalchemy import Column
from sqlalchemy import Integer
from sqlalchemy import String
from sqlalchemy import Text
from sqlalchemy import ForeignKey
from sqlalchemy import DateTime
from sqlalchemy import Enum

from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from sqlalchemy import Boolean
from app.core.database import Base

from app.models.enums import TaskStatus


class Task(Base):

    __tablename__ = "tasks"


    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    title = Column(
        String,
        nullable=False
    )

    description = Column(
        Text,
        nullable=True
    )

    status = Column(
        Enum(TaskStatus),
        default=TaskStatus.PENDING,
        nullable=False
    )

    created_by = Column(
        Integer,
        ForeignKey("users.id"),
        nullable=False
    )

    assigned_to = Column(
        Integer,
        ForeignKey("users.id"),
        nullable=True
    )

    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now()
    )

    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now()
    )

    completion_processed = Column(
    Boolean,
    default=False,
    nullable=False
)

    creator = relationship(
        "User",
        foreign_keys=[created_by]
    )

    assignee = relationship(
        "User",
        foreign_keys=[assigned_to]
    )