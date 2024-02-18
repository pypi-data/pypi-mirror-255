from osgeo import ogr, osr

from pytezergis.spatial.extent import Extent
from pytezergis.spatial.latlng import Latlng

class LineString:

    def __init__(self, wkt, epsg=4326):
        """
        Classe representando uma linestring

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
        return LineString(self.wkt, self.epsg)

    def buffer(self, distance, epsg=4326):
        poly = self.clone()

        if poly.epsg != epsg:
            poly.transform(epsg)
        
        poly.geom = poly.geom.Buffer(distance)
        poly.wkt = poly.geom.ExportToWkt()

        if poly.epsg != self.epsg:
            poly.transform(self.epsg)

        return poly

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

        for i in range(0, self.geom.GetPointCount()):
            p = self.geom.GetPoint(i)
            arr.append(Latlng(p[1], p[0]))

        return arr

    def toWkt(self):
        return self.wkt

    def __latlngsToWkt(self, latlngs):
        ring = ogr.Geometry(ogr.wkbLinearRing)

        for latlng in latlngs:
            ring.AddPoint(latlng.lng, latlng.lat)

        return ring.ExportToWkt()

    def __str__(self):
        return self.wkt