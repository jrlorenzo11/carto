from fastapi import APIRouter, Query, HTTPException
from pydantic import BaseModel
from app.services.tps_warp import TPSWarp
from app.core.config import settings
import geopandas as gpd
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
        gdf_match = gpd.read_file(settings.SALIDA_DIR / "0.3.1_intersecciones_osm_con_acad.geojson")
        gdf_target = gpd.read_file(settings.SALIDA_DIR / "0.1.1_manzanas_autocad.geojson")
        gdf_result = service.apply(gdf_match=gdf_match,gdf_target=gdf_target)
        # =========================
        # PERSISTENCIA (HOY ARCHIVO, MAÑANA BD)
        # =========================
        out_file = settings.SALIDA_DIR / "0.4.1_manzanas_tps.geojson"
        gdf_result.to_file(out_file, driver="GeoJSON")

        return {
            "output_file": str(out_file),
            "total_features": len(gdf_result)
        }
    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
