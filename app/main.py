import os
from typing import Annotated, List, Union
from dotenv import load_dotenv


# Load .env
load_dotenv()

from fastapi import Depends, FastAPI, APIRouter, HTTPException
from fastapi.middleware import Middleware
from starlette.middleware.sessions import SessionMiddleware

from sqlmodel import select

from app.core import token_utils
from app.database import SessionDep
from app.crud import user as user_crud
from app.models.user import User
from app.api.routers import router as api_router

SESSION_SECRET_KEY = os.environ.get("SESSION_SECRET_KEY")

middleware = [
    Middleware(SessionMiddleware, secret_key=SESSION_SECRET_KEY),
]

app: FastAPI = FastAPI(middleware=middleware)


app.include_router(api_router)
