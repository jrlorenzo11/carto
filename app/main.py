from fastapi import FastAPI
from contextlib import asynccontextmanager

from app.core.config import settings
from app.core.bootstrap import init_dirs

from app.api.health import router as health_router
from app.api.osm import router as osm_router
from app.api.autocad import router as autocad_router
from app.api.matcher import router as matcher_router
from app.api.tps_warp import router as tps_router
from app.api.pipeline import router as pipeline_router

# =========================
# Lifespan para startup/shutdown
# =========================
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Código que antes estaba en @app.on_event("startup")
    init_dirs()
    yield
    # Aquí podrías poner código de shutdown si hace falta
    # por ejemplo cerrar conexiones a DB, archivos, etc.

# =========================
# Crear app
# =========================
app = FastAPI(
    title=settings.app_name,
    debug=settings.debug,
    lifespan=lifespan
)

# =========================
# Routers
# =========================
app.include_router(health_router)
app.include_router(autocad_router, prefix="/gis", tags=["AutoCAD"])
app.include_router(osm_router, prefix="/osm", tags=["OSM"])
app.include_router(matcher_router, prefix="/gis", tags=["Matcher"])
app.include_router(tps_router, prefix="/gis", tags=["TPS Warp"])

app.include_router(pipeline_router, prefix="/gis", tags=["Pipeline"])
