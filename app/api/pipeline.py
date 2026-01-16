from fastapi import APIRouter, Query, HTTPException
from pydantic import BaseModel
from app.services.pipeline import GISPipeline
from app.core.config import settings

router = APIRouter(
    prefix="/pipeline",
    tags=["GIS Pipeline"]
)

class PipelineResponse(BaseModel):
    autocad: dict
    osm: dict
    matcher: dict
    tps: dict

@router.post("/run", response_model=PipelineResponse)
def run_pipeline(
    archivo: str = Query(..., description="CSV AutoCAD en data/entrada"),
    dist_max: float = Query(30),
    radio_osm: float = Query(1000),
    dist_match: float = Query(20),
    smooth_tps: float = Query(1.0),
    crs: str = Query(settings.crs_local),
):
    try:
        pipeline = GISPipeline(
            archivo=archivo,
            crs=crs,
            dist_max=dist_max,
            radio_osm=radio_osm,
            dist_match=dist_match,
            smooth_tps=smooth_tps,
        )
        return pipeline.run()

    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
