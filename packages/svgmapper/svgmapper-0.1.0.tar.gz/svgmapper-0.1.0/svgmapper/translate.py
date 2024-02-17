
class Translator:
    def __init__(self, minx: float, miny: float, scale: float = 1.0):
        self.minx = minx
        self.miny = miny
        self.scale = scale

    def translate(self, x: float, y: float):
        """Returns coordinate pairs (x,y) translated in reference to map minx, miny as defined in viewbox and scale"""
        rounded = lambda n: round(n, 4)
        x = (x - self.minx) * self.scale
        y = 0 - (y - self.miny) * self.scale
        return (rounded(x), rounded(y))