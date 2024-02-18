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

"""Module to transform 2D or 3D arrays between sensor and map geometry based on a single- or multi-band geolayer."""

from typing import Union, Tuple
from multiprocessing import cpu_count
from warnings import warn

import numpy as np
from osgeo import gdal, osr  # noqa
from pyresample.geometry import AreaDefinition

from .gdal_backend import GDALTransformer2D, GDALTransformer3D
from .pyresample_backend import PyresampleTransformer2D, PyresampleTransformer3D


default_options_gdal = dict(
    georef_convention='PIXEL_CENTER'
)
default_options_pyresample_2d = dict()
default_options_pyresample_3d = dict(
    mp_alg='auto'
)


class Transformer(object):
    def __init__(self,
                 lons: np.ndarray,
                 lats: np.ndarray,
                 backend='gdal',
                 resamp_alg: str = 'nearest',
                 nprocs: int = cpu_count(),
                 **options
                 ) -> None:
        """Get an instance of Transformer.

        :param lons:
            2D or 3D longitude array (3D array allows specific transformations per band)

        :param lats:
            2D or 3D latitude array (3D array allows specific transformations per band)

        :param backend:
            'gdal' or 'pyresample'

        :param resamp_alg:
            resampling algorithm

            The 'gdal' backend supports:
                'nearest', 'near', 'bilinear', 'cubic', 'cubic_spline',
                'lanczos', 'average', 'mode', 'max', 'min', 'med', 'q1', 'q3'

            The 'pyresample' backend supports:
                'nearest', 'bilinear', 'gauss', 'custom'

        :param nprocs:
            number of processor cores to be used

        :param options:
            Additional options for configuring the Transformer.
            See the possible keys depending on the chosen backend below.


        **Possible options in case of the gdal backend:**

        :key georef_convention:
            specifies to which pixel position the given coordinates refer
             ('PIXEL_CENTER' (corresponds to pyresample implementation) or 'TOP_LEFT_CORNER')


        **Possible options in case of the pyresample backend:**

        :key mp_alg:
            multiprocessing algorithm [ONLY in case of 3D geolayers] (default: auto)

                - 'bands': parallelize over bands using multiprocessing lib
                - 'tiles': parallelize over tiles using OpenMP
                - 'auto': automatically choose the algorithm

        :key radius_of_influence:
            <float> Cut off distance in meters (default: pixel size in meters for nearest,
            gauss, and custom resampling; 1.5 * pixelsize for bilinear resampling)

        :key sigmas:
            <list of floats or float> [ONLY 'gauss'] List of sigmas to use for the gauss
            weighting of each channel 1 to k, w_k = exp(-dist^2/sigma_k^2). If only one channel
            is resampled sigmas is a single float value.

        :key neighbours:
            <int> [ONLY 'bilinear', 'gauss'] Number of neighbours to consider for each grid
            point when searching the closest corner points

        :key epsilon:
            <float> Allowed uncertainty in meters. Increasing uncertainty reduces execution time

        :key weight_funcs:
            <list of function objects or function object> [ONLY 'custom'] List of weight
            functions f(dist) to use for the weighting of each channel 1 to k. If only one
            channel is resampled weight_funcs is a single function object.

        :key reduce_data:
            <bool> Perform initial coarse reduction of source dataset in order to reduce
            execution time

        :key segments:
            <int or None> Number of segments to use when resampling.
            If set to None an estimate will be calculated

        :key with_uncert:
            <bool> [ONLY 'gauss' and 'custom'] Calculate uncertainty estimates

            NOTE: resampling function has 3 return values instead of 1: result, stddev, count

        .. note::
           Refer to the `Pyresample API reference <https://pyresample.readthedocs.io/en/latest/api/pyresample.html>`__
           for a complete list of options.
        """
        if lons.ndim == lats.ndim:
            self.dims_ll = lats.ndim
        else:
            raise ValueError("'lons' and 'lats' must have the same shape.")

        self.lats = lats
        self.lons = lons
        self.backend = backend
        self.resamp_alg = resamp_alg
        self.nprocs = nprocs

        if backend == 'gdal':
            self.init_options = default_options_gdal.copy()
            transformer = \
                GDALTransformer2D if self.dims_ll == 2 else \
                GDALTransformer3D

            gdal_rsp_algs = ['nearest', 'near', 'bilinear', 'cubic', 'cubic_spline',
                             'lanczos', 'average', 'mode', 'max', 'min', 'med', 'q1', 'q3']
            if resamp_alg not in gdal_rsp_algs:
                raise ValueError(resamp_alg, f"The 'gdal' backend supports the following resampling algorithms: "
                                             f"{', '.join(gdal_rsp_algs)}, but not {resamp_alg}.")

        elif backend == 'pyresample':
            if self.dims_ll == 2:
                self.init_options = default_options_pyresample_2d.copy()
                transformer = PyresampleTransformer2D
            else:
                self.init_options = default_options_pyresample_3d.copy()
                transformer = PyresampleTransformer3D

            pyresample_rsp_algs = ['nearest', 'bilinear', 'gauss', 'custom']
            if resamp_alg not in pyresample_rsp_algs:
                raise ValueError(resamp_alg, f"The 'pyresample' backend supports the following resampling algorithms: "
                                             f"{', '.join(pyresample_rsp_algs)}, but not {resamp_alg}.")

        else:
            raise ValueError(backend, f"Unknown backend '{backend}'. Choose either 'gdal' or 'pyresample'.")

        if options:
            for k in options:
                self.init_options[k] = options[k]

        self._transformer = (
            transformer(
                lons=self.lons,
                lats=self.lats,
                resamp_alg=self.resamp_alg,
                nprocs=self.nprocs,
                **self.init_options
            )
        )

    def to_map_geometry(self,
                        data: np.ndarray,
                        tgt_prj: Union[str, int],
                        tgt_extent: Tuple[float, float, float, float] = None,
                        tgt_res: Tuple = None,
                        tgt_coordgrid: Tuple[Tuple, Tuple] = None,
                        src_nodata: int = None,
                        tgt_nodata: int = None,
                        area_definition: AreaDefinition = None
                        ) -> Tuple[np.ndarray, tuple, str]:
        """Transform the input sensor geometry array into map geometry.

        :param data:            2D or 3D numpy array (representing sensor geometry) to be warped to map geometry
        :param tgt_prj:         target projection (WKT or 'epsg:1234' or <EPSG_int>)
        :param tgt_extent:      extent coordinates of output map geometry array (LL_x, LL_y, UR_x, UR_y) in the tgt_prj
        :param tgt_res:         target X/Y resolution (e.g., (30, 30))
        :param tgt_coordgrid:   target coordinate grid ((x, x), (y, y)):
                                if given, the output extent is moved to this coordinate grid and tgt_res is obsolete
        :param area_definition: an instance of pyresample.geometry.AreaDefinition;
                                OVERRIDES tgt_prj, tgt_extent and tgt_res; saves computation time for the pyresample
                                backend, ignored if the GDAL backend is used
        :param src_nodata:      no-data value of the input array to be ignored in resampling
        :param tgt_nodata:      value for undetermined pixels in the output
        """
        if self.backend == 'gdal':
            if area_definition:
                warn("The 'area_definition' parameter is only used by the pyresample backend "
                     "but ignored for the GDAL backend.", RuntimeWarning)

            self._transformer: Union[GDALTransformer2D, GDALTransformer3D]
            data_mapgeo, out_gt, out_prj = (
                self._transformer.to_map_geometry(
                    data=data,
                    tgt_prj=tgt_prj,
                    tgt_extent=tgt_extent,
                    tgt_res=tgt_res,
                    tgt_coordgrid=tgt_coordgrid,
                    src_nodata=src_nodata,
                    tgt_nodata=tgt_nodata
                )
            )

        else:  # pyresample
            self._transformer: Union[PyresampleTransformer2D, PyresampleTransformer3D]
            data_mapgeo, out_gt, out_prj = (
                self._transformer.to_map_geometry(
                    data=data,
                    tgt_prj=tgt_prj,
                    tgt_extent=tgt_extent,
                    tgt_res=tgt_res,
                    tgt_coordgrid=tgt_coordgrid,
                    area_definition=area_definition,
                    src_nodata=src_nodata,
                    tgt_nodata=tgt_nodata
                )
            )

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
        data_sensorgeo = (
            self._transformer.to_sensor_geometry(
                data=data,
                src_gt=src_gt,
                src_prj=src_prj,
                src_nodata=src_nodata,
                tgt_nodata=tgt_nodata
            )
        )

        return data_sensorgeo
