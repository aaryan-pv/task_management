from sqlalchemy.orm import Session

from app.models.user import User


class UserRepository:


    @staticmethod
    def create_user(
        db: Session,
        user_data: dict
    ):

        """ Create user """

        user = User(**user_data)

        db.add(user)

        db.commit()

        db.refresh(user)

        return user


    @staticmethod
    def get_user_by_id(
        db: Session,
        user_id: int
    ):

        """ Fetch user by id """

        return db.query(User).filter(
            User.id == user_id
        ).first()


    @staticmethod
    def get_user_by_email(
        db: Session,
        email: str
    ):

        """ Fetch user by email """

        return db.query(User).filter(
            User.email == email
        ).first()


    @staticmethod
    def list_users(
        db: Session
    ):

        """ List all users """

        return db.query(User).all()


    @staticmethod
    def delete_user(
        db: Session,
        user
    ):

        """ Delete user """

        db.delete(user)

        db.commit()