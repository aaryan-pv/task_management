from sqlalchemy.orm import Session

from app.repositories.user_repository import (
    UserRepository
)

from app.utils.exceptions import (
    NotFoundException,
    BadRequestException
)

from app.utils.logger import logger


class UserService:


    @staticmethod
    def create_user(
        db: Session,
        payload
    ):

        logger.info(
            f"Creating user email={payload.email}"
        )

        existing_user = (
            UserRepository.get_user_by_email(
                db,
                payload.email
            )
        )

        if existing_user:

            raise BadRequestException(
                detail="Email already exists"
            )

        return UserRepository.create_user(
            db=db,
            user_data=payload.model_dump()
        )


    @staticmethod
    def get_user(
        db: Session,
        user_id: int
    ):

        logger.info(
            f"Fetching user_id={user_id}"
        )

        user = UserRepository.get_user_by_id(
            db,
            user_id
        )

        if not user:

            raise NotFoundException(
                detail="User not found"
            )

        return user


    @staticmethod
    def list_users(
        db: Session
    ):

        logger.info(
            "Listing users"
        )

        return UserRepository.list_users(db)


    @staticmethod
    def delete_user(
        db: Session,
        user_id: int
    ):

        logger.info(
            f"Deleting user_id={user_id}"
        )

        user = UserRepository.get_user_by_id(
            db,
            user_id
        )

        if not user:

            raise NotFoundException(
                detail="User not found"
            )

        UserRepository.delete_user(
            db,
            user
        )

        return {
            "message": "User deleted successfully"
        }