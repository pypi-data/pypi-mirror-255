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

"""Module to transform 3D arrays between sensor and map geometry (using band-wise Lon/Lat arrays)."""

from typing import Union, Tuple
from multiprocessing import cpu_count
import gc

import numpy as np
from osgeo import gdal  # noqa
from joblib import Parallel, delayed
from joblib import parallel_config
from py_tools_ds.dtypes.conversion import dTypeDic_NumPy2GDAL

from .transformer_2d import GDALTransformer2D


class GDALTransformer3D(object):
    def __init__(self,
                 lons: np.ndarray,
                 lats: np.ndarray,
                 resamp_alg: str = 'nearest',
                 georef_convention: str = 'PIXEL_CENTER',
                 nprocs: int = cpu_count()
                 ) -> None:
        """Get an instance of GDALTransformer3D.

        :param lons:                3D longitude array corresponding to the 3D sensor geometry array
        :param lats:                3D latitude array corresponding to the 3D sensor geometry array
        :param resamp_alg:          resampling algorithm ('nearest', 'bilinear', 'cubic', 'cubic_spline',
                                    'lanczos', 'average', 'mode', 'max', 'min', 'med', 'q1', 'q3')
        :param georef_convention:   specifies to which pixel position the given coordinates refer
                                    ('PIXEL_CENTER' (pyresample implementation) or 'TOP_LEFT_CORNER')
        :param nprocs:              number of processor cores to be used
        """
        # validation
        if lons.ndim != 3:
            raise ValueError(f'Expected a 3D longitude array. Received a {lons.ndim}D array.')
        if lats.ndim != 3:
            raise ValueError(f'Expected a 3D latitude array. Received a {lats.ndim}D array.')
        if lons.shape != lats.shape:
            raise ValueError((lons.shape, lats.shape), "'lons' and 'lats' are expected to have the same shape.")

        self.lats = lats
        self.lons = lons
        self.resamp_alg = resamp_alg
        self.georef_convention = georef_convention
        self.cpus = nprocs

    def to_map_geometry(self,
                        data: np.ndarray,
                        tgt_prj: Union[str, int],
                        tgt_extent: Tuple[float, float, float, float] = None,
                        tgt_res: Tuple = None,
                        tgt_coordgrid: Tuple[Tuple, Tuple] = None,
                        src_nodata: int = None,
                        tgt_nodata: int = None,
                        ) -> Tuple[np.ndarray, Tuple[float, float, float, float, float, float], str]:
        """Transform the input sensor geometry array into map geometry.

        - GDAL Autotest suite: https://github.com/rouault/gdal/blob/master/autotest/gcore/geoloc.py

        :param data:            numpy array (representing sensor geometry) to be warped to map geometry
        :param tgt_prj:         target projection (WKT or 'epsg:1234' or <EPSG_int>)
        :param tgt_extent:      extent coordinates of output map geometry array (LL_x, LL_y, UR_x, UR_y) in the tgt_prj
        :param tgt_res:         target X/Y resolution (e.g., (30, 30))
        :param tgt_coordgrid:   target coordinate grid ((x, x), (y, y)):
                                if given, the output extent is moved to this coordinate grid
        :param src_nodata:      no-data value of the input array to be ignored in resampling
        :param tgt_nodata:      value for undetermined pixels in the output
        """
        if data.ndim != 3:
            raise ValueError(data.ndim, "'data' must have 3 dimensions.")

        if data.shape != self.lons.shape:
            raise ValueError(data.shape, 'Expected a sensor geometry data array with %d rows, %d columns, and %d bands.'
                             % self.lons.shape)

        nbands = data.shape[2]

        def _to_map_geometry_2d(bidx: int):
            band_mapgeo, band_gt, band_prj = (
                GDALTransformer2D(
                    lons=self.lons[:, :, bidx],
                    lats=self.lats[:, :, bidx],
                    resamp_alg=self.resamp_alg,
                    georef_convention=self.georef_convention,
                    nprocs=1  # using more than 1 here implies sub-multiprocessing which slows it extremely down
                ).to_map_geometry(
                    data=data[:, :, bidx],
                    tgt_prj=tgt_prj,
                    tgt_extent=tgt_extent,
                    tgt_res=tgt_res,
                    tgt_coordgrid=tgt_coordgrid,
                    src_nodata=src_nodata,
                    tgt_nodata=tgt_nodata
                )
            )
            drv = gdal.GetDriverByName('GTiff')
            rows_out, cols_out = band_mapgeo.shape
            gdal_dtype = dTypeDic_NumPy2GDAL[str(np.dtype(band_mapgeo.dtype))]
            p_out = f'/vsimem/band_{bidx}.tif'

            with drv.Create(p_out, cols_out, rows_out, 1, gdal_dtype) as ds:
                ds.GetRasterBand(1).WriteArray(band_mapgeo)
                ds.SetGeoTransform(band_gt)
                ds.SetProjection(band_prj)

            gc.collect()  # free up memory (unclear if this has an effect)

            return p_out

        # NOTE: Using multiprocessing + imap_unordered + initializer is ~40% faster but requires to hold
        #       the complete 3D lons/lats/data in memory which is only feasible on machines with a lot of RAM.
        #       Instead, joblib makes it easy to share the variables ('sharedmem') and /vsimem/ of the threads
        #       is directly accessible from the main process. Threading is faster that processes here.
        with parallel_config(backend='threading', prefer='threads', n_jobs=self.cpus, require='sharedmem'):
            bandlist_mapgeo = list(
                Parallel(return_as='generator')(
                    delayed(_to_map_geometry_2d)(i) for i in range(nbands)))

        # create a VRT from all surface reflectance bands
        # vrt_options = gdal.BuildVRTOptions(srcNodata=0)
        with gdal.BuildVRT('/vsimem/data_mapgeo.tif',
                           bandlist_mapgeo,
                           separate=True
                           ) as ds_mapgeo:
            ds_mapgeo: gdal.Dataset
            data_mapgeo = ds_mapgeo.ReadAsArray().transpose(1, 2, 0).astype(data.dtype)
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

        :param data:        numpy array (representing map geometry) to be warped to sensor geometry
        :param src_gt:      GDAL GeoTransform tuple of the input map geometry array
        :param src_prj:     projection of the input map geometry array (WKT or 'epsg:1234' or <EPSG_int>)
        :param src_nodata:  no-data value of the input array to be ignored in resampling
        :param tgt_nodata:  value for undetermined pixels in the output
        """
        if data.ndim != 3:
            raise ValueError(data.ndim, "'data' must have 3 dimensions.")

        if data.shape[2] != self.lons.shape[2]:
            raise ValueError(data.shape[2], f'Expected a map geometry data array with {self.lons.shape[2]} bands.')

        nbands = data.shape[2]

        def _to_sensor_geometry_2d(bidx: int) -> str:
            band_sensorgeo = \
                GDALTransformer2D(
                    lons=self.lons[:, :, bidx],
                    lats=self.lats[:, :, bidx],
                    resamp_alg=self.resamp_alg,
                    georef_convention=self.georef_convention,
                    nprocs=1  # using more than 1 here implies sub-multiprocessing which slows it extremely down
                ).to_sensor_geometry(
                    data=data[:, :, bidx],
                    src_gt=src_gt,
                    src_prj=src_prj,
                    src_nodata=src_nodata,
                    tgt_nodata=tgt_nodata,
                )

            drv = gdal.GetDriverByName('GTiff')
            rows_out, cols_out = band_sensorgeo.shape
            gdal_dtype = dTypeDic_NumPy2GDAL[str(np.dtype(band_sensorgeo.dtype))]
            p_out = f'/vsimem/band_{bidx}.tif'

            with drv.Create(p_out, cols_out, rows_out, 1, gdal_dtype) as ds:
                ds.GetRasterBand(1).WriteArray(band_sensorgeo)

            gc.collect()  # free up memory (unclear if this has an effect)

            return p_out

        # NOTE: Using multiprocessing + imap_unordered + initializer is ~40% faster but requires to hold
        #       the complete 3D lons/lats/data in memory which is only feasible on machines with a lot of RAM.
        #       Instead, joblib makes it easy to share the variables ('sharedmem') and /vsimem/ of the threads
        #       is directly accessible from the main process. Threading is faster that processes here.
        with parallel_config(backend='threading', prefer='threads', n_jobs=self.cpus, require='sharedmem'):
            bandlist_sensorgeo = list(
                Parallel(return_as='generator')(
                    delayed(_to_sensor_geometry_2d)(i) for i in range(nbands)))

        # create a VRT from all surface reflectance bands
        # vrt_options = gdal.BuildVRTOptions(srcNodata=0)
        with gdal.BuildVRT('/vsimem/data_sensorgeo.tif', bandlist_sensorgeo, separate=True) as ds_sensorgeo:
            ds_sensorgeo: gdal.Dataset
            data_sensorgeo = ds_sensorgeo.ReadAsArray().transpose(1, 2, 0).astype(data.dtype)

        return data_sensorgeo
