from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel
from typing import Dict
from pathlib import Path
import logging

from app.core.config import settings
from app.services.autocad_service import AutoCADService

router = APIRouter(
    prefix="/autocad",
    tags=["AutoCAD"]
)

# =========================
# RESPONSE MODEL
# =========================
class AutoCADResponse(BaseModel):
    manzanas: int
    esquinas: int
    grupos_4: int
    outputs: Dict[str, str]

# =========================
# LOGGER
# =========================
logger = logging.getLogger("autocad")
logger.setLevel(logging.INFO)
file_handler = logging.FileHandler(settings.LOG_DIR / "app.log")
formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)

# =========================
# ENDPOINT
# =========================
@router.post(
    "/procesar",
    response_model=AutoCADResponse,
    summary="Procesa archivo AutoCAD CSV y genera GeoJSON"
)
def procesar_autocad(
    archivo: str = Query(..., description="Nombre del archivo CSV en /data/entrada"),
    crs: str = Query(settings.crs_local, description="CRS de salida"),
    dist_max: float = Query(30, description="Distancia máxima para grupos de 4")
):
    csv_path: Path = settings.ENTRADA_DIR / archivo
    if not csv_path.exists():
        logger.error(f"Archivo no encontrado: {csv_path}")
        raise HTTPException(status_code=404, detail=f"No se encuentra el archivo {archivo}")

    try:
        service = AutoCADService(crs=crs, dist_max=dist_max)
        result = service.procesar(archivo)
        logger.info(f"Archivo procesado correctamente: {archivo}")
        return result
    except Exception as e:
        logger.exception(f"Error procesando AutoCAD: {e}")
        raise HTTPException(status_code=500, detail=str(e))
