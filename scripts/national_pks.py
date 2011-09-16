from osgeo import ogr
from osgeo import osr


wgs84 = osr.SpatialReference()
wgs84.ImportFromEPSG(4326)

gb = osr.SpatialReference()

f = ogr.Open ( "UK_NationalPark.shp" )
layer = f.GetLayer ( 0 )
gb.ImportFromWkt( layer.GetSpatialRef().ExportToWkt() )
park_name_old="stuff"
print "==========================================   ================  ===================="
print " Park name                                   Longitude [deg]   Latitude [deg]     "
print "==========================================   ================  ===================="
for feat in layer:
    park_name =  feat.GetFieldAsString(6).capitalize()
    if park_name != park_name_old and park_name != "":
        geom = feat.GetGeometryRef()
        geom.AssignSpatialReference( gb )
        gc = geom.Centroid()
        gc.AssignSpatialReference( gb )
        gc.TransformTo ( wgs84 )
        lon = gc.GetX()
        lat = gc.GetY()
        print "%41s   %16.4g   %16.4g" % (park_name, lon, lat)
    park_name_old = park_name
print "==========================================   ================  ===================="