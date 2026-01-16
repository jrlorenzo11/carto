from fastapi import APIRouter, Query, HTTPException
from pydantic import BaseModel
from app.services.tps_warp import TPSWarp
from app.core.config import settings

router = APIRouter(
    prefix="/tps",
    tags=["TPS Warp"]
)

class TPSResponse(BaseModel):
    output_file: str
    total_features: int

@router.post("/apply", response_model=TPSResponse, summary="Aplica TPS Warp sobre manzanas")
def apply_tps(smooth: float = Query(1.0, description="Factor de suavizado TPS")):
    try:
        service = TPSWarp(smooth=smooth)
        gdf_result = service.apply()
        return {
            "output_file": str(service.out_file),
            "total_features": len(gdf_result)
        }
    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
