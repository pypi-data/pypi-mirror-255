# -*- coding: utf-8 -*-

# sensormapgeo, Transform remote sensing images between sensor and map geometry.
#
# Copyright (C) 2020-2024
# - Daniel Scheffler (GFZ Potsdam, daniel.scheffler@gfz-potsdam.de)
# - Helmholtz Centre Potsdam - GFZ German Research Centre for Geosciences Potsdam,
#   Germany (https://www.gfz-potsdam.de/)
#
# This software was developed within the context of the EnMAP project supported
# by the DLR Space Administration with funds of the German Federal Ministry of
# Economic Affairs and Energy (on the basis of a decision by the German Bundestag:
# 50 EE 1529) and contributions from DLR, GFZ and OHB System AG.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#   https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Module to transform 2D or 3D arrays between sensor and map geometry based on a single-band geolayer."""

from typing import Union, Tuple
from multiprocessing import cpu_count
from uuid import uuid4

import numpy as np
from osgeo import gdal, osr  # noqa
from pyproj import CRS
from py_tools_ds.dtypes.conversion import dTypeDic_NumPy2GDAL

from ..utils import corner_coords_lonlat_to_extent, move_extent_to_coordgrid


class GDALTransformer2D(object):
    def __init__(self,
                 lons: np.ndarray,
                 lats: np.ndarray,
                 resamp_alg: str = 'nearest',
                 georef_convention: str = 'PIXEL_CENTER',
                 nprocs: int = cpu_count()
                 ) -> None:
        """Get an instance of GDALTransformer2D.

        :param lons:                2D longitude array corresponding to the 2D sensor geometry array
        :param lats:                2D latitude array corresponding to the 2D sensor geometry array
        :param resamp_alg:          resampling algorithm ('nearest', 'bilinear', 'cubic', 'cubic_spline',
                                    'lanczos', 'average', 'mode', 'max', 'min', 'med', 'q1', 'q3')
        :param georef_convention:   specifies to which pixel position the given coordinates refer
                                    ('PIXEL_CENTER' (pyresample implementation) or 'TOP_LEFT_CORNER')
        :param nprocs:              number of processor cores to be used
        """
        # validation
        if lons.ndim != 2:
            raise ValueError(f'Expected a 2D longitude array. Received a {lons.ndim}D array.')
        if lats.ndim != 2:
            raise ValueError(f'Expected a 2D latitude array. Received a {lats.ndim}D array.')
        if lons.shape != lats.shape:
            raise ValueError((lons.shape, lats.shape), "'lons' and 'lats' are expected to have the same shape.")
        if georef_convention not in ['PIXEL_CENTER', 'TOP_LEFT_CORNER']:
            raise ValueError(georef_convention, "'georef_convention' must be 'PIXEL_CENTER' or 'TOP_LEFT_CORNER'.")

        self.resamp_alg = resamp_alg
        self.lats = lats
        self.lons = lons
        self.georef_convention = georef_convention
        self.nprocs = nprocs

    def _get_target_extent(self, tgt_epsg: int):
        corner_coords_ll = [[self.lons[0, 0], self.lats[0, 0]],  # UL_xy
                            [self.lons[0, -1], self.lats[0, -1]],  # UR_xy
                            [self.lons[-1, 0], self.lats[-1, 0]],  # LL_xy
                            [self.lons[-1, -1], self.lats[-1, -1]],  # LR_xy
                            ]
        tgt_extent = corner_coords_lonlat_to_extent(corner_coords_ll, tgt_epsg)

        return tgt_extent

    def to_map_geometry(self,
                        data: np.ndarray,
                        tgt_prj: Union[str, int],
                        tgt_extent: Tuple[float, float, float, float] = None,
                        tgt_res: Tuple = None,
                        tgt_coordgrid: Tuple[Tuple, Tuple] = None,
                        src_nodata: int = None,
                        tgt_nodata: int = None
                        ) -> Tuple[np.ndarray, tuple, str]:
        """Transform the input sensor geometry array into map geometry.

        - GDAL Autotest suite: https://github.com/rouault/gdal/blob/master/autotest/gcore/geoloc.py

        :param data:            2D or 3D numpy array (representing sensor geometry) to be warped to map geometry
        :param tgt_prj:         target projection (WKT or 'epsg:1234' or <EPSG_int>)
        :param tgt_extent:      extent coordinates of output map geometry array (LL_x, LL_y, UR_x, UR_y) in the tgt_prj
        :param tgt_res:         target X/Y resolution (e.g., (30, 30))
        :param tgt_coordgrid:   target coordinate grid ((x, x), (y, y)):
                                if given, the output extent is moved to this coordinate grid and tgt_res is obsolete
        :param src_nodata:      no-data value of the input array to be ignored in resampling
        :param tgt_nodata:      value for undetermined pixels in the output
        """
        if data.ndim not in [2, 3]:
            raise ValueError(data.ndim, "'data' must have 2 or 3 dimensions.")

        if data.shape[:2] != self.lons.shape[:2]:
            raise ValueError(data.shape, 'Expected a sensor geometry data array with %d rows and %d columns.'
                             % self.lons.shape[:2])

        rows, cols = data.shape[:2]
        bands = 1 if data.ndim == 2 else data.shape[2]
        gdal_dtype = dTypeDic_NumPy2GDAL[str(np.dtype(data.dtype))]
        gdal_dtype_gl = dTypeDic_NumPy2GDAL[str(np.dtype(self.lons.dtype))]
        tgt_wkt = CRS(tgt_prj).to_wkt(version='WKT1_GDAL')
        wgs84_wkt = osr.GetUserInputAsWKT('WGS84')

        uuid = uuid4().hex  # needed to avoid conflicts in 3D mode when running via threading backend
        p_geoloc_tmp = f'/vsimem/{uuid}_lons_lats.tif'
        p_data_tmp = f'/vsimem/{uuid}_data.tif'
        p_data_mapgeo = f'/vsimem/{uuid}_data_mapgeo.tif'
        drv = gdal.GetDriverByName('GTiff')

        # set up GEOLOCATION dataset
        with drv.Create(p_geoloc_tmp, cols, rows, 2, gdal_dtype_gl) as ds_geoloc:
            ds_geoloc.GetRasterBand(1).WriteArray(self.lons)
            ds_geoloc.GetRasterBand(2).WriteArray(self.lats)

        # set up source dataset in sensor geometry
        with drv.Create(p_data_tmp, cols, rows, bands, gdal_dtype) as ds_sensorgeo:
            for i in range(bands):
                data_band = data if bands == 1 else data[:, :, i]
                ds_sensorgeo.GetRasterBand(i + 1).WriteArray(data_band)

            # add geolocation information to input data
            ds_sensorgeo.SetMetadata(
                dict(
                    SRS=wgs84_wkt,
                    X_DATASET=p_geoloc_tmp,
                    Y_DATASET=p_geoloc_tmp,
                    X_BAND='1',
                    Y_BAND='2',
                    PIXEL_OFFSET='0',
                    LINE_OFFSET='0',
                    PIXEL_STEP='1',
                    LINE_STEP='1',
                    GEOREFERENCING_CONVENTION=self.georef_convention
                ),
                'GEOLOCATION'
            )

        # warp from geolocation arrays and read the result
        tgt_epsg = CRS(tgt_prj).to_epsg()
        tgt_extent = tgt_extent or self._get_target_extent(tgt_epsg)

        if tgt_coordgrid:
            tgt_extent = move_extent_to_coordgrid(tgt_extent, *tgt_coordgrid)
            tgt_res = (abs(tgt_coordgrid[0][1] - tgt_coordgrid[0][0]),
                       abs(tgt_coordgrid[1][1] - tgt_coordgrid[1][0]))

        # for performance optimization see https://github.com/OpenDroneMap/ODM/issues/778
        warpOptions = gdal.WarpOptions(
            format='GTIFF',  # VRT causes blurry output: https://github.com/OSGeo/gdal/issues/7750
            outputBounds=tgt_extent,  # bounds of output are exactly as given
            outputBoundsSRS=tgt_wkt,  # FIXME not needed?
            xRes=tgt_res[0] if tgt_res else None,
            yRes=tgt_res[1] if tgt_res else None,
            # targetAlignedPixels=True,  # not needed if outputBounds are given
            errorThreshold=0,
            srcSRS=wgs84_wkt,
            dstSRS=tgt_wkt,
            geoloc=True,
            resampleAlg=self.resamp_alg,
            warpOptions=[f'NUM_THREADS={self.nprocs}'] if self.nprocs > 1 else [],
            # warpOptions=['XSCALE=1', 'YSCALE=1']  # needed when using VRT
            # creationOptions=['NUM_THREADS=ALL_CPUS', 'BLOCKXSIZE=256', 'BLOCKYSIZE=256'],  # only slows it down
            multithread=self.nprocs > 1,
            warpMemoryLimit=2000,  # avoid ERROR 1: Too many points failed to transform, unable to compute output bounds
            outputType=gdal_dtype,
            workingType=gdal_dtype,
            srcNodata=src_nodata,
            dstNodata=tgt_nodata
        )

        with gdal.config_option('GDAL_CACHEMAX', str(2000)):
            gdal.Warp(p_data_mapgeo, p_data_tmp, options=warpOptions)

        # read the warped data
        with gdal.Open(p_data_mapgeo) as ds_mapgeo:
            data_mapgeo = \
                ds_mapgeo.ReadAsArray().astype(data.dtype) if bands == 1 else \
                ds_mapgeo.ReadAsArray().transpose(1, 2, 0).astype(data.dtype)
            out_gt = ds_mapgeo.GetGeoTransform()
            out_prj = ds_mapgeo.GetProjection()

        return data_mapgeo, out_gt, out_prj

    def to_sensor_geometry(self,
                           data: np.ndarray,
                           src_gt: Tuple[float, float, float, float, float, float],
                           src_prj: Union[str, int],
                           src_nodata: int = None,
                           tgt_nodata: int = None
                           ) -> np.ndarray:
        """Transform the input map geometry array into sensor geometry.

        :param data:        2D or 3D numpy array (representing map geometry) to be warped to sensor geometry
        :param src_gt:      GDAL GeoTransform tuple of the input map geometry array
        :param src_prj:     projection of the input map geometry array (WKT or 'epsg:1234' or <EPSG_int>)
        :param src_nodata:  no-data value of the input array to be ignored in resampling
        :param tgt_nodata:  value for undetermined pixels in the output
        """
        if data.ndim not in [2, 3]:
            raise ValueError(data.ndim, "'data' must have 2 or 3 dimensions.")

        uuid = uuid4().hex  # needed to avoid conflicts in 3D mode when running via threading backend
        p_geoloc_tmp = f'/vsimem/{uuid}_lons_lats.tif'
        p_data_tmp = f'/vsimem/{uuid}_data.tif'
        p_data_sensorgeo = f'/vsimem/{uuid}_data_sensorgeo.tif'

        wgs84_wkt = osr.GetUserInputAsWKT('WGS84')
        src_wkt = CRS(src_prj).to_wkt(version='WKT1_GDAL')

        # set up GEOLOCATION dataset
        drv = gdal.GetDriverByName('GTiff')
        rows_sg, cols_sg = self.lons.shape
        gdal_dtype_gl = dTypeDic_NumPy2GDAL[str(np.dtype(self.lons.dtype))]
        with drv.Create(p_geoloc_tmp, cols_sg, rows_sg, 2, gdal_dtype_gl) as ds_geoloc:
            ds_geoloc.GetRasterBand(1).WriteArray(self.lons)
            ds_geoloc.GetRasterBand(2).WriteArray(self.lats)

        # set up source dataset in map geometry
        rows_mg, cols_mg = data.shape[:2]
        bands_mg = 1 if data.ndim == 2 else data.shape[2]
        gdal_dtype = dTypeDic_NumPy2GDAL[str(np.dtype(data.dtype))]

        with drv.Create(p_data_tmp, cols_mg, rows_mg, bands_mg, gdal_dtype) as ds_mapgeo:
            for i in range(bands_mg):
                data_band = data if bands_mg == 1 else data[:, :, i]
                ds_mapgeo.GetRasterBand(i + 1).WriteArray(data_band)

            ds_mapgeo.SetGeoTransform(src_gt)
            ds_mapgeo.SetProjection(src_wkt)

        # set up target dataset in sensor geometry with associated GEOLOCATION metadata
        # -> documentation at https://gdal.org/development/rfc/rfc4_geolocate.html
        with drv.Create(p_data_sensorgeo, cols_sg, rows_sg, bands_mg, gdal_dtype) as ds_sensorgeo:
            ds_sensorgeo.SetMetadata(
                dict(
                    SRS=wgs84_wkt,
                    X_DATASET=p_geoloc_tmp,
                    Y_DATASET=p_geoloc_tmp,
                    X_BAND='1',
                    Y_BAND='2',
                    PIXEL_OFFSET='0',
                    LINE_OFFSET='0',
                    PIXEL_STEP='1',
                    LINE_STEP='1',
                    GEOREFERENCING_CONVENTION=self.georef_convention
                ),
                'GEOLOCATION'
            )

        # for performance optimization see https://github.com/OpenDroneMap/ODM/issues/778
        # - custom creation options do not speed it up (would have to be added to the dataset creation above)
        warpOptions = gdal.WarpOptions(
            errorThreshold=0,
            resampleAlg=self.resamp_alg,
            warpOptions=[f'NUM_THREADS={self.nprocs}'] if self.nprocs > 1 else [],
            # warpOptions=['XSCALE=1', 'YSCALE=1']  # needed when using VRT
            multithread=self.nprocs > 1,
            warpMemoryLimit=2000,  # avoid ERROR 1: Too many points failed to transform, unable to compute output bounds
            workingType=gdal_dtype,
            srcNodata=src_nodata,
            dstNodata=tgt_nodata
        )

        # warp the data from map to sensor geometry
        with gdal.Open(p_data_sensorgeo, gdal.GA_Update) as ds_sensorgeo:
            with gdal.config_option('GDAL_CACHEMAX', str(2000)):
                gdal.Warp(ds_sensorgeo, p_data_tmp, options=warpOptions)

            # read the warped data
            data_sensorgeo = \
                ds_sensorgeo.ReadAsArray().astype(data.dtype) if bands_mg == 1 else \
                ds_sensorgeo.ReadAsArray().transpose(1, 2, 0).astype(data.dtype)

        return data_sensorgeo
