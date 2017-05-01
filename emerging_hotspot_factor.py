#make sure to have remapped TCD mosaic(0-31 as NoData, 31-101 as 1)
#remap loss 0 values to NoData. Keep all other values
#set indir to AOI (country or other AOI)
#create geodatabase for results

import os
import arcpy
from arcpy.sa import *
import datetime

import utilities

def emerging_hs_points(country_shapefile, datadir, iso):
    #''' Section 2: Set directories ###############################################################################'''
    maindir = r'U:\egoldman\hs_2015_update'
    geodatabase = r'U:\egoldman\hs_2015_update\results.gdb'
    outdir = os.path.join(geodatabase,"outdir")
    tile_grid = r'U:\egoldman\hs_2015_update\footprint.shp'
    masks = r'S:\masks'

    #'''Section 3: set path to mosaic files #######################################################################'''
    lossyearmosaic = r'U:\egoldman\mosaics_updated.gdb\loss15'
    tcdmosaic = r'U:\egoldman\mosaics_updated.gdb\tcd'
    hansenareamosaic = r'U:\egoldman\mosaics_updated.gdb\area'

    #create tcd country masks
    print " creating tile list"
    tile_list = utilities.select_tiles(country_shapefile, tile_grid)

    print " clipping masks"
    clipped_mask_list = utilities.clipped_mask_list(tile_list, country_shapefile, datadir)

    print " merging masks"
    merged_country_mask = utilities.merge_clipped_masks(clipped_mask_list, datadir, iso)

    print " simplifying mask"
    simplified_mask = utilities.merge_polygon_simplify(merged_country_mask, datadir, iso)

    start = datetime.datetime.now()

    #''' Section 1: Set environments ##############################################################################'''
    arcpy.CheckOutExtension("Spatial")
    arcpy.env.overwriteOutput = "TRUE"

    #'''Section 4: Set environments (part 2) ######################################################################'''
    scratch_gdb = os.path.join(maindir,"scratch.gdb")
    if not os.path.exists(scratch_gdb):
        arcpy.CreateFileGDB_management(maindir,"scratch.gdb")
    scratch_workspace = os.path.join(maindir,"scratch.gdb")
    arcpy.env.scratchWorkspace = scratch_workspace
    arcpy.env.workspace = outdir
    arcpy.env.snapRaster = hansenareamosaic

    #'''Section 5: main body of script ############################################################################'''
    country_file = simplified_mask
    f = os.path.basename(country_file).split(".")[0]
    #extract by AOI
    arcpy.AddMessage( "     extracting by mask")
    country_loss_30tcd = ExtractByMask(lossyearmosaic,country_file)
    mosaic_country_loss_30tcd = utilities.create_mosaic(country_loss_30tcd, scratch_gdb)

    # define our remap table
    remap_table = os.path.join(datadir, "hs_function_table.dbf")
    year_remap_function = os.path.join(datadir, "remap_loss_year.rft.xml")
    # loop over years 1-15
    for short_year in range(1,16):
        print("\nPROCESSING RASTER VALUE {} (YEAR = {})".format(short_year, 2000 + short_year))
        #reclassify per year
        utilities.update_remap_table(remap_table, short_year)

        # update reclass function using table
        utilities.update_reclass_function(mosaic_country_loss_30tcd, year_remap_function)

        #aggregate cell by factor
        arcpy.AddMessage ( "     aggregate")
        cell_factor = 80
        aggregate_raster = Aggregate(mosaic_country_loss_30tcd, cell_factor, "SUM", "TRUNCATE", "DATA")
        #raster to point
        arcpy.AddMessage ('     raster to point')
        #points_name = f + '_year_' + str(short_year)
        temp_points = os.path.join(scratch_workspace, f)
        all_points = os.path.join(geodatabase, f + "_all_points")
        arcpy.RasterToPoint_conversion(aggregate_raster, temp_points, "Value")
        #add date for individual year
        arcpy.AddMessage("     adding date")
        arcpy.AddField_management(temp_points, "date", "DATE")
        date_for_points = "\"01/01/{}\"".format(2000 + short_year)
        print date_for_points
        print temp_points
        arcpy.CalculateField_management(temp_points, "date", date_for_points, "PYTHON")
        #create point feature class or append to existing
        if arcpy.Exists(all_points):
            arcpy.Append_management(temp_points, all_points)
        else:
            sr = 32662  # EPSG code for Plate Carree
            arcpy.CreateFeatureclass_management(geodatabase, f + "_all_points", "POINT", template=temp_points,
                                                spatial_reference=sr)
            arcpy.Append_management(temp_points, all_points)
        arcpy.Delete_management(temp_points)



    end = datetime.datetime.now() - start
    arcpy.AddMessage("EHS prep tool took this long: " + str(end))