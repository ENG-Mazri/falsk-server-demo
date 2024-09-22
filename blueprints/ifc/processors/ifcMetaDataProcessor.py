import ifcopenshell.geom as Geom
import ifcopenshell.util as Util

settings = Geom.settings()

class IfcMetaDataProcessor:
    
    def __init__(self, model):
        self.model = model

    def getElemmentsByStorey(self):
        elementsByStorey = {}

        stories = self.model.by_type("IfcBuildingStorey")
        for storey in stories:
            elements = Util.element.get_decomposition(storey)
            ids = []
            for element in elements:
                try:
                    ids.append(element.Name)
                    # shape = Geom.create_shape(settings, element)
                    # verts = shape.geometry.verts
                    # matrix = shape.matrix
                    
                except:
                    print("An exception occurred")

            elementsByStorey[storey.Name] = ids

        return elementsByStorey