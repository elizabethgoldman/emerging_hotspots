import fiona
import os
from shapely.geometry import shape
from shapely.geometry import mapping
import arcpy
import os
def select_tiles(country, footprint):
    tile_list = []
    with fiona.open(footprint, 'r') as grid:
        with fiona.open(country, 'r') as country:

            # compare each feature in dataset 1 and 2
            for g in grid:
                tileid = g['properties']['Name'][-8:]
                for i in country:
                    # print tile ID if geometry intersects
                    if shape(g['geometry']).intersects(shape(i['geometry'])):
                        #print "{}: intersects".format(tileid)
                        tile_list.append(tileid)
                    else:
                        pass
                        #print "{}: doesn't intersect".format(tileid)
    return tile_list


def clipped_mask_list(tile_list, country_shapefile, datadir):
    clipped_list = []
    for tileid in tile_list:
        mask_tile = os.path.join(r"s:\masks", tileid + ".shp")
        clipped_mask = tileid + "_clip.shp"
        clipped_mask_path = os.path.join(datadir, clipped_mask)
        arcpy.Clip_analysis(mask_tile,country_shapefile, clipped_mask_path)
        clipped_list.append(clipped_mask_path)
    return clipped_list

def merge_clipped_masks(clipped_list, datadir, iso):
    merged_masks = os.path.join(datadir, iso + "_merged_mask.shp")
    arcpy.Merge_management(clipped_list, merged_masks)
    return merged_masks

def merge_polygon_simplify(merged_masks, datadir, iso):
    simp_masks = os.path.join(datadir, iso + "_tcd_mask.shp")
    arcpy.SimplifyPolygon_cartography(merged_masks, simp_masks, "BEND_SIMPLIFY", "500 Meters", "100 Hectares")
    return simp_masks
