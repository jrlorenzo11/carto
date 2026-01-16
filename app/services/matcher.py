import logging
import geopandas as gpd
from app.core.config import settings

logger = logging.getLogger("matcher")
logger.setLevel(logging.INFO)
file_handler = logging.FileHandler(settings.LOG_DIR / "app.log")
formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)


class SpatialMatcher:
    def __init__(self, dist_max: float = 20, crs: str = settings.crs_local):
        self.dist_max = dist_max
        self.crs = crs

    def match(self, gdf_osm=None, gdf_acad=None):
        # =========================
        # LEER ARCHIVOS SI NO SE PASAN
        # =========================
        if gdf_osm is None:
            gdf_osm = gpd.read_file(settings.SALIDA_DIR / "0.2.1_intersecciones_osm_grado4.geojson")
        if gdf_acad is None:
            gdf_acad = gpd.read_file(settings.SALIDA_DIR / "0.1.3_grupos_esquinas_4.geojson")

        # reproyectar a CRS de la clase
        gdf_osm = gdf_osm.to_crs(self.crs)
        gdf_acad = gdf_acad.to_crs(self.crs)

        gdf_osm["id_osm"] = gdf_osm.index
        gdf_acad["id_acad"] = gdf_acad.index

        # =========================
        # ASOCIACIÓN ESPACIAL
        # =========================
        join = gpd.sjoin_nearest(
            gdf_osm,
            gdf_acad,
            how="left",
            max_distance=self.dist_max,
            distance_col="dist_m"
        )

        # quedarse con el más cercano por id_osm
        join = join.sort_values("dist_m").drop_duplicates(subset="id_osm")

        logger.info(f"Intersecciones OSM asociadas: {join['id_acad'].notna().sum()}")

        # filtrar solo matches
        join = join.dropna(subset=["dist_m"])
        logger.info(f"Intersecciones finales: {len(join)}")

        # =========================
        # GUARDAR RESULTADO
        # =========================
        out_file = settings.SALIDA_DIR / "0.3.1_intersecciones_osm_con_acad.geojson"
        join.to_file(out_file, driver="GeoJSON")
        logger.info(f"Archivo guardado: {out_file}")

        return join
