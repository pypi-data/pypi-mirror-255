import numpy as np

from osgeo import osr, gdal
from pytezergis.geomathutils import GeoMathUtils
from pytezergis.spatial.georeference import GeoReference
from pytezergis.spatial.extent import Extent
from pytezergis.spatial.envelope import Envelope
from pytezergis.spatial.bbox import Bbox

class RasterOrder:
    CRGB = 1
    RGBC = 2

class RasterType:
    BYTE = gdal.GDT_Byte
    UINT16 = gdal.GDT_UInt16
    INT16 = gdal.GDT_Int16

    @staticmethod
    def convertToNumpyType(type):
        if type == RasterType.BYTE:
            return np.uint8
        
        if type == RasterType.UINT16:
            return np.uint16
        
        if type == RasterType.INT16:
            return np.int16

class Raster:
    READ  = 0
    WRITE = 1
    
    def __init__(self, filename, mode=READ):
        raster = self._raster = self.open(filename, mode)        

        self.width = raster.RasterXSize
        self.height = raster.RasterYSize
        self.bands = raster.RasterCount
        
    def open(self, filename, mode):
        raster = gdal.Open(filename, gdal.GA_ReadOnly if mode == Raster.READ else gdal.GA_Update)

        if raster is None:
            raise Exception("O arquivo espeficado para o raster não existe ou não é um tipo válido")
        
        return raster

    def dtype(self):
        return self._raster.GetRasterBand(1).DataType

    def close(self):
        self._raster = None

    def transform(self, transform=None):
        if transform is None:
            return self._raster.GetGeoTransform()
        else:
            self._raster.SetGeoTransform(transform)

    def epsg(self, epsg = None):
        if epsg is None:
            srs = osr.SpatialReference()
            srs.ImportFromWkt(self._raster.GetProjection())
            return self.__toInt(srs.GetAttrValue('AUTHORITY',1))
        else:
            srs = osr.SpatialReference()
            srs.ImportFromEPSG(epsg)
            self._raster.SetProjection(srs.ExportToWkt())

    def geoReference(self, geoReference=None):
        if geoReference is None:
            return GeoReference.createFromTransform(self.transform(), self.width, self.height)
        
        self.transform(geoReference.transform())
        
    def write(self, array, order=RasterOrder.RGBC):
        for i in range(self.bands):
            if order == RasterOrder.CRGB:
                band = array[i, :,:]
                self._raster.GetRasterBand(i + 1).WriteArray(band)
            else:
                band = array[:,:, i]
                self._raster.GetRasterBand(i + 1).WriteArray(band)

    def envelope(self):
        geo = self.geoReference()

        p1 = geo.pivot()
        p2 = geo.pointToLatLng((self._raster.RasterXSize, 0))
        p3 = geo.pointToLatLng((self._raster.RasterXSize, self._raster.RasterYSize))
        p4 = geo.pointToLatLng((0, self._raster.RasterYSize))

        return Envelope(p1, p2, p3, p4)

    def extent(self):
        geoRef = self.geoReference()
        pivot = geoRef.pivot()

        se = geoRef.pointToLatLng((self._raster.RasterXSize, self._raster.RasterYSize))

        return Extent(pivot, se)

    def bbox(self):
        env = self.envelope()

        return Bbox(env.south_west(), env.north_east())

    def band(self, number):
        band = self._raster.GetRasterBand(number)

        return band.ReadAsArray()

    def clip(self, bbox:Bbox, size=256, order=RasterOrder.RGBC):
        raster = self._raster
        bands = raster.RasterCount
        querysize = size
        data = None

        p1 = bbox.first().toList()
        p2 = bbox.last().toList()

        bbox = (*p1, *p2)

        rb, wb = GeoMathUtils.query(raster, bbox[0], bbox[3], bbox[2], bbox[1], querysize)
        rx, ry, rxsize, rysize = rb
        wx, wy, wxsize, wysize = wb

        if rxsize != 0 and rysize != 0 and wxsize != 0 and wysize != 0:
            data = raster.ReadRaster(rx, ry, rxsize, rysize, wxsize, wysize, band_list=list(range(1, bands+1)), buf_type=self.dtype())

        if data:
            mem_drv = gdal.GetDriverByName('MEM')
            dsquery = mem_drv.Create('', querysize, querysize, bands, eType=self.dtype())
            dsquery.WriteRaster(wx, wy, wxsize, wysize, data, band_list=list(range(1, bands+1)), buf_type=self.dtype())

            if order == RasterOrder.CRGB:
                array = np.zeros((bands, querysize, querysize), dtype=RasterType.convertToNumpyType(self.dtype()))

                for i in range(bands):
                    r = dsquery.GetRasterBand(i + 1)
                    array[i, :, :] = r.ReadAsArray(0, 0, querysize, querysize)

                return array
            else:
                array = np.zeros((querysize, querysize, bands), dtype=RasterType.convertToNumpyType(self.dtype()))

                for i in range(bands):
                    r = dsquery.GetRasterBand(i + 1)
                    array[:, :, i] = r.ReadAsArray(0, 0, querysize, querysize)

                return array

        return None

    def crop(self, roi=None, order=RasterOrder.RGBC):
        """
        Retorna um array com as bandas do raster

        Args:
            roi (tuple) (opcional): Tupla contendo os valores (origemX, origemY, width, height)

        Returns:
            numpy.array: Array com todas as bandas contidas no raster
        """
        bands = self.bands

        rasterXSize = self._raster.RasterXSize if roi is None else roi[2]
        rasterYSize = self._raster.RasterYSize if roi is None else roi[3]

        if order == RasterOrder.CRGB:
            array = np.zeros((bands, rasterYSize, rasterXSize), dtype=RasterType.convertToNumpyType(self.dtype()))
        else:
            array = np.zeros((rasterYSize, rasterXSize, bands), dtype=RasterType.convertToNumpyType(self.dtype()))

        for i in range(bands):
            r = self._raster.GetRasterBand(i + 1)
            if order == RasterOrder.CRGB:
                if roi is None:
                    array[i, :, :] = r.ReadAsArray(0, 0, rasterXSize, rasterYSize)
                else:
                    array[i, :, :] = r.ReadAsArray(roi[0], roi[1], roi[2], roi[3])
            else:
                if roi is None:
                    array[:, :, i] = r.ReadAsArray(0, 0, rasterXSize, rasterYSize)
                else:
                    array[:, :, i] = r.ReadAsArray(roi[0], roi[1], roi[2], roi[3])

        return array
        
    def clone(self, filename):
        dtype = self._raster.GetRasterBand(1).DataType
        driverName = self._raster.GetDriver().GetDescription()

        clone = Raster.create(filename, self.width, self.height, self.bands, dtype, driverName)
        clone.epsg(self.epsg())
        clone.transform(self.transform())

        return clone

    @staticmethod
    def create(filename, xsize, ysize, bands, dtype, driverName='GTiff'):
        driver = gdal.GetDriverByName(driverName)
        driver.Create(filename, xsize=xsize, ysize=ysize, bands=bands, eType=dtype)

        return Raster(filename, Raster.WRITE)
  
    def __toInt(self, str:str):
        try:
            return int(str)
        except Exception as ex:
            return 0
