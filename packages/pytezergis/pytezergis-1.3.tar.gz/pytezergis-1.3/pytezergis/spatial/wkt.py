import ogr

from pytezergis.spatial.polygon import Polygon

class Wkt:
    def __init__(self, wkt):
        self.wkt = wkt
        self.geom = ogr.CreateGeometryFromWkt(self.wkt)

    @staticmethod
    def createFromWkb(wkb):
        geometry = ogr.CreateGeometryFromWkb(wkb)
        wkt = geometry.ExportToWkt()
        return Wkt(wkt)

    def isValid(self):
        return self.geom is not None

    def envelope(self):
        polygon = Polygon(self.wkt)
        return polygon.envelope()
    
    def isPoint(self):
        geom = self.geom
        geomType = geom.GetGeometryType()
        return geomType == ogr.wkbPoint or geomType == ogr.wkbPointM or geomType == ogr.wkbPointZM or geomType == ogr.wkbPoint25D

    def isMultiPoint(self):
        geom = self.geom
        geomType = geom.GetGeometryType()
        return geomType == ogr.wkbMultiPoint or geomType == ogr.wkbMultiPointM or geomType == ogr.wkbMultiPointZM or geomType == ogr.wkbMultiPoint25D
    
    def isLineString(self):
        geom = self.geom
        geomType = geom.GetGeometryType()
        return geomType == ogr.wkbLineString or geomType == ogr.wkbLineStringM or geomType == ogr.wkbLineStringZM or geomType == ogr.wkbLineString25D
    
    def isMultiLineString(self):
        geom = self.geom
        geomType = geom.GetGeometryType()
        return geomType == ogr.wkbMultiLineString or geomType == ogr.wkbMultiLineStringM or geomType == ogr.wkbMultiLineStringZM or geomType == ogr.wkbMultiLineString25D

    def isPolygon(self):
        geom = self.geom
        geomType = geom.GetGeometryType()
        return geomType == ogr.wkbPolygon or geomType == ogr.wkbPolygonM or geomType == ogr.wkbPolygonZM or geomType == ogr.wkbPolygon25D

    def isGeometryCollection(self):
        geom = self.geom
        geomType = geom.GetGeometryType()
        return geomType == ogr.wkbGeometryCollection or geomType == ogr.wkbGeometryCollectionM or geomType == ogr.wkbGeometryCollectionZM or geomType == ogr.wkbGeometryCollection25D

    def isCircularString(self):
        geom = self.geom
        geomType = geom.GetGeometryType()
        return geomType == ogr.wkbCircularString or geomType == ogr.wkbCircularStringZ or geomType == ogr.wkbCircularStringM or geomType == ogr.wkbCircularStringZM or geomType == ogr.wkbCircularString25D

    def isMultiPolygon(self):
        geom = self.geom
        geomType = geom.GetGeometryType()
        return geomType == ogr.wkbMultiPolygon or geomType == ogr.wkbMultiPolygonM or geomType == ogr.wkbMultiPolygonZM or geomType == ogr.wkbMultiPolygon25D

    def isLinearRing(self):
        geom = self.geom
        geomType = geom.GetGeometryType()
        return geomType == ogr.wkbLinearRing