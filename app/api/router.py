from fastapi import APIRouter
from app.api.lab1.router import router as lab1_router

api_router = APIRouter()

api_router.include_router(
    lab1_router,
    prefix="/lab1",
    tags=["Lab1 - RNG"]
)
