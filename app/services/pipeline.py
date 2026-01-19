from app.services.autocad_service import AutoCADService
from app.services.osm_service import OSMService
from app.services.matcher import SpatialMatcher
from app.services.tps_warp import TPSWarp
from app.core.config import settings
import geopandas as gpd

class GISPipeline:
    def __init__(
        self,
        archivo: str,
        crs: str,
        dist_max: float,
        radio_osm: float,
        dist_match: float,
        smooth_tps: float,
    ):
        self.archivo = archivo
        self.crs = crs
        self.dist_max = dist_max
        self.radio_osm = radio_osm
        self.dist_match = dist_match
        self.smooth_tps = smooth_tps

    def run(self):
        summary = {}

        # =========================
        # 1. AUTOCAD
        # =========================
        autocad = AutoCADService(
            crs=self.crs,
            dist_max=self.dist_max
        )
        result_autocad = autocad.procesar(self.archivo)
        path_esquinas= settings.SALIDA_DIR / "0.1.2_esquinas_autocad.geojson"
        gdf_esquinas = result_autocad["esquinas"]
        gdf_esquinas = gpd.read_file(path_esquinas)
        assert hasattr(gdf_esquinas, "geometry"), "gdf_esquinas no tiene geometría"

        summary["autocad"] = {
            "n_manzanas": result_autocad["n_manzanas"],
            "n_esquinas": result_autocad["n_esquinas"],
            "n_grupos_4": result_autocad["n_grupos_4"],
        }


        # =========================
        # 2. OSM
        # =========================
        osm = OSMService(
            crs=self.crs,
            radio=self.radio_osm
        )

        gdf_esquinas = gpd.read_file(result_autocad["esquinas"])

        gdf_g4, gdf_edges = osm.download(gdf_esquinas)

        assert hasattr(gdf_g4, "geometry"), "gdf_g4 no tiene geometría"
        assert hasattr(gdf_edges, "geometry"), "gdf_edges no tiene geometría"

        summary["osm"] = {
            "intersecciones": len(gdf_g4),
            "aristas": len(gdf_edges)
        }

        # =========================
        # 3. MATCHER
        # =========================
        matcher = SpatialMatcher(
            dist_max=self.dist_match,
            crs=self.crs
        )

        gdf_match = matcher.match(
            gdf_acad=gdf_esquinas,
            gdf_osm=gdf_g4
        )

        summary["matcher"] = {
            "matches": len(gdf_match)
        }

        # =========================
        # 4. TPS
        # =========================


        tps = TPSWarp(
            smooth=self.smooth_tps,
            crs=self.crs
        )
        gdf_tps = tps.apply(
            gdf_match=gdf_match,
            gdf_target=gdf_esquinas
        )
        out_tps = settings.SALIDA_DIR / "0.4.1_esquinas_tps.geojson"
        gdf_tps.to_file(out_tps, driver="GeoJSON")

        summary["tps"] = {
            "features": len(gdf_tps),
            "output": str(out_tps)
        }

        return summary
