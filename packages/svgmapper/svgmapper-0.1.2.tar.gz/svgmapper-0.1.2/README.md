# svgmapper
`svgmapper` generates SVG maps from `.geojson` files, Esri shapefiles, and geopandas geodataframes. 
Below is a bried overview of how to use `svgmapper` and a description of its classes and methods.

## Creating a map

```python
from svgmapper import Map, Layer

Map(
    name="Map of US and Canada",
    css='map.css',
    epsg='epsg:2163',
    size=(504, 504),
    layers=[
        Layer(
            name='usa-states',
            path='north-america/usa-states.geojson'
        ),
        Layer(
            name='ca-provinces',
            path='north-america/canada-provinces.geojson'
        )
    ]
).save('north-america.svg')

```
The code snippet above initializes a new map object with the specified Layers 
(the drawing order of which is determined by the Layer's index in the provided list). That Map is then
saved to the specified location in the `save()` method. The output map looks like below:

![SVG map of Canada provinces and US states](./north-america.svg)

