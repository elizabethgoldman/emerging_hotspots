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

def update_remap_table(remap_table, shortyear):
    with arcpy.da.UpdateCursor(remap_table, "from_") as cursor:
        for row in cursor:
            row[0] = shortyear
            cursor.updateRow(row)

def update_reclass_function(lossyearmosaic, year_remap_function):
    print "removing function"
    arcpy.EditRasterFunction_management(lossyearmosaic, "EDIT_MOSAIC_DATASET", "REMOVE", year_remap_function)
    print "inserting function"
    arcpy.EditRasterFunction_management(lossyearmosaic, "EDIT_MOSAIC_DATASET", "INSERT", year_remap_function)

def create_mosaic(country_loss_30tcd, scratch_gdb):
    out_cs = arcpy.SpatialReference(4326)
    mosaic_name = "mosaic_country_loss_30tcd"
    mosaic_path = os.path.join(scratch_gdb, mosaic_name)
    arcpy.CreateMosaicDataset_management(scratch_gdb, mosaic_name, out_cs)
    arcpy.AddRastersToMosaicDataset_management(mosaic_path, "Raster Dataset", country_loss_30tcd)
    return os.path.join(scratch_gdb, mosaic_name)
