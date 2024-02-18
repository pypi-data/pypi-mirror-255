from osgeo import ogr

from pytezergis.raster.abstract import AbstractRaster

class Shapefile(AbstractRaster):
    def __init__(self, filename:str):
        super(Shapefile, self).__init__(filename)

    def open(self, filename:str):
        driver = ogr.GetDriverByName('ESRI Shapefile')
        return driver.Open(filename, 0)
       
    def metadata(self):
        return []