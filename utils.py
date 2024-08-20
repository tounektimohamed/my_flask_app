import pyproj
from shapely.geometry import shape, mapping
from shapely.ops import transform

def convert_utm_to_wgs(geojson_data):
    # Define projections (example for UTM zone 33N)
    utm_proj = pyproj.CRS('EPSG:22332')
    wgs84_proj = pyproj.CRS('EPSG:4326')

    # Transform coordinates
    project = pyproj.Transformer.from_crs(utm_proj, wgs84_proj, always_xy=True).transform

    for feature in geojson_data['features']:
        geom = shape(feature['geometry'])
        geom_wgs84 = transform(project, geom)
        feature['geometry'] = mapping(geom_wgs84)

    return geojson_data
