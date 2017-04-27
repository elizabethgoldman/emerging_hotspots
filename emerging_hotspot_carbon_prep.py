#make sure to have remapped TCD layer (0-10 as NoData, >10 as 1)
#set indir to AOI (country or other AOI)

import os
import arcpy
from arcpy.sa import *

#''' Section 1: Set environments ##############################################################################'''
arcpy.CheckOutExtension("Spatial")
arcpy.env.overwriteOutput = "TRUE"

#''' Section 2: Set directories ##############################################################################'''
indir = r'U:\egoldman\peru_hotspots\peru_amazon_final_simp4.shp'
#------------------------------------
maindir = r'U:\egoldman\peru_hotspots'
geodatabase = r'U:\egoldman\peru_hotspots\results3.gdb'
outdir = os.path.join(geodatabase,"outdir")

#'''Section 3: set path to mosaic files #################################################################'''
lossyearmosaic = r'U:\egoldman\mosaics_updated.gdb\loss'
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
# change buffer distance to suit aoi of script.
# arcpy.AddMessage( "     buffering aoi")
f = os.path.basename(indir).split(".")[0]
# buff_distance=arcpy.GetParameterAsText(2)
# outbuff =os.path.join(maindir,f+"_buff.shp")
# arcpy.Buffer_analysis(indir, outbuff, str(buff_distance)+ ' Kilometers')

arcpy.AddMessage( "     extracting by mask")
outExtractbyMask = ExtractByMask(lossyearmosaic,indir)

arcpy.AddMessage( "     multiplying")
outMult =outExtractbyMask*Raster(tcdmosaic)

arcpy.AddMessage( "     converting to point")
outpoint = os.path.join(geodatabase,f+"_hs_points")
arcpy.RasterToPoint_conversion(outMult,outpoint, "VALUE")

#arcpy.AddMessage( "     projecting")
outprj = os.path.join(geodatabase,f+ "_hs_points_prj")
out_coordinate_system = arcpy.SpatialReference('Eckert IV (world)')
arcpy.Project_management(outpoint,outprj, out_coordinate_system)

arcpy.AddMessage( "     adding columns")
arcpy.AddField_management(outprj, "date", "DATE")

arcpy.AddMessage( "     calculating date")
layer = arcpy.MakeFeatureLayer_management(outprj, "aoi_lyr")
arcpy.SelectLayerByAttribute_management(layer,"NEW_SELECTION", "GRID_CODE <10")
arcpy.CalculateField_management(layer, field="date", expression=""""1/1/200"+str(!GRID_CODE!)""", expression_type="PYTHON_9.3", code_block="")

arcpy.SelectLayerByAttribute_management(layer,"NEW_SELECTION", "GRID_CODE >=10")
arcpy.CalculateField_management(layer, field="date", expression=""""1/1/20"+str(!GRID_CODE!)""", expression_type="PYTHON_9.3", code_block="")
#

#arcpy.AddMessage( "     create space time cuuuube")
#netcdf = os.path.join(maindir,f+"_hs.nc")
#arcpy.CreateSpaceTimeCube_stpm(outprj,netcdf,"date","","1 Years","","","2.5 Kilometers")
#arcpy.AddMessage( "     create emerging hotspots")
#hotspots = os.path.join(maindir,f+"_hs_final.shp")
#arcpy.EmergingHotSpotAnalysis_stpm(netcdf,"COUNT",hotspots, "20 Kilometers",1)