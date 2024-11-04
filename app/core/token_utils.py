from typing import Annotated

import os
import jwt
from jwt import InvalidTokenError
from datetime import datetime, timedelta, timezone

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer

from app.crud.user import get_user
from app.models.token import Token, TokenData
from app.database import SessionDep

SECRET_KEY = os.environ.get("SECRET_KEY")
ALGORITHM = os.environ.get("ALGORITHM")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.environ.get("ACCESS_TOKEN_EXPIRE_MINUTES"))
ACCESS_TOKEN_REFRESH_MINUTES = int(os.environ.get("ACCESS_TOKEN_REFRESH_MINUTES"))


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/login")


def get_expiration_time(
    expires_delta: timedelta,
):
    if expires_delta:
        expire = expires_delta
    else:
        expire = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    return datetime.now(timezone.utc) + expire


def decode_token(token: Token) -> dict:
    return jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])


def create_access_token(
    data: dict,
    expires_delta: timedelta | None = None,
):
    to_encode: dict = data.copy()
    expire = get_expiration_time(expires_delta)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


def refresh_token_expiration(
    token: Token,
    expires_delta: timedelta | None = None,
):
    token_data = decode_token(token)
    expire_delta = timedelta(minutes=ACCESS_TOKEN_REFRESH_MINUTES)
    return create_access_token(token_data, expire_delta)


async def get_current_user(
    token: Annotated[str, Depends(oauth2_scheme)],
    session: SessionDep,
):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        username: str = decode_token(token).get("sub")
        if username is None:
            raise credentials_exception

        token_data = TokenData(username=username)

    except InvalidTokenError:
        raise credentials_exception

    user = get_user(token_data.username, session)
    if user is None:
        raise credentials_exception

    return user
