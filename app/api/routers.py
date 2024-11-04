from fastapi import APIRouter

from app.api.v1.auth import router as auth_router


router: APIRouter = APIRouter(prefix="/api")

router.include_router(auth_router, tags=["auth"])
