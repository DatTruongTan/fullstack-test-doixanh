from typing import Generator, Optional

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from sqlalchemy.orm import Session

from app.infrastructure.db.session import SessionLocal
from app.domain.models.user import User
from app.application.schemas.token import TokenData
from app import security
from app.config import settings
from app.domain.repositories.user_repository import IUserRepository
from app.infrastructure.repositories.user_repository import UserRepository
from app.domain.repositories.task_repository import ITaskRepository
from app.infrastructure.repositories.task_repository import TaskRepository
from app.application.services.auth_service import AuthService
from app.application.services.task_service import TaskService

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/token")

def get_db() -> Generator:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def get_user_repository(db: Session = Depends(get_db)) -> IUserRepository:
    return UserRepository(db)

def get_task_repository(db: Session = Depends(get_db)) -> ITaskRepository:
    return TaskRepository(db)

def get_auth_service(
    user_repo: IUserRepository = Depends(get_user_repository),
) -> AuthService:
    return AuthService(user_repo)

def get_task_service(
    task_repo: ITaskRepository = Depends(get_task_repository),
) -> TaskService:
    return TaskService(task_repo)

def get_current_user(
    db: Session = Depends(get_db), token: str = Depends(oauth2_scheme)
) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[security.ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)
    except JWTError:
        raise credentials_exception
    user_repo = get_user_repository(db)
    user = user_repo.get_user_by_username(username=token_data.username)
    if user is None:
        raise credentials_exception
    return user

def get_current_active_user(
    current_user: User = Depends(get_current_user),
) -> User:
    if not current_user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user

def is_admin(
    current_user: User = Depends(get_current_active_user),
) -> User:
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Not enough permissions")
    return current_user 