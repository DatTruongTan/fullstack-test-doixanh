from abc import ABC, abstractmethod
from typing import Optional
from app.domain.models.user import User
from app.application.schemas.user import UserCreate

class IUserRepository(ABC):
    @abstractmethod
    def get_user_by_email(self, email: str) -> Optional[User]:
        pass

    @abstractmethod
    def get_user_by_username(self, username: str) -> Optional[User]:
        pass

    @abstractmethod
    def create_user(self, user: UserCreate) -> User:
        pass

    @abstractmethod
    def authenticate_user(self, username: str, password: str) -> Optional[User]:
        pass 