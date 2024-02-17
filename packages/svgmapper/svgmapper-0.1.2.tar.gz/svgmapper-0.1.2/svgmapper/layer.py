import geopandas as gpd
from svgwrite.container import Group
from svgwrite import Drawing
import tempfile
import webbrowser
from svgmapper.path import Path
from svgmapper.symbol import Symbol
from svgmapper.point import Point
from svgmapper.translate import Translator

class Layer:
    def __init__(
            self,
            name: str,
            path: str = '',
            gdf: gpd.geodataframe = None,
            symbol: Symbol = None,
            crs='epsg:4326'
    ):
        self.path = path
        self.gdf = gpd.read_file(path).to_crs(crs) if path else gdf.to_crs(crs)
        self.symbol = symbol
        self.group = Group(class_=name, id=name)

    def total_bounds(self):
        """Returns total bounds of geodataframe"""
        return self.gdf.total_bounds

    def get_features(self):
        """Returns features of geodataframe using iterrows method"""
        return [feature[1] for feature in self.gdf.iterrows()]

    def to_crs(self, epsg: str):
        """Re-projects coordinate system with provided epgs code"""
        if epsg:
            self.gdf = self.gdf.to_crs(epsg)
        return self

    def clip(self, mask):
        if isinstance(mask, type(self.gdf)):
            self.gdf = self.gdf.clip(mask=mask)
        return self

    def get_layer(self):
        return self._layer

    def get_dwg(self):
        dwg = Drawing()
        dwg.add(self._layer)
        return dwg.tostring()

    def view(self):
        tmp = tempfile.NamedTemporaryFile(delete=False)
        path = tmp.name+'.svg'
        f = open(path, 'w')
        f.write(self.get_dwg())
        f.close()
        webbrowser.open_new('file://' + path)

    def write(self, translator: Translator = None):
        for feature in self.get_features():
            name = 'feature' if 'name' not in feature else feature['name']
            group = Group(id=name.replace(' ', '-'))
            # print(feature)
            geometry = feature['geometry']
            if geometry.geom_type == 'Polygon':
                path = Path(
                    geometry=geometry,
                    translator=translator
                )
                group.add(path.path)
            if geometry.geom_type == 'MultiPolygon':
                for geom in geometry.geoms:
                    path = Path(
                        geometry=geom,
                        translator=translator
                    )
                    group.add(path.path)
            if geometry.geom_type == 'Point':
                point = Point(
                    geometry=geometry,
                    symbol=self.symbol,
                    translator=translator
                ).get_point()
                group.add(point)
            self.group.add(group)

        self._layer = self.group
        return self.group



