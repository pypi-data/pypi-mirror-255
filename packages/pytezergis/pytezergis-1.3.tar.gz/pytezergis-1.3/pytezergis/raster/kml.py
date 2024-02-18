import xml.etree.ElementTree as ET

from osgeo import ogr
from pytezergis.raster.abstract import AbstractRaster

class KML(AbstractRaster):
    def __init__(self, filename:str):
        super(KML, self).__init__(filename)

    def open(self, filename:str):
        driver = ogr.GetDriverByName('KML')
        self._filename = filename
        return driver.Open(filename)
    
    def metadata(self):
        xml_data = ''
        with open(self._filename, "r") as file:
            xml_data = file.read()

        # Parse do XML
        root = ET.fromstring(xml_data)

        # Namespace utilizado no XML
        namespace = "{http://www.opengis.net/kml/2.2}"

        # Dicionário para armazenar os dados por SchemaData
        metadata = []

        # Itera sobre todos os elementos <SchemaData> dentro do XML
        for schema_data in root.findall(f".//{namespace}SchemaData"):
            schema_id = schema_data.get("schemaUrl")
            simple_data_list = {}
            
            # Itera sobre todos os elementos <SimpleData> dentro de cada <SchemaData>
            for simple_data in schema_data.findall(f".//{namespace}SimpleData"):
                name = simple_data.get("name")
                value = simple_data.text
                simple_data_list[name] = value
            
            metadata.append(simple_data_list)

        return metadata