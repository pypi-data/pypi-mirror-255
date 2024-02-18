class AbstractRaster:
    def __init__(self, filename:str):
        """
        Classe abstrata representando um raster generico
        Caso o arquivo informado não existe ou não seja possivel abrir o raster será lançada uma excessão
        """
        self.dataSource = self.open(filename)
        if self.dataSource is None:
            raise Exception("Não foi possível abrir o raster informado")

    def features(self):
        features = []

        if self.dataSource is None:
            return features

        for i in range(self.dataSource.GetLayerCount()):
            layer = self.dataSource.GetLayerByIndex(i)
            for feature in layer:
                features.append({
                    'wkt': feature.GetGeometryRef().ExportToWkt(),
                    'fields': feature.items()
                })

        if len(features) == 0:
            layer = self.dataSource.GetLayer()
            for feature in layer:
                features.append({
                    'wkt': feature.GetGeometryRef().ExportToWkt(),
                    'fields': feature.items()
                })

        return features

    def geometries(self):
        geometries = []

        if self.dataSource is None:
            return geometries

        for i in range(self.dataSource.GetLayerCount()):
            layer = self.dataSource.GetLayerByIndex(i)
            for feature in layer:
                geom = feature.GetGeometryRef()
                geometries.append(geom.ExportToWkt())

        if len(geometries) == 0:
            layer = self.dataSource.GetLayer()
            for feature in layer:
                geometries.append(feature.GetGeometryRef().ExportToWkt())

        return geometries

    def fields(self):
        arr = []

        if self.dataSource is None:
            return arr

        layers = self.dataSource.GetLayerCount()

        # Loop através das camadas
        for i in range(layers):
            layer = self.dataSource.GetLayer(i)

            # Loop através das feições (geometrias) na camada
            for feature in layer:
                # Obtenha as informações dos atributos (chave-valor) da feição
                arr.append(feature.items())

        return arr
    
    def epsg(self, type:str='GEOGCS'):
        if self.dataSource is None:
            return None
    
        layer= self.dataSource.GetLayer()
        crs = layer.GetSpatialRef()

        return crs.GetAuthorityCode(type)

    def open(self, filename):
        return None

    def close(self):
        self.dataSource = None