from fastapi import APIRouter
from app.core.config import settings

router = APIRouter()

@router.get("/health")
def healthcheck():
    return {
        "status": "ok",
        "env": settings.env,
        "crs_local": settings.crs_local
    }
