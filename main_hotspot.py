import fiona
from shapely.geometry import shape
import emerging_hotspot_factor
country = r'U:\egoldman\hs_2015_update\test_aoi.shp'

with fiona.open(country, 'r') as country_file:
    for country in country_file:
        geometry = shape(country['geometry'])
        properties = country['properties']
        #properties = "test"
        emerging_hotspot_factor.emerging_hs_points(geometry, properties)