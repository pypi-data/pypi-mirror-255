class Latlng:
    def __init__(self, lat:float, lng:float):
        """
        Classe representando uma coordenada de ponto

        Args:
            lat (float)
            lng (float)
        """
        self.lat = lat
        self.lng = lng

    def toList(self):
        return (self.lng, self.lat)

    def compareTo(self, latlng):
        if self.lat < latlng.lat and self.lng < latlng.lng:
            return - 1
        elif self.lat == latlng.lat and self.lng == latlng.lng:
            return 0
        else:
            return 1
        
    def toWkt(self):
        return "POINT (%s %s)" % (self.lng, self.lat)
        
    def __getitem__(self, idx):
        return self.lng if idx == 0 else self.lat

    def __str__(self):
        return "POINT (%s %s)" % (self.lng, self.lat)