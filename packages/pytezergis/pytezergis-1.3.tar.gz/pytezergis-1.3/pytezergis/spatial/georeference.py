from pytezergis.spatial.wkt import Wkt
from pytezergis.spatial.latlng import Latlng
from pytezergis.spatial.polygon import Polygon

class GeoReference:
    def __init__(self, latlng:Latlng, tx, ty, width, height):
        self._latlng = latlng
        self._tx = tx
        self._ty = ty

        self.width = width
        self.height = height

        self.__load_bounds()

    def pivot(self):
        return self._latlng

    def transform(self):
        return (self._latlng.lng, self._tx, 0.0, self._latlng.lat, 0.0, self._ty)
    
    def latLngsToPoints(self, latlngs):
        points = []

        for latlng in latlngs:
            points.append(self.latLngToPoint(latlng))

        return points
    
    def pointsToLatlngs(self, points):
        latlngs = []

        for point in points:
            latlngs.append(self.pointToLatLng(point))

        return latlngs

    def pointsToPolygon(self, points):
        return Polygon(self.pointsToLatlngs(points))

    def polygonToPoints(self, polygon:Polygon):
        return self.latLngsToPoints(polygon.toLatlngs())

    def pointToLatLng(self, point):
        x, y = point
        rx = float(x / self.width)
        ry = float(y / self.height)

        rs = self.__lerp(self.tr, self.br, ry)
        ls = self.__lerp(self.tl, self.bl, ry)

        (lng, lat) = self.__lerp(ls, rs, rx)

        return Latlng(lat, lng)

    def latLngToPoint(self, latlng:Latlng):
        transform = self.transform()

        x = int((latlng.lng - transform[0]) / transform[1] + 0.001)
        y = int((latlng.lat - transform[3]) / transform[5] + 0.001)

        return x, y

    def __lerp(self, p1, p2, t):
        x = ((1 - t)*p1[0]) + (t*p2[0])
        y = ((1 - t)*p1[1]) + (t*p2[1])

        return (x, y)

    def __load_bounds(self):
        self.tl = self.__get_corner(0.0, 0.0)
        self.tr = self.__get_corner(self.width, 0.0)
        self.bl = self.__get_corner(0.0, self.height)
        self.br = self.__get_corner(self.width, self.height)
        
    def __get_corner(self, x, y):
        transform = self.transform()

        gx = transform[0] + transform[1] * x + transform[2] * y
        gy = transform[3] + transform[4] * x + transform[5] * y

        return (gx, gy)

    @staticmethod
    def createFromTransform(transform, width, height):
        return GeoReference(Latlng(transform[3], transform[0]), transform[1], transform[5], width, height)

    @staticmethod
    def createFromWkt(wkt, width, height):
        if isinstance(wkt, str):
            wkt = Wkt(wkt)

        e = wkt.envelope()
        p1 = e.pivot()
        p2 = e.south_east()

        tx = (p2.lng - p1.lng) / width
        ty = (p2.lat - p1.lat) / height

        return GeoReference(p1, tx, ty, width, height)
    
    def __str__(self) -> str:
        return "pivot = %s \ntx = %s \nty = %s \nwidth = %s \nheight = %s" % (self._latlng, self._tx, self._tx, self.width, self.height)