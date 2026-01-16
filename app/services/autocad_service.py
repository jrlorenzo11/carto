import re
import numpy as np
import geopandas as gpd
from shapely.geometry import Polygon, MultiPoint
from scipy.spatial import KDTree
from itertools import combinations
from app.core.config import settings

class AutoCADService:
    def __init__(self, crs: str, dist_max: float):
        self.crs = crs
        self.dist_max = dist_max

    def procesar(self, archivo: str):
        csv_path = settings.ENTRADA_DIR / archivo

        if not csv_path.exists():
            raise FileNotFoundError(f"No existe el archivo: {csv_path}")

        # =========================
        # LEER TEXTO COMO EN STAND-ALONE
        # =========================
        texto = csv_path.read_text(encoding="latin-1", errors="ignore")

        bloques = texto.split("),nil")
        manzanas = []

        # =========================
        # PARSEO MANZANAS
        # =========================
        for bloque in bloques:
            if '(8 . "MANZANAS")' not in bloque:
                continue

            m_id = re.search(r'\(300 \. "1\|(\d+)\|"\)', bloque)
            if not m_id:
                continue

            id_manzana = m_id.group(1)

            coords = re.findall(
                r'\(10 \. ([\d\.\-]+) ([\d\.\-]+) [\d\.\-]+\)',
                bloque
            )

            if len(coords) < 3:
                continue

            coords = [(float(x), float(y)) for x, y in coords]

            if coords[0] != coords[-1]:
                coords.append(coords[0])

            poligono = Polygon(coords)
            if not poligono.is_valid:
                poligono = poligono.buffer(0)

            manzanas.append({
                "id_manzana": id_manzana,
                "geometry": poligono
            })

        gdf_manzanas = gpd.GeoDataFrame(
            manzanas,
            geometry="geometry",
            crs=self.crs
        )

        # =========================
        # EXTRAER ESQUINAS
        # =========================
        esquinas = []
        for _, row in gdf_manzanas.iterrows():
            coords = list(row.geometry.exterior.coords)
            for x, y in coords[:-1]:
                esquinas.append({
                    "id_manzana": row.id_manzana,
                    "geometry": gpd.points_from_xy([x], [y])[0]
                })

        gdf_esquinas = gpd.GeoDataFrame(
            esquinas,
            geometry="geometry",
            crs=self.crs
        )

        # =========================
        # PREPARAR COORDENADAS
        # =========================
        coords_np = np.array([(g.x, g.y) for g in gdf_esquinas.geometry])
        ids_manzana = gdf_esquinas["id_manzana"].to_numpy()
        tree = KDTree(coords_np)

        grupos_validos = []
        grupos_set = set()

        # =========================
        # GRUPOS DE 4
        # =========================
        for i, punto in enumerate(coords_np):
            vecinos_idx = tree.query_ball_point(punto, self.dist_max)
            if len(vecinos_idx) < 4:
                continue

            for combo in combinations(vecinos_idx, 4):
                ids_combo = ids_manzana[list(combo)]
                if len(set(ids_combo)) != 4:
                    continue

                sub_coords = coords_np[list(combo)]
                max_dist = max(
                    np.linalg.norm(a - b)
                    for a, b in combinations(sub_coords, 2)
                )
                if max_dist > self.dist_max:
                    continue

                combo_key = tuple(sorted(combo))
                if combo_key in grupos_set:
                    continue

                grupos_set.add(combo_key)
                grupos_validos.append({
                    "indices": combo,
                    "ids_manzana": ids_combo,
                    "geometry": MultiPoint(sub_coords).centroid
                })

        gdf_grupos = gpd.GeoDataFrame(
            grupos_validos,
            geometry="geometry",
            crs=self.crs
        )

        # =========================
        # GUARDAR
        # =========================
        out_manzanas = settings.SALIDA_DIR / "0.1.1_manzanas_autocad.geojson"
        out_esquinas = settings.SALIDA_DIR / "0.1.2_esquinas_autocad.geojson"
        out_grupos = settings.SALIDA_DIR / "0.1.3_grupos_esquinas_4.geojson"

        gdf_manzanas.to_file(out_manzanas, driver="GeoJSON")
        gdf_esquinas.to_file(out_esquinas, driver="GeoJSON")
        gdf_grupos.to_file(out_grupos, driver="GeoJSON")

        return {
            # ===== outputs (planos) =====
            "manzanas": str(out_manzanas),
            "esquinas": str(out_esquinas),
            "grupos_4": str(out_grupos),

            # ===== métricas =====
            "n_manzanas": len(gdf_manzanas),
            "n_esquinas": len(gdf_esquinas),
            "n_grupos_4": len(gdf_grupos),
        }

