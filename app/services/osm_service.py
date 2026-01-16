class OSMService:
    import geopandas as gpd
    def __init__(self, crs: str = None, radio: float = None):
        self.crs = crs or "EPSG:22195"
        self.radio = radio or 1000

    def download(self, gdf_esquinas: gpd.GeoDataFrame, dx=0, dy=0):
        import geopandas as gpd
        import osmnx as ox

        # =========================
        # Centro de la zona
        # =========================
        centro = gdf_esquinas.geometry.unary_union.centroid
        x0, y0 = centro.x + dx, centro.y + dy

        centro_corr = gpd.GeoSeries([gpd.points_from_xy([x0], [y0])[0]], crs=self.crs)

        # =========================
        # Convertir a WGS84 para OSMnx
        # =========================
        centro_wgs84 = centro_corr.to_crs(epsg=4326).iloc[0]
        lat, lon = centro_wgs84.y, centro_wgs84.x

        # =========================
        # Descargar grafo OSM
        # =========================
        G = ox.graph_from_point(
            (lat, lon),
            dist=self.radio,
            network_type="drive",
            simplify=False,
            truncate_by_edge=True
        )

        # Proyectar a CRS métrico
        G = ox.project_graph(G, to_crs=self.crs)

        # Convertir a NO dirigido
        G = ox.convert.to_undirected(G)

        # =========================
        # Nodos y aristas
        # =========================
        gdf_nodes, gdf_edges = ox.graph_to_gdfs(G)
        gdf_nodes["grado"] = gdf_nodes.index.map(dict(G.degree()))

        # Filtrar nodos grado ≥3
        gdf_g4 = gdf_nodes[gdf_nodes["grado"] >= 3].copy()

        return gdf_g4, gdf_edges

