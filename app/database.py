import os

from typing import Annotated, AsyncGenerator

from fastapi import Depends
from sqlmodel import Session, create_engine

# Create db connection engine
engine = create_engine(os.environ.get("DATABASE_URL"))


def get_db():
    with Session(engine) as session:
        yield session


SessionDep = Annotated[Session, Depends(get_db)]

# print(os.environ.get("DATABASE_URL"))
