import svgwrite
import geopandas as gpd
from svgmapper.layer import Layer
from symbol import Symbol
from translate import Translator

class Map:
    def __init__(
            self,
            name: str,
            layers: list[Layer],
            css: str = '',
            epsg: str = 'epsg:4326',
            mask: str = None,
            symbols: list[Symbol] = None,
            size=None,
            padding=0
    ):
        self.name = name
        self.mask = mask
        self.epsg = epsg
        self.layers = self.clip_layers(layers)
        self.size = size
        self.css = css
        self.minx, self.miny, self.maxx, self.maxy = self.get_bounds()
        self.dwg = self.init_drawing()
        self.symbols = symbols
        self.translator = Translator(self.minx, self.miny, scale=self.get_scale())
        self.padding = padding
        self.group = self.dwg.add(svgwrite.container.Group())
        if self.symbols: self.add_syms()

    def get_bounds(self):
        minx = miny = maxx = maxy = 0
        for layer in self.layers:
            _minx, _miny, _maxx, _maxy = layer.total_bounds()
            minx = _minx if _minx < minx else minx
            miny = _miny if _miny < miny else miny
            maxx = _maxx if _maxx > maxx else maxx
            maxy = _maxy if _maxy > maxy else maxy
        return [minx, miny, maxx, maxy]

    def clip_layers(self, layers):
        if self.mask:
            mask = gpd.read_file(self.mask).to_crs(self.epsg).buffer(0)
            return [layer.to_crs(self.epsg).clip(mask) for layer in layers]
        else:
            return [layer.to_crs(self.epsg) for layer in layers]

    def add_syms(self):
        [self.dwg.defs.add(s.symbol) for s in self.symbols]

    def get_scale(self):
        if not self.size: return 1
        width_delta = self.size[0] / (self.maxx - self.minx)
        height_delta = self.size[1] / (self.maxy - self.miny)
        return min(height_delta, width_delta)

    def get_viewbox(self):
        if self.size:
            return f'0 {0 - (self.size[1])} {self.size[0]} {self.size[1]} '
        return f'0 {0 - (self.maxy - self.miny)} {self.maxx - self.minx} {self.maxy - self.miny}'

    def init_drawing(self):
        return svgwrite.Drawing(
            f'file.svg',
            size = self.size,
            viewBox=self.get_viewbox(),
            id='map',
            style='padding: 10px'
        )

    def center(self):
        max_x, max_y = self.translator.translate(self.maxx, self.maxy)
        x = round((self.size[0] - abs(max_x))/2)
        y = round((self.size[1] - abs(max_y))/2)
        x = 0 - x if max_x < 0 else x
        y = 0 - y if max_y < 0 else y
        self.group.translate(x, y)

    def write(self):
        if self.size: self.center()
        for layer in self.layers:
            lyr = layer.write(self.translator)
            self.group.add(lyr)

    def save(self, filename: str):
        self.write()
        if self.css:
            with open(self.css) as f:
                css = f.read()
            self.dwg.embed_stylesheet(css)
        self.dwg.saveas(filename=filename)
