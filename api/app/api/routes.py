from fastapi import APIRouter
from app.api.auth import router as auth_router
from app.api.starships import router as starships_router
from app.api.manufacturers import router as manufacturers_router

router = APIRouter()

router.include_router(auth_router)
router.include_router(starships_router)
router.include_router(manufacturers_router)
