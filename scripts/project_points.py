#!/usr/bin/env python

from osgeo import ogr
from osgeo import osr
"""
SYNOPSIS

project_points.py

DESCRIPTION

A script to convert longitude latitude coordinates in WGS84 to the MODIS 
sinusoidal projection using GDAL. Currently it uses a big string, but can you 
modify it to take data in a file, or make it into a function?

AUTHOR

Jose Gomez-Dans <j.gomez-dans@geog.ucl.ac.uk>

LICENSE

This script is in the public domain, free from copyrights or restrictions.

VERSION

1.0
"""



# The next line defines the data as a string
# as would be for example if read from a file etc.
park_data = """Dartmoor national park,             -3.904,              50.58
New forest national park,             -1.595,              50.86
Exmoor national park,             -3.651,              51.14
Pembrokeshire coast national park,             -4.694,              51.64
Brecon beacons national park,             -3.432,              51.88
Pembrokeshire coast national park,              -4.79,              51.99
Norfolk and suffolk broads,              1.569,              52.62
Snowdonia national park,             -3.898,               52.9
Peak district national park,             -1.802,               53.3
Yorkshire dales national park,             -2.157,              54.23
North yorkshire moors national park,            -0.8855,              54.37
Lake district national park,             -3.084,              54.47
Galloway forest park,             -4.171,              54.87
Galloway forest park,             -4.191,              55.18
Galloway forest park,             -4.379,              55.28
Northumberland national park,             -2.228,              55.28
Loch lomond & the trossachs national park,            -4.593,              56.24
Tay forest park,             -4.025,              56.59
Cairngorms national park,             -3.545,              57.08"""

# Define the source projection, WGS84 lat/lon. 
wgs84 = osr.SpatialReference( ) # Define a SpatialReference object
wgs84.ImportFromEPSG( 4326 ) # And set it to WGS84 using the EPSG code

# Now for the target projection, MODIS sinusoidal
modis_sinu = osr.SpatialReference() # define the SpatialReference object
# In this case, we get the projection from a Proj4 string
modis_sinu.ImportFromProj4 ( \
                "+proj=sinu +R=6371007.181 +nadgrids=@null +wktext")

# Now, we define a coordinate transformtion object, *from* wgs84 *to* modis_sinu
tx = osr.CoordinateTransformation( wgs84, modis_sinu )
# We loop over the lines of park_data, 
#         using the split method to split by newline characters
for linea in park_data.split( "\n" ):
    # Split linea by spacing
    park_name, lon, lat = linea.split(",")
    # Convert longitude and latitude values to floats
    # they are strings at the moment
    lon = float ( lon )
    lat = float ( lat )
    # Actually do the transformation using the TransformPoint method
    modis_x, modis_y, modis_z = tx.TransformPoint ( lon, lat )
    # Print out
    print park_name, lon, lat, modis_x, modis_y
