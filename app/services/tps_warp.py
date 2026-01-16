import geopandas as gpd
import numpy as np
from shapely.geometry import Point, LineString, Polygon
from scipy.interpolate import Rbf
from app.core.config import settings


class TPSWarp:
    def __init__(self, smooth: float = 1.0, crs: str = settings.crs_local):
        self.smooth = smooth
        self.crs = crs

    def apply(
        self,
        gdf_match: gpd.GeoDataFrame,
        gdf_target: gpd.GeoDataFrame,
    ) -> gpd.GeoDataFrame:
        """
        Aplica Thin Plate Spline usando matches OSM ↔ AutoCAD
        y deforma las geometrías de gdf_target.

        Parámetros
        ----------
        gdf_match : GeoDataFrame
            Salida de SpatialMatcher.match()
            Geometría activa = OSM
        gdf_target : GeoDataFrame
            Geometrías a deformar (AutoCAD)

        Retorna
        -------
        GeoDataFrame
            gdf_target deformado
        """

        # =========================
        # COPIAS DEFENSIVAS
        # =========================
        gdf_match = gdf_match.copy()
        gdf_target = gdf_target.copy()

        # =========================
        # CRS
        # =========================
        if gdf_match.crs != self.crs:
            gdf_match = gdf_match.to_crs(self.crs)
        if gdf_target.crs != self.crs:
            gdf_target = gdf_target.to_crs(self.crs)

        # =========================
        # COORDENADAS DE CONTROL
        # =========================
        # geometry = OSM
        geom_osm = gdf_match.geometry
        geom_acad = gdf_match["geometry_right"]

        mask = (~geom_osm.isna()) & (~geom_acad.isna())

        if mask.sum() < 6:
            raise ValueError("No hay suficientes puntos de control para TPS")

        x_osm = geom_osm[mask].x.values
        y_osm = geom_osm[mask].y.values
        x_acad = geom_acad[mask].x.values
        y_acad = geom_acad[mask].y.values

        # =========================
        # NORMALIZACIÓN
        # =========================
        x0 = np.mean(x_osm)
        y0 = np.mean(y_osm)

        x_osm_c = x_osm - x0
        y_osm_c = y_osm - y0
        x_acad_c = x_acad - x0
        y_acad_c = y_acad - y0

        # =========================
        # TPS (RBF)
        # =========================
        rbf_x = Rbf(
            x_osm_c, y_osm_c, x_acad_c,
            function="thin_plate",
            smooth=self.smooth
        )
        rbf_y = Rbf(
            x_osm_c, y_osm_c, y_acad_c,
            function="thin_plate",
            smooth=self.smooth
        )

        # =========================
        # FUNCIONES DEFORMADORAS
        # =========================
        def warp_coords(xs, ys):
            xs_c = np.asarray(xs) - x0
            ys_c = np.asarray(ys) - y0
            xn = rbf_x(xs_c, ys_c) + x0
            yn = rbf_y(xs_c, ys_c) + y0
            return xn, yn

        def warp_geom(geom):
            if geom is None or geom.is_empty:
                return geom

            if geom.geom_type == "Point":
                x, y = geom.xy
                xn, yn = warp_coords(x, y)
                return Point(xn[0], yn[0])

            elif geom.geom_type == "LineString":
                xs, ys = geom.xy
                xn, yn = warp_coords(xs, ys)
                return LineString(zip(xn, yn))

            elif geom.geom_type == "Polygon":
                xs, ys = geom.exterior.xy
                xn, yn = warp_coords(xs, ys)
                return Polygon(zip(xn, yn))

            else:
                return geom

        # =========================
        # APLICAR TPS
        # =========================
        gdf_target["geometry"] = gdf_target.geometry.apply(warp_geom)

        return gdf_target
