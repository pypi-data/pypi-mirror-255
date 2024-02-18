from osgeo import ogr, osr

from pytezergis.spatial.extent import Extent
from pytezergis.spatial.latlng import Latlng

class Polygon:

    def __init__(self, wkt, epsg=4326):
        """
        Classe representando um poligono

        Args:
            wkt (str, list(Latlng))
            epsg (int, optional)
        """

        if isinstance(wkt, (list, tuple)):
            wkt = self.__latlngsToWkt(wkt)

        self.wkt = wkt
        self.epsg = epsg

        self.geom = ogr.CreateGeometryFromWkt(wkt)

    
    def isValid(self):
        return self.geom is not None

    def envelope(self):
        env = self.geom.GetEnvelope()
        return Extent.createFromList((env[0], env[2], env[1], env[3])).toEnvelope()

    def clone(self):
        return Polygon(self.wkt, self.epsg)

    def buffer(self, distance, epsg=4326):
        poly = self.clone()

        if poly.epsg != epsg:
            poly.transform(epsg)
        
        poly.geom = poly.geom.Buffer(distance)
        poly.wkt = poly.geom.ExportToWkt()

        if poly.epsg != self.epsg:
            poly.transform(self.epsg)

        return poly

    def intersect(self, polygon):
        p = self.geom.Intersection(polygon.geom)

        if p is None:
            return None

        if p.IsEmpty():
            return None
            
        return Polygon(p.ExportToWkt(), self.epsg)

    def area(self, epsg=None):
        if epsg is None:
            return self.geom.GetArea()

        p = self.clone()
        p.transform(epsg)
        return p.area()

    def perimeter(self):
        return self.geom.Boundary().Length()

    def transform(self, epsg):
        src = osr.SpatialReference()
        src.ImportFromEPSG(self.epsg)

        dst = osr.SpatialReference()
        dst.ImportFromEPSG(epsg)

        transform = osr.CoordinateTransformation(src, dst)

        self.geom.Transform(transform)
        self.wkt = self.geom.ExportToWkt()

        self.epsg = epsg

    def toLatlngs(self):
        arr = []

        for geom in self.geom:
            for i in range(0, geom.GetPointCount()):
                p = geom.GetPoint(i)
                arr.append(Latlng(p[1], p[0]))

        return arr

    def toWkt(self):
        return self.wkt

    def __latlngsToWkt(self, latlngs):
        ring = ogr.Geometry(ogr.wkbLinearRing)

        for latlng in latlngs:
            ring.AddPoint(latlng.lng, latlng.lat)

        firstPoint = latlngs[0]
        lastPoint = latlngs[len(latlngs)-1]

        if firstPoint.lng != lastPoint.lng or firstPoint.lat != lastPoint.lat:
            ring.AddPoint(firstPoint.lng, firstPoint.lat)

        poly = ogr.Geometry(ogr.wkbPolygon)
        poly.AddGeometry(ring)

        poly.FlattenTo2D()

        return poly.ExportToWkt()

    def __str__(self):
        return self.wkt