#make sure to have remapped TCD mosaic(0-31 as NoData, 31-101 as 1)
#remap loss 0 values to NoData. Keep all other values
#set indir to AOI (country or other AOI)

import os
import arcpy
from arcpy.sa import *
import timeit

#''' Section 1: Set environments ##############################################################################'''
arcpy.CheckOutExtension("Spatial")
arcpy.env.overwriteOutput = "TRUE"

#''' Section 2: Set directories ##############################################################################'''
indir = r'U:\egoldman\forest_masks\peru_mask_simp.shp'
maindir = r'U:\egoldman\forest_masks'
geodatabase = r'U:\egoldman\forest_masks\results.gdb'
outdir = os.path.join(geodatabase,"outdir")

#'''Section 3: set path to mosaic files #################################################################'''
lossyearmosaic = r'U:\egoldman\mosaics_updated.gdb\loss15'
tcdmosaic = r'U:\egoldman\mosaics_updated.gdb\tcd'
hansenareamosaic = r'U:\egoldman\mosaics_updated.gdb\area'

#'''Section 4: Set environments (part 2) #####################################################################'''
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
tic=timeit.default_timer()
arcpy.AddMessage( "     extracting by mask")
outExtractbyMask = ExtractByMask(lossyearmosaic,indir)

#multiply to get loss within 30% tree cover density
arcpy.AddMessage( "     multiplying")
outMult =outExtractbyMask*Raster(tcdmosaic)

#convert to point
arcpy.AddMessage( "     converting to point")
outpoint = os.path.join(geodatabase,f+"_hs_points")
arcpy.RasterToPoint_conversion(outMult,outpoint, "VALUE")

#project
sr = 32662 #EPSG code for Plate Carree Projection
outprj = os.path.join(geodatabase,f+ "_hs_points_prj")
out_coordinate_system = arcpy.SpatialReference(sr)
arcpy.Project_management(outpoint,outprj, out_coordinate_system)

#Add loss year date
arcpy.AddMessage( "     adding columns")
arcpy.AddField_management(outprj, "date", "DATE")

arcpy.AddMessage( "     calculating date")
layer = arcpy.MakeFeatureLayer_management(outprj, "aoi_lyr")
arcpy.SelectLayerByAttribute_management(layer,"NEW_SELECTION", "GRID_CODE <10")
arcpy.CalculateField_management(layer, field="date", expression=""""1/1/200"+str(!GRID_CODE!)""", expression_type="PYTHON_9.3", code_block="")

arcpy.SelectLayerByAttribute_management(layer,"NEW_SELECTION", "GRID_CODE >=10")
arcpy.CalculateField_management(layer, field="date", expression=""""1/1/20"+str(!GRID_CODE!)""", expression_type="PYTHON_9.3", code_block="")

