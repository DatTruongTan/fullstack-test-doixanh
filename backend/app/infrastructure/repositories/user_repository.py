from sqlalchemy.orm import Session
from app.security import get_password_hash, verify_password
from app.domain.models.user import User
from app.application.schemas.user import UserCreate
from app.domain.repositories.user_repository import IUserRepository

class UserRepository(IUserRepository):
    def __init__(self, db: Session):
        self.db = db

    def get_user_by_email(self, email: str) -> User | None:
        """Get a user by their email.

        Args:
            email (str): The email of the user to get.

        Returns:
            User | None: The user.
        """
        return self.db.query(User).filter(User.email == email).first()

    def get_user_by_username(self, username: str) -> User | None:
        """Get a user by their username.

        Args:
            username (str): The username of the user to get.

        Returns:
            User | None: The user.
        """
        return self.db.query(User).filter(User.username == username).first()

    def create_user(self, user: UserCreate) -> User:
        """Create a new user.

        Args:
            user (UserCreate): The user to create.

        Returns:
            User: The created user.
        """
        hashed_password = get_password_hash(user.password)
        db_user = User(
            email=user.email,
            username=user.username,
            hashed_password=hashed_password
        )
        self.db.add(db_user)
        self.db.commit()
        self.db.refresh(db_user)
        return db_user

    def authenticate_user(self, username: str, password: str) -> User | None:
        """Authenticate a user.

        Args:
            username (str): The username of the user to authenticate.
            password (str): The password of the user to authenticate.

        Returns:
            User | None: The authenticated user.
        """
        user = self.get_user_by_username(username)
        if not user or not verify_password(password, user.hashed_password):
            return None
        return user