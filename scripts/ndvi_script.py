#!/usr/bin/env python
import matplotlib.pyplot as plt
import numpy as np
from osgeo import gdal
from osgeo import osr

    
def calculate_ndvi ( red_filename, nir_filename ):
    """
    A function to calculate the Normalised Difference Vegetation Index
    from red and near infrarred reflectances. The reflectance data ought to
    be present on two different files, specified by the varaibles 
    `red_filename` and `nir_filename`. The file format ought to be
    recognised by GDAL
    """
    from osgeo import gdal
    g = gdal.Open ( red_filename )
    red = g.ReadAsArray()
    g = gdal.Open ( nir_filename )
    nir = g.ReadAsArray()
    ndvi = ( 1.*nir - red ) / ( 1.*nir + red )
    return ndvi

def save_raster ( output_name, raster_data, dataset, driver="GTiff" ):
    """
    A function to save a 1-band raster using GDAL to the file indicated
    by ``output_name``. It requires a GDAL-accesible dataset to collect 
    the projection and geotransform.
    """
    # Open the reference dataset
    g = gdal.Open ( dataset )
    # Get the Geotransform vector
    geo_transform = g.GetGeoTransform ()
    x_size = g.RasterXSize # Raster xsize
    y_size = g.RasterYSize # Raster ysize
    srs = g.GetProjectionRef () # Projection
    # Need a driver object. By default, we use GeoTIFF
    driver = gdal.GetDriverByName ( driver )
    dataset_out = driver.Create ( output_name, x_size, y_size, 1, \
            gdal.GDT_Float32 )
    dataset_out.SetGeoTransform ( geo_transform )
    dataset_out.SetProjection ( srs )
    dataset_out.GetRasterBand ( 1 ).WriteArray ( \
            raster_data.astype(np.float32) )
    
    
    
def reproject_dataset ( dataset, \
            pixel_spacing=5000., epsg_from=4326, epsg_to=27700 ):
    """
    A sample function to reproject and resample a GDAL dataset from within 
    Python. The idea here is to reproject from one system to another, as well
    as to change the pixel size. The procedure is slightly long-winded, but
    goes like this:
    
    1. Set up the two Spatial Reference systems.
    2. Open the original dataset, and get the geotransform
    3. Calculate bounds of new geotransform by projecting the UL corners 
    4. Calculate the number of pixels with the new projection & spacing
    5. Create an in-memory raster dataset
    6. Perform the projection
    """
    # Define the UK OSNG, see <http://spatialreference.org/ref/epsg/27700/>
    osng = osr.SpatialReference ()
    osng.ImportFromEPSG ( epsg_to )
    wgs84 = osr.SpatialReference ()
    wgs84.ImportFromEPSG ( epsg_from )
    tx = osr.CoordinateTransformation ( wgs84, osng )
    # Up to here, all  the projection have been defined, as well as a 
    # transformation from the from to the  to :)
    # We now open the dataset
    g = gdal.Open ( dataset )
    # Get the Geotransform vector
    geo_t = g.GetGeoTransform ()
    x_size = g.RasterXSize # Raster xsize
    y_size = g.RasterYSize # Raster ysize
    # Work out the boundaries of the new dataset in the target projection
    (ulx, uly, ulz ) = tx.TransformPoint( geo_t[0], geo_t[3])
    (lrx, lry, lrz ) = tx.TransformPoint( geo_t[0] + geo_t[1]*x_size, \
                                          geo_t[3] + geo_t[5]*y_size )
    # See how using 27700 and WGS84 introduces a z-value!
    # Now, we create an in-memory raster
    mem_drv = gdal.GetDriverByName( 'MEM' )
    # The size of the raster is given the new projection and pixel spacing
    # Using the values we calculated above. Also, setting it to store one band
    # and to use Float32 data type.
    dest = mem_drv.Create('', int((lrx - ulx)/pixel_spacing), \
            int((uly - lry)/pixel_spacing), 1, gdal.GDT_Float32)
    # Calculate the new geotransform
    new_geo = ( ulx, pixel_spacing, geo_t[2], \
                uly, geo_t[4], -pixel_spacing )
    # Set the geotransform
    dest.SetGeoTransform( new_geo )
    dest.SetProjection ( osng.ExportToWkt() )
    # Perform the projection/resampling 
    res = gdal.ReprojectImage( g, dest, \
                wgs84.ExportToWkt(), osng.ExportToWkt(), \
                gdal.GRA_Bilinear )
    return dest
    
if __name__ == "__main__":
    red_filename = "red_2005001_uk.vrt"
    nir_filename = "nir_2005001_uk.vrt"
    
    ndvi = calculate_ndvi ( red_filename, nir_filename )
    save_raster ( "./ndvi.tif", ndvi, red_filename )
    # Data is now produced and saved. We can try to open the file and read it
    g = gdal.Open ( "ndvi.tif" )
    # Use the geotransform to 
    geo_t = g.GetGeoTransform()
    print "Raster extends from\n\t Lon: %f to %f" % (  geo_t[0], geo_t[0] + \
                geo_t[1]*g.RasterXSize )
    print "\t Lat: %f to %f" % ( geo_t[3], geo_t[3] + \
                geo_t[5]*g.RasterYSize )
    
    data = g.ReadAsArray ()
    cmap = plt.cm.spectral
    cmap.set_over ( 'w' )
    cmap.set_bad ( 'k' )
    cmap.set_under ( 'k' )
    plt.subplot( 1,2,1 )
    plt.imshow ( data, interpolation='nearest', vmin=0, vmax=0.95, cmap=cmap)

    plt.title("WGS84")
    plt.subplot( 1,2,2 )
    # Now, reproject and resample the NDVI dataset
    reprojected_dataset = reproject_dataset ( "ndvi.tif" )
    # This is a GDAL object. We can read it
    reprojected_data = reprojected_dataset.ReadAsArray ()
    # Let's save it as a GeoTIFF.
    driver = gdal.GetDriverByName ( "GTiff" )
    dst_ds = driver.CreateCopy( "./ndvi_osng.tif", reprojected_dataset, 0 )
    dst_ds = None # Flush the dataset to disk
    # Data is now saved. We can try to open the file and read it
    g = gdal.Open ( "ndvi_osng.tif" )
    # Use the geotransform to 
    geo_t = g.GetGeoTransform()
    print "Raster extends from\n\t Lon: %f to %f" % (  geo_t[0], geo_t[0] + \
        geo_t[1]*g.RasterXSize )
    print "\t Lat: %f to %f" % ( geo_t[3], geo_t[3] + \
        geo_t[5]*g.RasterYSize )
    
    data = g.ReadAsArray ()
    cmap = plt.cm.spectral
    cmap.set_over ( 'w' )
    cmap.set_bad ( 'k' )
    cmap.set_under ( 'k' )
    plt.imshow ( data, interpolation='nearest', vmin=0, vmax=0.95, cmap=cmap)
    plt.colorbar()
    plt.title("OSNG")
    plt.show()