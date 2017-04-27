import fiona
import os
from shapely.geometry import shape
from shapely.geometry import mapping
import arcpy
import os
def select_tiles(country, properties, masks):
    footprint = r'U:\egoldman\hs_2015_update\footprint.shp'
    # set schema
    mask_tile = os.path.join(masks, "00N_000E.shp")
    meta= fiona.open(mask_tile).meta

    # open mask collection for writing
    mask_collection = r'U:\egoldman\hs_2015_update\mask_collection.shp'

    with fiona.open(mask_collection, 'w', **meta) as mask_write:

        tile_in_country_list = []
        # open both input datasets
        with fiona.open(footprint, 'r') as grid:
            # compare each feature in dataset 1 and 2
            for g in grid:
                tileid = g['properties']['Name'][-8:]
                #properties = g['properties']

                # print tile ID if geometry intersects
                if shape(g['geometry']).intersects(country):
                    tile_in_country = tileid[-8:]
                    mask_tile = os.path.join(masks, tile_in_country + ".shp")

                    with fiona.open(mask_tile, 'r') as mask_file:
                        for mask in mask_file:

                            mask_geometry = shape(mask['geometry'])
                            mask_properties = mask['properties']
                            country_properties = {"test": "this is a column"}
                            print country
                            print shape(mask['geometry'])
                            mask_write.write({'geometry': mapping(shape(mask['geometry'].intersection(country))), 'properties': mask_properties})
                                             ## 'geometry': mapping(shape(g['geometry']).intersection(shape(i['geometry']))), 'properties': prop})


        return tile_in_country_list


def create_mask(tile_list, masks):
    arcpy.Clip_analysis(tile_path, geometry)

    first_tile_name = tile_list[0]
    first_tile_path = os.path.join(masks, first_tile_name + ".shp")
    meta = fiona.open(first_tile_path).meta

    with fiona.open(r'U:\egoldman\hs_2015_update\merge.shp', 'w', **meta) as merged_tiles:
        for tile in tile_list:
            tile_path = os.path.join(masks, tile + ".shp")
            for features in fiona.open(tile_path):
                merged_tiles.write(features)
        merged_tiles.close()