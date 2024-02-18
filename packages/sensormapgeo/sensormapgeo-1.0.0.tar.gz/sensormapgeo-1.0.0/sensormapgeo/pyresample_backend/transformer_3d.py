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
from warnings import warn
import warnings
import gc

import numpy as np
from osgeo import gdal  # noqa
from joblib import Parallel, delayed
from joblib import parallel_config
from pyproj import CRS

with warnings.catch_warnings():
    # work around https://github.com/pytroll/pyresample/issues/375
    warnings.simplefilter('ignore', UserWarning)
    from pyresample import AreaDefinition

from py_tools_ds.dtypes.conversion import dTypeDic_NumPy2GDAL
from py_tools_ds.geo.coord_trafo import transform_any_prj

from .transformer_2d import PyresampleTransformer2D
from ..utils import corner_coords_lonlat_to_extent, move_extent_to_coordgrid, get_validated_tgt_res
from ..version import __version__ as _libver


class PyresampleTransformer3D(object):
    def __init__(self,
                 lons: np.ndarray,
                 lats: np.ndarray,
                 resamp_alg: str = 'nearest',
                 nprocs: int = cpu_count(),
                 mp_alg: str = 'auto',
                 **opts) -> None:
        """Get an instance of PyresampleTransformer3D.

        :param lons:
            3D longitude array corresponding to the 3D sensor geometry array

        :param lats:
            3D latitude array corresponding to the 3D sensor geometry array

        :key resamp_alg:
            resampling algorithm ('nearest', 'bilinear', 'gauss', 'custom')

        :key nprocs:
            <int>, Number of processor cores to be used (default: all cores available)

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
        # validation
        if lons.ndim != 3:
            raise ValueError('Expected a 3D longitude array. Received a %dD array.' % lons.ndim)
        if lats.ndim != 3:
            raise ValueError('Expected a 3D latitude array. Received a %dD array.' % lats.ndim)
        if lons.shape != lats.shape:
            raise ValueError((lons.shape, lats.shape), "'lons' and 'lats' are expected to have the same shape.")

        self.lats = lats
        self.lons = lons
        self.resamp_alg = resamp_alg
        self.nprocs = nprocs if not nprocs > cpu_count() else cpu_count()
        self.opts = opts

        if 'fill_value' in self.opts:
            warn("In sensormapgeo 1.0.0, the 'fill_value' parameter was removed when initializing the transformer "
                 "class. Use 'src_nodata' and 'tgt_nodata' in the methods 'to_map_geometry' and 'to_sensor_geometry.",
                 DeprecationWarning)
            del self.opts['fill_value']

        # define number of CPUs to use (but avoid sub-multiprocessing)
        #   -> parallelize either over bands or over image tiles
        #      bands: multiprocessing uses joblib, implemented in to_map_geometry / to_sensor_geometry
        #      tiles: multiprocessing uses OpenMP implemented in pykdtree which is used by pyresample
        if mp_alg == 'auto':
            if self.lons.shape[2] >= self.nprocs:
                self.mp_alg = 'bands'
            else:
                self.mp_alg = 'tiles'
        else:
            self.mp_alg = mp_alg

        # in the bands case, avoid sub-multiprocessing in
        # PyresampleTransformer2D as PyresampleTransformer3D does the multiprocessing
        if self.mp_alg == 'bands':
            self._nprocs_3d = self.nprocs
            self._nprocs_2d = 1
        else:
            self._nprocs_3d = 1
            self._nprocs_2d = self.nprocs

    def _get_common_target_extent(self,
                                  tgt_epsg: int,
                                  tgt_coordgrid: Tuple[Tuple, Tuple] = None):
        if tgt_epsg == 4326:
            corner_coords_ll = [[self.lons[0, 0, :].min(), self.lats[0, 0, :].max()],  # common UL_xy
                                [self.lons[0, -1, :].max(), self.lats[0, -1, :].max()],  # common UR_xy
                                [self.lons[-1, 0, :].min(), self.lats[-1, 0, :].min()],  # common LL_xy
                                [self.lons[-1, -1, :].max(), self.lats[-1, -1, :].min()],  # common LR_xy
                                ]
            common_tgt_extent = corner_coords_lonlat_to_extent(corner_coords_ll, tgt_epsg)
        else:
            # get Lon/Lat corner coordinates of geolayers
            UL_UR_LL_LR_ll = [(self.lons[y, x], self.lats[y, x]) for y, x in [(0, 0), (0, -1), (-1, 0), (-1, -1)]]

            # transform them to target projection
            UL_UR_LL_LR_prj = [transform_any_prj(4326, tgt_epsg, x, y) for x, y in UL_UR_LL_LR_ll]

            # separate X and Y
            X_prj, Y_prj = zip(*UL_UR_LL_LR_prj)

            # 3D geolayers, i.e., the corner coordinates have multiple values for multiple bands
            # -> use the outermost coordinates to be sure all data is included
            X_prj = (X_prj[0].min(), X_prj[1].max(), X_prj[2].min(), X_prj[3].max())
            Y_prj = (Y_prj[0].max(), Y_prj[1].max(), Y_prj[2].min(), Y_prj[3].min())

            # get the extent
            common_tgt_extent = (min(X_prj), min(Y_prj), max(X_prj), max(Y_prj))

        if tgt_coordgrid:
            common_tgt_extent = move_extent_to_coordgrid(common_tgt_extent, *tgt_coordgrid)

        return common_tgt_extent

    def _get_common_area_definition(self,
                                    data: np.ndarray,
                                    tgt_prj: Union[str, int],
                                    tgt_extent: Tuple[float, float, float, float] = None,
                                    tgt_res: Tuple = None,
                                    tgt_coordgrid: Tuple[Tuple, Tuple] = None
                                    ) -> AreaDefinition:
        # get common target extent
        tgt_epsg = CRS(tgt_prj).to_epsg()
        tgt_extent = tgt_extent or self._get_common_target_extent(tgt_epsg, tgt_coordgrid=tgt_coordgrid)

        common_area_definition = \
            PyresampleTransformer2D(
                lons=self.lons[:, :, 0],  # does NOT affect the computed area definition
                lats=self.lats[:, :, 0],  # -> only needed for __init__
                resamp_alg=self.resamp_alg,
                **self.opts
            ).compute_areadefinition_sensor2map(
                tgt_prj=tgt_prj,
                tgt_extent=tgt_extent,
                tgt_res=tgt_res,
                tgt_coordgrid=tgt_coordgrid
            )

        return common_area_definition

    def to_map_geometry(self,
                        data: np.ndarray,
                        tgt_prj: Union[str, int],
                        tgt_extent: Tuple[float, float, float, float] = None,
                        tgt_res: Tuple[float, float] = None,
                        tgt_coordgrid: Tuple[Tuple, Tuple] = None,
                        area_definition: AreaDefinition = None,
                        src_nodata: int = None,
                        tgt_nodata: int = None
                        ) -> Tuple[np.ndarray, Tuple[float, float, float, float, float, float], str]:
        """Transform the input sensor geometry array into map geometry.

        :param data:            3D numpy array (representing sensor geometry) to be warped to map geometry
        :param tgt_prj:         target projection (WKT or 'epsg:1234' or <EPSG_int>)
        :param tgt_extent:      extent coordinates of output map geometry array (LL_x, LL_y, UR_x, UR_y) in the tgt_prj
        :param tgt_res:         target X/Y resolution (e.g., (30, 30))
        :param tgt_coordgrid:   target coordinate grid ((x, x), (y, y)):
                                if given, the output extent is moved to this coordinate grid
        :param area_definition: an instance of pyresample.geometry.AreaDefinition;
                                OVERRIDES tgt_prj, tgt_extent, tgt_res and tgt_coordgrid; saves computation time
        :param src_nodata:      no-data value of the input array to be ignored in resampling
        :param tgt_nodata:      value for undetermined pixels in the output
        """
        if data.ndim != 3:
            raise ValueError(data.ndim, "'data' must have 3 dimensions.")

        if data.shape != self.lons.shape:
            raise ValueError(data.shape, 'Expected a sensor geometry data array with %d rows, %d columns, and %d bands.'
                             % self.lons.shape)

        if not tgt_prj and not area_definition:
            raise ValueError(tgt_prj, 'Target projection must be given if area_definition is not given.')

        if tgt_coordgrid:
            tgt_res = get_validated_tgt_res(tgt_coordgrid, tgt_res)

        # get common area_definition
        if not area_definition:
            area_definition = self._get_common_area_definition(data, tgt_prj, tgt_extent, tgt_res, tgt_coordgrid)

        def _to_map_geometry_2d(bidx: int):
            band_mapgeo, band_gt, band_prj = (
                PyresampleTransformer2D(
                    lons=self.lons[:, :, bidx],
                    lats=self.lats[:, :, bidx],
                    resamp_alg=self.resamp_alg,
                    nprocs=self._nprocs_2d,
                    **self.opts,
                ).to_map_geometry(
                    data=data[:, :, bidx],
                    area_definition=area_definition,
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
        with parallel_config(backend='threading', prefer='threads', n_jobs=self._nprocs_3d, require='sharedmem'):
            bandlist_mapgeo = list(
                Parallel(return_as='generator')(
                    delayed(_to_map_geometry_2d)(i) for i in range(data.shape[2])))

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
                           src_prj: Union[str, int],
                           src_gt: Tuple[float, float, float, float, float, float] = None,
                           src_extent: Tuple[float, float, float, float] = None,
                           src_nodata: int = None,
                           tgt_nodata: int = None
                           ) -> np.ndarray:
        """Transform the input map geometry array into sensor geometry.

        :param data:        3D numpy array (representing map geometry) to be warped to sensor geometry
        :param src_gt:      GDAL GeoTransform tuple of the input map geometry array
        :param src_prj:     projection of the input map geometry array (WKT or 'epsg:1234' or <EPSG_int>)
        :param src_extent:  extent coordinates of input map geometry array (LL_x, LL_y, UR_x, UR_y) in the src_prj
        :param src_nodata:  no-data value of the input array to be ignored in resampling
        :param tgt_nodata:  value for undetermined pixels in the output
        """
        # reject bilinear resampling due to an issue in pyresample (see
        # https://git.gfz-potsdam.de/EnMAP/sensormapgeo/-/issues/7 and https://github.com/pytroll/pyresample/issues/325)
        if self.resamp_alg == 'bilinear':
            warn(f"Bilinear resampling is not available in sensormapgeo {_libver} when transforming map geometry to "
                 f"sensor geometry due to changes in upstream packages. Using 'gauss' instead. "
                 "Note that bilinear resampling works in sensormapgeo<=0.5.0.", RuntimeWarning)

        if data.ndim != 3:
            raise ValueError(data.ndim, "'data' must have 3 dimensions.")

        if data.shape[2] != self.lons.shape[2]:
            raise ValueError(data.shape[2], f'Expected a map geometry data array with {self.lons.shape[2]} bands.')

        # TODO: remove src_extent and use src_gt as second mandatory parameter.
        if not src_gt:
            if src_extent:
                warn("Using 'src_extent' is deprecated and will soon be removed, use 'src_gt' instead.",
                     DeprecationWarning)
                xmin, ymin, xmax, ymax = src_extent
                rows, cols = data.shape[:2]
                src_gt = (xmin, (xmax - xmin) / cols, 0, ymax, 0, -abs((ymax - ymin) / rows))
            else:
                raise ValueError("'src_gt' should be provided.")

        def _to_sensor_geometry_2d(bidx: int) -> str:
            band_sensorgeo = \
                PyresampleTransformer2D(
                    lons=self.lons[:, :, bidx],
                    lats=self.lats[:, :, bidx],
                    resamp_alg=self.resamp_alg if self.resamp_alg != 'bilinear' else 'gauss',
                    nprocs=self._nprocs_2d,
                    **self.opts
                ).to_sensor_geometry(
                    data=data[:, :, bidx],
                    src_gt=src_gt,
                    src_prj=src_prj,
                    src_nodata=src_nodata,
                    tgt_nodata=tgt_nodata
                )

            drv = gdal.GetDriverByName('GTiff')
            rows_out, cols_out = band_sensorgeo.shape
            gdal_dtype = dTypeDic_NumPy2GDAL[str(np.dtype(band_sensorgeo.dtype))]
            p_out = f'/vsimem/band_{bidx}.tif'

            with drv.Create(p_out, cols_out, rows_out, 1, gdal_dtype) as ds:
                ds.GetRasterBand(1).WriteArray(band_sensorgeo)

            gc.collect()  # free up memory (unclear if this has an effect)

            return p_out

        with parallel_config(backend='threading', prefer='threads', n_jobs=self._nprocs_3d, require='sharedmem'):
            bandlist_sensorgeo = list(
                Parallel(return_as='generator')(
                    delayed(_to_sensor_geometry_2d)(i) for i in range(data.shape[2])))

        # create a VRT from all surface reflectance bands
        # vrt_options = gdal.BuildVRTOptions(srcNodata=0)
        with gdal.BuildVRT('/vsimem/data_sensorgeo.tif', bandlist_sensorgeo, separate=True) as ds_sensorgeo:
            ds_sensorgeo: gdal.Dataset
            data_sensorgeo = ds_sensorgeo.ReadAsArray().transpose(1, 2, 0).astype(data.dtype)

        return data_sensorgeo


class SensorMapGeometryTransformer3D(PyresampleTransformer3D):
    def __init__(self, *args, **kwargs):
        warn("Using 'SensorMapGeometryTransformer3D' is deprecated. "
             "Use sensormapgeo.Transformer(backend='pyresample') instead "
             "or switch to the new (and much faster) 'gdal' backend.", DeprecationWarning)
        super().__init__(*args, **kwargs)
