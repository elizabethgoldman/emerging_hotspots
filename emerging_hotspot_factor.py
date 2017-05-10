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
    tile_grid = r'U:\egoldman\hs_2015_update\footprint.shp'

    #'''Section 3: set path to mosaic files #######################################################################'''
    lossyearmosaic = r'U:\egoldman\mosaics_updated.gdb\loss15'
    hansenareamosaic = r'U:\egoldman\mosaics_updated.gdb\area'

    #create tcd country masks
    start = datetime.datetime.now()

    print " creating tile list"
    tile_list = utilities.select_tiles(country_shapefile, tile_grid)

    print " clipping masks"
    clipped_mask_list = utilities.clipped_mask_list(tile_list, country_shapefile, datadir)

    print " merging masks"
    merged_country_mask = utilities.merge_clipped_masks(clipped_mask_list, datadir, iso)

    print " simplifying mask"
    simplified_mask = utilities.merge_polygon_simplify(merged_country_mask, datadir, iso)

    #''' Section 1: Set environments ##############################################################################'''
    arcpy.CheckOutExtension("Spatial")
    arcpy.env.overwriteOutput = "TRUE"

    #'''Section 4: Set environments (part 2) ######################################################################'''
    scratch_gdb = os.path.join(datadir,"scratch.gdb")
    if not os.path.exists(scratch_gdb):
        arcpy.CreateFileGDB_management(datadir, "scratch.gdb")
    scratch_workspace = os.path.join(datadir, "scratch.gdb")
    results_gdb = os.path.join(datadir, "results.gdb")
    if not os.path.exists(results_gdb):
        arcpy.CreateFileGDB_management(datadir, "results.gdb")
    arcpy.env.scratchWorkspace = scratch_workspace
    arcpy.env.workspace = datadir
    arcpy.env.snapRaster = hansenareamosaic

    #'''Section 5: main body of script ############################################################################'''
    country_file = merged_country_mask
    f = os.path.basename(country_file).split(".")[0]
    # extract by AOI
    arcpy.AddMessage( "     extracting by mask")
    country_loss_30tcd = ExtractByMask(lossyearmosaic,country_file)
    country_loss_30tcd.save(r'U:\egoldman\scripts\emerging_hotspots\data\scratch.gdb\extract')
    mosaic_country_loss_30tcd = utilities.create_mosaic(country_loss_30tcd, scratch_gdb)

    # define remap table
    remap_table = os.path.join(datadir, "hs_function_table.dbf")
    year_remap_function = os.path.join(datadir, "remap_loss_year.rft.xml")
    # loop over years 1-15
    for short_year in range(1, 16):
        print("\nPROCESSING RASTER VALUE {} (YEAR = {})".format(short_year, 2000 + short_year))
        # reclassify per year
        utilities.update_remap_table(remap_table, short_year)

        # update reclass function using table
        utilities.update_reclass_function(mosaic_country_loss_30tcd, year_remap_function)

        # aggregate cell by factor
        print "     aggregate"
        loss_aggregate = utilities.aggregate(mosaic_country_loss_30tcd)

        # raster to point
        print "     raster to point"
        temp_points = utilities.raster_to_point(scratch_gdb, f, results_gdb, loss_aggregate)

        # add date for individual year
        print "     adding date"
        utilities.add_date(temp_points, short_year)

        # create point feature class or append to existing
        all_points = utilities.create_append_fc(results_gdb, f, temp_points)

    # create space time cube
    #all_points = r'U:\egoldman\scripts\emerging_hotspots\data\results.gdb\UGA_merged_mask_all_points'
    print "       space time cube"
    cube = utilities.create_space_time_cube(all_points, datadir, f)

    # create hot spot analysis
    print "       create hot spots"
    utilities.create_hot_spots(cube, datadir, f, simplified_mask)


    end = datetime.datetime.now() - start
    arcpy.AddMessage("EHS took this long: " + str(end))