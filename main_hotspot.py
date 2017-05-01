import emerging_hotspot_factor
import arcpy
import os
arcpy.env.overwriteOutput = True
country = r'U:\egoldman\hs_2015_update\test_aoi.shp'
current_dir = os.path.dirname(os.path.realpath(__file__))
datadir = os.path.join(current_dir, "data")
arcpy.env.worksapce = datadir

fields = ["ISO"]
with arcpy.da.SearchCursor(country, fields) as cursor:
        for row in cursor:
            iso = row[0]
            print "running code for {}".format(iso)
            where = '"ISO" = ' + "'{}'".format(iso)
            country_selection = "country_selection"
            country_shapefile = os.path.join(datadir, "country_shapefile.shp")
            arcpy.Select_analysis(country, country_shapefile, where)

            emerging_hotspot_factor.emerging_hs_points(country_shapefile, datadir, iso)
