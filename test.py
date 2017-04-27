import fiona

meta = fiona.open(r'U:\egoldman\hs_2015_update\footprint.shp').meta
with fiona.open(r'U:\egoldman\hs_2015_update\merge.shp', 'w', **meta) as output:
	for features in fiona.open(r'U:\egoldman\hs_2015_update\footprint.shp'):
		output.write(features)
	output.close()