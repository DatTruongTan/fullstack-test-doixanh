from fastapi import HTTPException, status
from app.domain.repositories.user_repository import IUserRepository
from app.application.schemas.user import UserCreate
from app.domain.models.user import User

class AuthService:
    def __init__(self, user_repository: IUserRepository):
        self.user_repository = user_repository

    def register_user(self, user: UserCreate) -> User:
        """Register a new user.

        Args:
            user (UserCreate): The user to register.

        Raises:
            HTTPException: If the email or username is already taken.

        Returns:
            User: The registered user.
        """
        db_user = self.user_repository.get_user_by_email(email=user.email)
        if db_user:
            raise HTTPException(status_code=400, detail="Email already registered")
        
        db_user = self.user_repository.get_user_by_username(username=user.username)
        if db_user:
            raise HTTPException(status_code=400, detail="Username already taken")
            
        return self.user_repository.create_user(user=user)

    def login_user(self, username: str, password: str) -> User:
        """Login a user.

        Args:
            username (str): The username of the user to login.
            password (str): The password of the user to login.

        Returns:
            User: The logged in user.
        """
        user = self.user_repository.authenticate_user(username, password)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect username or password",
                headers={"WWW-Authenticate": "Bearer"},
            )
        return user 