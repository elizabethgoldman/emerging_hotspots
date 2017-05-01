#make sure to have remapped TCD mosaic(0-31 as NoData, 31-101 as 1)
#remap loss 0 values to NoData. Keep all other values
#set indir to AOI (country or other AOI)
#create geodatabase for results

import os
import arcpy
from arcpy.sa import *
import datetime

start = datetime.datetime.now()

#''' Section 1: Set environments ##############################################################################'''
arcpy.CheckOutExtension("Spatial")
arcpy.env.overwriteOutput = "TRUE"

#''' Section 2: Set directories ###############################################################################'''
indir = r'U:\egoldman\hs_2015_update\small_test_aoi.shp'
maindir = r'U:\egoldman\hs_2015_update'
geodatabase = r'U:\egoldman\hs_2015_update\results.gdb'
outdir = os.path.join(geodatabase,"outdir")

#'''Section 3: set path to mosaic files #######################################################################'''
lossyearmosaic = r'U:\egoldman\mosaics_updated.gdb\loss15'
tcdmosaic = r'U:\egoldman\mosaics_updated.gdb\tcd'
hansenareamosaic = r'U:\egoldman\mosaics_updated.gdb\area'

#'''Section 4: Set environments (part 2) ######################################################################'''
scratch_gdb = os.path.join(maindir,"scratch.gdb")
if not os.path.exists(scratch_gdb):
    arcpy.CreateFileGDB_management(maindir,"scratch.gdb")
scratch_workspace = os.path.join(maindir,"scratch.gdb")
arcpy.env.scratchWorkspace = scratch_workspace
arcpy.env.workspace = outdir
arcpy.env.snapRaster = hansenareamosaic

#'''Section 5: main body of script ############################################################################'''
f = os.path.basename(indir).split(".")[0]
#extract by AOI
arcpy.AddMessage( "     extracting by mask")
outExtractbyMask = ExtractByMask(lossyearmosaic,indir)
#multiply to get loss within 30% tree cover density
arcpy.AddMessage( "     multiplying")
outMult =outExtractbyMask*Raster(tcdmosaic)
#loop through years of loss data
value_years = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15]
for short_year in value_years:
    print("\nPROCESSING RASTER VALUE {} (YEAR = {})".format(short_year, 2000 + short_year))
    count = 1
    #reclassify per year
    arcpy.AddMessage ("     reclassify")
    reclass_raster = Reclassify(outMult, "Value", RemapValue([[short_year, 1]]),"NODATA")
    #aggregate cell by factor
    arcpy.AddMessage ( "     aggregate")
    cell_factor = 80
    aggregate_raster = Aggregate(reclass_raster, cell_factor, "SUM", "TRUNCATE", "DATA")
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
    arcpy.CalculateField_management(temp_points, "date", date_for_points)
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