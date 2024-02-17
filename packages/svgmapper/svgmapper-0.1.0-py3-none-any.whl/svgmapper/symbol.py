import svgwrite
from svgpathtools import Path


class Symbol:
    def __init__(
            self,
            id: str,
            size: tuple[int, int],
            paths: list[str],
            stroke: str = 'black',
            stroke_width: int = 1,
            fill: str = 'white'
    ):
        self.id = id
        self.size = size
        self.paths = paths
        self.minx = self.maxx = self.miny = self.maxy = 0
        self.stroke_width = stroke_width
        self.stroke = stroke
        self.fill = fill
        self.dwg = svgwrite.Drawing()
        self.symbol = self.create_symbol()
        self.add_paths()
        self.pad()

    def create_symbol(self):
        return svgwrite.container.Symbol(
            id=self.id,
            fill=self.fill,
            stroke=self.stroke,
            stroke_width=str(self.stroke_width)
        )

    def add_paths(self):
        for path in self.paths:
            p = Path(path)
            _minx, _maxx, _miny, _maxy = p.bbox()
            self.maxx = max(_maxx, self.maxx)
            self.maxy = max(_maxy, self.maxy)
            p = self.dwg.path(d=p.d())
            self.symbol.add(p)

    def pad(self):
        minx = 0 - self.stroke_width / 2
        miny = 0 - self.stroke_width / 2
        maxx = self.maxx + self.stroke_width
        maxy = self.maxy + self.stroke_width
        self.symbol.viewbox(minx, miny, maxx, maxy)

    def get_use(self, insert: tuple[int, int]):
        use = svgwrite.container.Use(
            href=f'#{self.id}',
            insert=insert,
            size=self.size
        )
        use.translate(-(self.size[0]/2), -(self.size[1]))
        return use
