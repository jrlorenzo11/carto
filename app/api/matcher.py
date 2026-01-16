from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel
from typing import Dict
import logging
from pathlib import Path

from app.core.config import settings
from app.services.matcher import SpatialMatcher
import geopandas as gpd

router = APIRouter(
    prefix="/matcher",
    tags=["Matcher"]
)

# =========================
# RESPONSE MODEL
# =========================
class MatcherResponse(BaseModel):
    total_matches: int
    output_file: str

# =========================
# LOGGER
# =========================
logger = logging.getLogger("matcher_api")
logger.setLevel(logging.INFO)
file_handler = logging.FileHandler(settings.LOG_DIR / "app.log")
formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)

# =========================
# ENDPOINT
# =========================
@router.post(
    "/match",
    response_model=MatcherResponse,
    summary="Asocia intersecciones OSM con grupos AutoCAD"
)
def run_matcher(dist_max: float = Query(20, description="Distancia máxima para match en metros")):
    try:
        service = SpatialMatcher(dist_max=dist_max, crs=settings.crs_local)
        gdf_result = service.match()

        total_matches = len(gdf_result)
        output_file = str(settings.SALIDA_DIR / "0.3.1_intersecciones_osm_con_acad.geojson")

        logger.info(f"Matcher completado: {total_matches} matches")
        return {
            "total_matches": total_matches,
            "output_file": output_file
        }

    except FileNotFoundError as e:
        logger.error(f"Archivo no encontrado: {e}")
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.exception(f"Error ejecutando matcher: {e}")
        raise HTTPException(status_code=500, detail=str(e))
