from svgwrite.container import Group
from shapely import Point
from translate import Translator
from symbol import Symbol


class Point:
    def __init__(
            self,
            geometry: Point,
            name: str = '',
            symbol: Symbol = None,
            translator: Translator = None
    ):
        self.symbol = symbol
        self.name = name
        self.geometry = geometry
        self.translator = translator
        self.write()

    def translate(self):
        if self.translator:
            coords = self.translator.translate(self.geometry.x, self.geometry.y)
        else:
            coords = (self.geometry.x, self.geometry.y)
        return coords

    def get_point(self):
        return self._point

    def write(self):
        coords = self.translate()
        if self.symbol:
            point = self.symbol.get_use(insert=coords)
        else:
            point = self.dwg.circle(
                center=(coords[0], coords[1]),
                r='3px',
                fill='red',
                stroke='white',
                stroke_width='0.5px'
            )
        self._point = point