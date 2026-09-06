from fastapi import APIRouter
from app.api.endpoints import areas, satellite, change_detection, auth, health, users

api_router = APIRouter()

api_router.include_router(health.router, prefix="/health", tags=["health"])
api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(areas.router, prefix="/areas", tags=["areas"])
api_router.include_router(satellite.router, prefix="/satellite", tags=["satellite"])
api_router.include_router(change_detection.router, prefix="/change-detection", tags=["change-detection"])
