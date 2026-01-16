from fastapi import APIRouter, UploadFile
from app.services.autocad_service import AutoCADParser
from app.services.osm_service import OSMService
from app.services.matcher import SpatialMatcher
from app.services.tps_warp import TPSWarp
from app.core.config import settings

router = APIRouter()

@router.post("/correct")
def correct_cartography(file: UploadFile):
    parser = AutoCADParser(settings.crs_autocad, settings.dist_esquinas)
    osm = OSMService(settings.crs_autocad, settings.osm_radio)
    matcher = SpatialMatcher(settings.dist_match, settings.crs_autocad)
    tps = TPSWarp(settings.tps_smooth, settings.crs_autocad)

    gdf_manz, gdf_esq, gdf_grupos = parser.parse_csv(file.file)
    gdf_osm, _ = osm.download(gdf_esq)
    gdf_ctrl = matcher.match(gdf_osm, gdf_grupos)
    gdf_final = tps.apply(gdf_ctrl, gdf_grupos, gdf_manz)

    return {"status": "ok"}
