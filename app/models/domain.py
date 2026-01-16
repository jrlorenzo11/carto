# app/models/domain.py
from shapely.geometry import Polygon, Point

class Manzana:
    def __init__(self, id_manzana: str, geometry: Polygon):
        self.id = id_manzana
        self.geometry = geometry

class PuntoControl:
    def __init__(self, geom_acad: Point, geom_osm: Point):
        self.acad = geom_acad
        self.osm = geom_osm
