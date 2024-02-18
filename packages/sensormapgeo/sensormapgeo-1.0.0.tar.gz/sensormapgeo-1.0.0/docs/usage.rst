.. _usage:

Usage
=====

Getting started
---------------

The sensormapgeo package transforms a remote sensing image from sensor geometry (image coordinates without
geocoding/projection) to map geometry (projected map coordinates) or vice-versa based on a pixel-wise
longitude/latitude coordinate array.


Transformation from sensor geometry to map geometry
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Here is a simple example how to transform an image from sensor- to map geometry using bilinear resampling and
UTM, zone 32 North as target projection:

.. code-block:: python

    from sensormapgeo import Transformer
    data_mapgeo, geotranform, projection = \
        Transformer(
            lons=longitudes_array,  # 2- or 3-dimensional numpy array of longitudes (3D uses band-specific coordinates)
            lats=latitudes_array,   # 2- or 3-dimensional numpy array of latitudes (3D uses band-specific coordinates)
            resamp_alg='bilinear'   # resampling algorithm to use (default: nearest neighbour)
        ).to_map_geometry(
            data_sensor_geometry,  # numpy array of 2- or 3-dimensional input image in sensor geometry
            tgt_prj=32632          # EPSG code or WKT string of the target projection
        )


Transformation from map geometry to sensor geometry
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

To transform the image from map- to sensor geometry, you need to provide the projection and the geocoding information
(GDAL GeoTransform tuple) of the input image, in addition to the actual input image in map geometry:

.. code-block:: python

    from sensormapgeo import Transformer
    data_sensorgeo = \
        Transformer(
            lons=longitudes_array,  # 2- or 3-dimensional numpy array of longitudes (3D uses band-specific coordinates)
            lats=latitudes_array,   # 2- or 3-dimensional numpy array of latitudes (3D uses band-specific coordinates)
            resamp_alg='bilinear'   # resampling algorithm to use (default: nearest neighbour)
        ).to_sensor_geometry(
            data_map_geometry,      # numpy array of 2- or 3-dimensional input image in map geometry (i.e., projected)
            src_gt=(622600, 30.0, -0.0, 5270000, -0.0, -30.0),   # source GDAL GeoTransform tuple
            src_prj=32632           # EPSG code of source projection, i.e., the projection of data_map_geometry
        )


The Transformer class - detailed API description
------------------------------------------------

In addition to the parameters used in the above examples, there are **many more optional parameters** you may pass to
the :class:`sensormapgeo.Transformer` class or both of the above-mentioned methods. Below, you find a detailed
description of the API:


.. autoclass:: sensormapgeo.Transformer
   :members: to_map_geometry, to_sensor_geometry
   :no-index:
