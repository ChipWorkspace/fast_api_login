from typing import Union
from fastapi import FastAPI, APIRouter

app: FastAPI = FastAPI()
router: APIRouter = APIRouter()


@router.get("/users/", tags=["users"])
async def read_users():
    return [{"username": "Rick"}, {"username": "Morty"}]


app.include_router(router)
