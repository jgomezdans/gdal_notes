
********************************************        
Reprojecting and resampling data
********************************************

A common problem
------------------


The previous section demonstrated how to save raster data. However, in many cases, there's a need to reproject and resample this data. A pragmtic solution would use `gdalwarp <http://www.gdal.org/gdalwarp.html>`_ and do this on the shell. On the one hand, this is convenient, but sometimes, you need to perform this task as a intermediate step, and creating and deleting files is tedious and error-prone. Ideally, you would have a python function that would perform the projection for you. GDAL allows this by defining *in-memory raster files*. These are normal GDAL datasets, but that don't exist on the filesystem, only in the computer's memory. They are a convenient "scratchpad" for quick intermediate calculations. GDAL also makes available a function, ``gdal.ReprojectImage`` that exposes most of the abilities of gdalwarp. We shall combine these two tricks to carry out the reprojection. As an example, we shall look at the case where the NDVI data for the British Isles mentioned in the previous section needs to be reprojected to the Ordnance Survey National Grid, an appropriate projection for the UK.

The main complication comes from the need of ``gdal.ReprojectImage`` to operate on GDAL datasets. In the previous section, we saved the NDVI data to a GeoTIFF file, so this gives us a starting dataset. We still need to create the output dataset. This means that we need to define the geotransform and size of the output dataset before the projection is made. This entails gathering information on the extent of the original dataset, projecting it to the destination projection, and calculating the number of pixels and geotransform parameters from there. This is a (heavily commented) function that performs just that task:

    .. literalinclude:: ../scripts/ndvi_script.py
        :language: python
        :pyobject: reproject_dataset

The function returns a GDAL in-memory file object, where you can ``ReadAsArray`` etc. As it stands, ``reproject_dataset`` does not write to disk. However, we can save the in-memory raster to any format supported by GDAL very conveniently by making a copy of the dataset. This literally takes two lines of code.

We expand the main part of the program to (i) save the result of the reprojection as a GeoTIFF file, (ii) read the resulting datafile and (iii) plot it:
    
    .. literalinclude:: ../scripts/ndvi_script.py
        :language: python
        :lines: 123-146
        
The result of running the whole script is shown below

    .. figure:: fig_5.*
        :scale: 50
    
    
Try it out
^^^^^^^^^^^^^^^^^^

#. Compare the produced NDVI with the official one in the HDF product (extract the area of interest to a VRT file).
#. Have a look at the QA flags (you may find `this table <http://gis.cri.fmach.it/modis-ndvi-evi/>`_ useful). Antyhing interesting? 
#. In the NDVI directory there's NDVI data for a whole year. Can you plot an annual series of NDVI?
#. The NDVI HDF files also have a blue band, that you can use to calculate the EVI (Enhanced Vegetation Index). The formula for this is index `can be found here <http://en.wikipedia.org/wiki/EVI>`_. Repeat the above exercise with the EVI, and compare EVI and NDVI results.
