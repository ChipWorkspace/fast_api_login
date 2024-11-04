from typing import Annotated

from multimethod import multimethod

from fastapi import Form, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm

from sqlmodel import select

from app.core import auth_utils
from app.database import SessionDep
from app.models.user import User
from app.forms.user import CreateUserForm


@multimethod
def get_user(user_id: int, session: SessionDep) -> User:
    return session.get(User, user_id)


@multimethod
def get_user(email: str, session: SessionDep) -> User:
    return session.exec(select(User).where(User.email == email)).first()


def authenticate_user(login_form: OAuth2PasswordRequestForm, session: SessionDep):
    user: User = get_user(login_form.username.lower(), session)
    if not user or not auth_utils.verify_password(login_form.password, user.password):
        return False

    return user


def create_user(user_form: Annotated[CreateUserForm, Form()], session: SessionDep):
    if get_user(user_form.email.lower(), session):
        raise HTTPException(
            status.HTTP_409_CONFLICT,
            "This email is already in use",
        )

    try:
        user_form.password = auth_utils.get_password_hash(user_form.password)
        db_user: User = User(**user_form.model_dump())

        session.add(db_user)
        session.commit()
        session.refresh(db_user)

        return db_user

    except Exception as error:
        session.rollback()

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while creating the user.",
        )
