import os
import urllib2
from zipfile import ZipFile

from osgeo import ogr
from osgeo import osr
from osgeo import gdal

import numpy as np
import matplotlib.pyplot as plt

class GeoException(Exception):
    pass


def reproject_vector ( tx, layer, vector_layer ):
    """
    This function reprojects a layer using a transformation function given by
    `tx`. 
    """
    # Create an in-memory dataset
    target_driver = ogr.GetDriverByName( 'Memory' ) 
    target_datasource = target_driver.CreateDataSource( '' ) 
    # this in-memory vector layer is just a copy of the filtered input, and so
    # ought to have a single feature in this example
    target_datasource.CopyLayer( layer, layer.GetName() )  
    target_layer = target_datasource.GetLayer( vector_layer ) 
    #Now, we "loop" through the original (filtered) layer, and convert 
    # each geometry. 
    for (i, feature ) in enumerate ( layer ): 
        # We get the target feature in the in-memory vector layer
        feature_t = target_layer.GetFeature ( i ) # Ought to be only one after filtering 
        # Get the original feature's geometry
        geom = source_feature.GetGeometryRef ( ) 
        # Clone the original geometry into the in-memory dataset
        target_geometry = geom.Clone() 
        # Transform it
        target_geometry.Transform ( tx )  
        # Update the feature in the output with the transformed geometry
        feature_t.SetGeometry ( target_geometry ) 
    # We return the datasource and the layer. Otherwise, we get a segfault
    return ( target_datasource, target_layer )
    
def temporary_raster ( raster_file ):
    """
    It is simpler to "copy" the raster_file into an in-memory raster. As a 
    further refinement, we set the actual band that will be used as a mask
    """
    tmp_driver = gdal.GetDriverByName ( "MEM" )
    # The datasource is just a copy of the raster_file dataset
    dst_ds = tmp_driver.CreateCopy( '', raster_file, 1 )
    #.Create(raster_file.RasterXSize, raster_file.RasterYSize, 1, gdal.GDT_UInt32 )
    
    # Note that we could have just used a copy of the original, but we might
    # want to set the datatype to something big to store large integers
    
    # However, the mask ought to be 0s with 1s where the vector feature is
    # rasterised. So we read an array from the original, set it to 0
    blanco = raster_file.GetRasterBand(1).ReadAsArray()
    blanco = blanco * 0
    # and we update the in-memory raster to contain only 0s
    dst_ds.GetRasterBand(1).WriteArray ( blanco )
    return dst_ds
    
def reproject_to_raster ( raster_fname, vector_fname, \
            filter_field, filter_value, \
            vector_layer=0 ):
    """
    This function reprojects vector_fname (assumed to have a single layer, like
    ESRI shapefiles, otherwise, set vector_layer to somthing else) to match
    raster_fname. It is assumed that raster_fname does have a projection, in case
    it doesn't, bail out raising an exception
    """
    # Start by creating spatial references for the raster and vector datasets
    raster_srs = osr.SpatialReference()
    vector_srs = osr.SpatialReference()
    # Now, open the raster file
    raster_file = gdal.Open ( raster_fname )
    # Complain if it couldn't open it
    if raster_file is None:
        raise GeoException ("Couldn't open the raster file ->%s<-" % \
                    raster_fname )
    # Get the spatial reference from the raster file
    raster_wkt = raster_file.GetProjectionRef ()
    # Need to test if doesn't exist, but let's just try importing it into 
    # raster_srs
    raster_srs.ImportFromWkt ( raster_wkt )
    
    # Now, open the vector file
    vector_file = ogr.Open ( vector_fname )
    # Filter the vector_layer-th layer using filter_field an filter_value
    layer = vector_file.GetLayer ( vector_layer )
    # Get the vector WKT
    vector_wkt = layer.GetSpatialRef().ExportToWkt()
    vector_srs.ImportFromWkt ( vector_wkt )
    # Set up the coordinate transformation from vector_srs -> rater_srs
    tx = osr.CoordinateTransformation ( vector_srs, raster_srs )
    
    # Filter by attribute
    layer.SetAttributeFilter ( "%s = %s" % ( filter_field, filter_value ) )
    
    # Reproject the filtered raster layer
    ( target_ds, target_layer ) = reproject_vector ( tx, layer, vector_layer )
    
    # At this stage target_layer is an in-memory raster where the single
    # feature that it contains has a geometry that has been reprojected
    # using tx
    dst_ds = temporary_raster ( raster_file )
    # Now, we produce an in-memory raster dataset, where we will store the 
    # "mask"
    # This is the bit that does the rasterisation
    err = gdal.RasterizeLayer ( dst_ds, [1], target_layer, burn_values=[1L] )
    # If all went well, we can fish the rasterised data from dst_ds:
    mascara = dst_ds.GetRasterBand(1).ReadAsArray()
    # Return the mask array
    return mascara
        
        
    
if __name__ == "__main__":
    shp_url = "http://txpub.usgs.gov/USACE/data/water_resources/" + \
              "Hydrologic_Units.zip"
    hdf_url = "http://www2.geog.ucl.ac.uk/~plewis/geogg122/_images/" + \
            "MCD15A2.A2011185.h09v05.005.2011213154534.hdf"
    if not os.path.exists ( \
        "/tmp/MCD15A2.A2011185.h09v05.005.2011213154534.hdf" ):
        request = urllib2.Request( hdf_url )
        response = urllib2.urlopen( request )
        data = response.read()
        fp = open ( "/tmp/MCD15A2.A2011185.h09v05.005.2011213154534.hdf", 'w' )
        fp.write ( data )
        fp.close()
    
    if not os.path.exists ("/tmp/Hydrologic_Units/" ):
        request = urllib2.Request( shp_url )
        response = urllib2.urlopen( request )
        data = response.read()
        fp = open ( "/tmp/HydrologicUnits.zip", 'w' )
        fp.write ( data )
        fp.close()
        z = ZipFile ( "/tmp/HydrologicUnits.zip" )
        for f in z.namelist():
            z.extract( f, path="/tmp/")
            
            
    raster_fname = 'HDF4_EOS:EOS_GRID:' + \
        '"/tmp/MCD15A2.A2011185.h09v05.005.2011213154534.hdf":' + \
        'MOD_Grid_MOD15A2:Lai_1km'
        
    vector_fname = "/tmp/Hydrologic_Units/HUC_Polygons.shp"
    my_data = reproject_to_raster ( raster_fname, vector_fname, \
        "HUC", "13010001" )
    plt.imshow ( my_data )
    plt.show()