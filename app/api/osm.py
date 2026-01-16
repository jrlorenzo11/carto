from fastapi import APIRouter, HTTPException, Query
from pathlib import Path
import logging
from app.core.config import settings
from app.services.osm_service import OSMService
import geopandas as gpd

router = APIRouter(
    prefix="/osm",
    tags=["OSM"]
)

# =========================
# ENDPOINT
# =========================
@router.post("/procesar")
def procesar_osm(
    dx: float = Query(0, description="Desplazamiento Este/Oeste en metros"),
    dy: float = Query(0, description="Desplazamiento Norte/Sur en metros"),
    radio: float = Query(500, description="Radio de descarga OSM en metros")
):
    try:
        # Cargar esquinas generadas por AutoCAD
        gdf_esquinas = gpd.read_file(settings.SALIDA_DIR / "0.1.2_esquinas_autocad.geojson")
        if gdf_esquinas.crs is None:
            gdf_esquinas = gdf_esquinas.set_crs(settings.crs_local)
        else:
            gdf_esquinas = gdf_esquinas.to_crs(settings.crs_local)

        # Instanciar servicio OSM y descargar nodos/aristas
        service = OSMService(crs=settings.crs_local, radio=radio)
        gdf_g4, gdf_edges = service.download(gdf_esquinas, dx=dx, dy=dy)

        # Guardar resultados
        out_nodes = settings.SALIDA_DIR / "0.2.1_intersecciones_osm_grado4.geojson"
        out_edges = settings.SALIDA_DIR / "0.2.2_aristas_osm.geojson"
        gdf_g4.to_file(out_nodes, driver="GeoJSON")
        gdf_edges.to_file(out_edges, driver="GeoJSON")

        return {
            "nodos_grado4": len(gdf_g4),
            "aristas": len(gdf_edges),
            "outputs": {
                "nodos": str(out_nodes),
                "aristas": str(out_edges)
            }
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
