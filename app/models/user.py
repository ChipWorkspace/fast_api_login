from typing import Optional
from sqlmodel import SQLModel, Field


class User(SQLModel, table=True):
    __tablename__ = "asistente"
    id: Optional[int] = Field(default=None, primary_key=True)
    email: str = Field(unique=True)
    password: Optional[str] = Field(default=None)
    nombre: str = Field(default=None)
    apellido: str = Field(default=None)
    institucion: str = Field(default=None)
