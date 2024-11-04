from typing import Annotated
from datetime import timedelta

from jwt import ExpiredSignatureError

from fastapi import APIRouter, Form, HTTPException, Depends, status, Request
from fastapi.security import OAuth2PasswordRequestForm

from app.database import SessionDep
from app.crud import user as user_crud
from app.core import auth_utils, token_utils
from app.models.token import Token
from app.models.user import User
from app.forms.user import CreateUserForm

router: APIRouter = APIRouter(prefix="/v1")


@router.post("/token")
async def login(
    request: Request,
    login_form: Annotated[OAuth2PasswordRequestForm, Depends()],
    session: SessionDep,
) -> Token:
    user = user_crud.authenticate_user(login_form, session)
    if not user:
        raise HTTPException(
            status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token_expires = timedelta(minutes=token_utils.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = token_utils.create_access_token(
        data={"sub": user.email},
        expires_delta=access_token_expires,
    )

    return Token(access_token=access_token, token_type="bearer")


@router.post("/token/refresh")
async def refresh_token(
    request: Request,
    token: Annotated[Token, Depends(token_utils.oauth2_scheme)],
):
    try:
        new_token = token_utils.refresh_token_expiration(token)

    except ExpiredSignatureError:
        raise HTTPException(
            status.HTTP_401_UNAUTHORIZED,
            headers={"WWW-Authenticate": "Bearer"},
        )

    return new_token


@router.post("/logout")
async def logout(
    request: Request,
    token: Annotated[Token, Depends(token_utils.oauth2_scheme)],
):
    pass


@router.post("/register")
async def register_user(
    form_data: Annotated[CreateUserForm, Form()],
    session: SessionDep,
):
    user = user_crud.create_user(form_data, session)

    access_token_expires = timedelta(minutes=token_utils.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = token_utils.create_access_token(
        data={"sub": user.email},
        expires_delta=access_token_expires,
    )

    return Token(access_token=access_token, token_type="bearer")
