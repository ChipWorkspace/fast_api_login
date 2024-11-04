from pydantic import BaseModel


class CreateUserForm(BaseModel):
    email: str
    password: str
