from pytezergis.spatial.latlng import Latlng

class Envelope:
    def __init__(self, p1:Latlng, p2:Latlng, p3:Latlng, p4:Latlng):
        """
        Classe que manipula 4 coordenadas representando os limites de uma geometria

        Args:
            p1 (tuple(Latlng), Latlng)
            p2 (Latlng, optional)
            p3 (Latlng, optional)
            p4 (Latlng, optional)
        """

        self.p1:Latlng = p1
        self.p2:Latlng = p2
        self.p3:Latlng = p3
        self.p4:Latlng = p4

    def north_east(self):
        """
        Retorna o ponto mais à direita superior
        """
        p = self.p1

        if self.p2.lat >= p.lat and self.p2.lng >= p.lng:
            p = self.p2
        
        if self.p3.lat >= p.lat and self.p3.lng >= p.lng:
            p = self.p3

        if self.p4.lat >= p.lat and self.p4.lng >= p.lng:
            p = self.p4

        return p

    def south_west(self):
        """
        Retorna o ponto mais à esquerda inferior
        """
        p = self.p1

        if self.p2.lat <= p.lat and self.p2.lng <= p.lng:
            p = self.p2
        
        if self.p3.lat <= p.lat and self.p3.lng <= p.lng:
            p = self.p3

        if self.p4.lat <= p.lat and self.p4.lng <= p.lng:
            p = self.p4

        return p

    def south_east(self):
        """
        Retorna o ponto mais à direita inferior
        """
        p = self.p1

        if self.p2.lat <= p.lat and self.p2.lng >= p.lng:
            p = self.p2
        
        if self.p3.lat <= p.lat and self.p3.lng >= p.lng:
            p = self.p3

        if self.p4.lat <= p.lat and self.p4.lng >= p.lng:
            p = self.p4

        return p

    def pivot(self):
        """
        Retorna o ponto mais à esquerda superior
        """
        p = self.p1

        if self.p2.lat >= p.lat and self.p2.lng <= p.lng:
            p = self.p2
        
        if self.p3.lat >= p.lat and self.p3.lng <= p.lng:
            p = self.p3

        if self.p4.lat >= p.lat and self.p4.lng <= p.lng:
            p = self.p4

        return p

    def isIntersect(self, envelope):
        latlower = 0
        lathigh = 0

        lnglower = 0
        lnghigh = 0

        if self.p1.lat < self.p4.lat:
            latlower = self.p1.lat
            lathigh = self.p4.lat
        else:
            latlower = self.p4.lat
            lathigh = self.p1.lat

        if self.p1.lng < self.p2.lng:
            lnglower = self.p1.lng
            lnghigh = self.p2.lng
        else:
            lnglower = self.p2.lng
            lnghigh = self.p1.lng

        if envelope.p1.lat >= latlower and envelope.p1.lat <= lathigh:
            if envelope.p1.lng >= lnglower and envelope.p1.lng <= lnghigh:
                return True

        if envelope.p2.lat >= latlower and envelope.p2.lat <= lathigh:
            if envelope.p2.lng >= lnglower and envelope.p2.lng <= lnghigh:
                return True

        if envelope.p3.lat >= latlower and envelope.p3.lat <= lathigh:
            if envelope.p3.lng >= lnglower and envelope.p3.lng <= lnghigh:
                return True

        if envelope.p4.lat >= latlower and envelope.p4.lat <= lathigh:
            if envelope.p4.lng >= lnglower and envelope.p4.lng <= lnghigh:
                return True

        return False

    def toList(self):
        return (
            (self.p1.lng, self.p1.lat),
            (self.p2.lng, self.p2.lat),
            (self.p3.lng, self.p3.lat),
            (self.p4.lng, self.p4.lat),
        )

    def toWkt(self):
        return "POLYGON ((%s %s, %s %s, %s %s, %s %s, %s %s))" % (
            self.p1.lng, self.p1.lat,
            self.p2.lng, self.p2.lat,
            self.p3.lng, self.p3.lat,
            self.p4.lng, self.p4.lat,
            self.p1.lng, self.p1.lat,
        )
    
    def __str__(self):
        return self.toWkt()