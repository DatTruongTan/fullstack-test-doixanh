from fastapi import APIRouter, Depends
from fastapi.security import OAuth2PasswordRequestForm
from datetime import timedelta

from app import security
from app.config import settings
from app.presentation.dependencies import get_auth_service
from app.application.services.auth_service import AuthService
from app.application.schemas.token import Token
from app.application.schemas.user import User, UserCreate

router = APIRouter()

@router.post("/register", response_model=User)
def register_user(
    user: UserCreate, auth_service: AuthService = Depends(get_auth_service)
):
    return auth_service.register_user(user)

@router.post("/token", response_model=Token)
async def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    auth_service: AuthService = Depends(get_auth_service),
):
    user = auth_service.login_user(form_data.username, form_data.password)
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = security.create_access_token(
        subject=user.username, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"} 