from pytezergis.spatial.envelope import Envelope
from pytezergis.spatial.latlng import Latlng

class Bbox:
    def __init__(self, p1:Latlng, p2:Latlng):
        """
        Classe contendo duas coordenadas representando as extremidades de um poligono

        Args:
            p1 (tuple(Latlng), Envelop)
            p2 (Latlng, optional)
        """
        self.p1 = p1
        self.p2 = p2

    @staticmethod
    def createFromList(latlngs:tuple):
        p1 = Latlng(latlngs[1], latlngs[0])
        p2 = Latlng(latlngs[3], latlngs[2])

        return Bbox(p1, p2)

    @staticmethod
    def createFromEnvelope(env:Envelope):
        p1 = env.south_west()
        p2 = env.north_east()

        return Bbox(p1, p2)

    def first(self):
        if self.p1.lng < self.p2.lng:
            return self.p1

        return self.p2

    def last(self):
        if self.p1.lng < self.p2.lng:
            return self.p2
            
        return self.p1

    def toArray(self):
        first = self.first()
        last = self.last()

        return (first.lng, first.lat, last.lng, last.lat)

    def toEnvelope(self):
        first = self.first()
        last = self.last()

        p1 = Latlng(last.lat, first.lng)
        p2 = last
        p3 = Latlng(first.lat, last.lng)
        p4 = first

        return Envelope(p1, p2, p3, p4)
    
    def __str__(self) -> str:
        return self.toWkt()
    
    def toWkt(self):
        pass
        first = self.first()
        last = self.last()

        return "LINESTRING (%s %s, %s %s)" % (first.lng, first.lat, last.lng, last.lat)