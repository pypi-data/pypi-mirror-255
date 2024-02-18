from pytezergis.raster.kml import KML

from pytezerio.directory import Directory
from pytezerio.file import File

from zipfile import ZipFile

class KMZ(KML):
    def __init__(self, filename:str):
        super(KMZ, self).__init__(filename)

    def open(self, filename):
        self.__temp = Directory.temporary()
        with ZipFile(filename, 'r') as zip:
            zip.extractall(self.__temp.fullpath)

        for filename in self.__temp.list(Directory.FILES):
            file = File(filename)
            if file.extension() == 'kml':
                return super().open(self.__temp.resolve(filename))

    def __del__(self):
        self.close()

        if self.__temp is not None:
            self.__temp.remove()
        
        self.__temp = None
