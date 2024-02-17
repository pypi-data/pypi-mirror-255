import svgwrite
from shapely import Polygon
from svgmapper.translate import Translator


class Path:
    def __init__(self, geometry: Polygon, name: str = '', translator: Translator = None):
        self.geometry = geometry
        self.dwg = svgwrite.Drawing()
        self.name = name
        self.path_string = ''
        self.translator = translator
        self.path = None
        self.write()

    def simplify(self):
        max_coords = 20000
        coord_num = len(self.geometry.exterior.coords)
        if coord_num < max_coords: return None
        tolerance = 0
        while coord_num > max_coords:
            tolerance += 100
            self.geometry = self.geometry.simplify(tolerance)
            coord_num = len(self.geometry.exterior.coords)

    def translate(self, x, y):
        lat, long = self.translator.translate(x, y) if self.translator else (x, y)
        return f'{lat}, {long}'

    def write(self):
        self.simplify()
        coordinates = self.geometry.exterior.coords
        data = [self.translate(x, y) for x, y in coordinates]
        path_data = "M " + " ".join(data) + " Z"
        self.path = self.dwg.path(
            d=path_data,
            class_= self.name if self.name else 'path'
        )
