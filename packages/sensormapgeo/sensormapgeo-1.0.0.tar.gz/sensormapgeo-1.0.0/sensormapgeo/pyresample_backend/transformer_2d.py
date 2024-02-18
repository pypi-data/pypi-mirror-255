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

"""Module to transform 2D arrays between sensor and map geometry."""

from typing import Union, Tuple, Optional
import os
from warnings import warn, catch_warnings, filterwarnings
from multiprocessing import cpu_count

import numpy as np
from osgeo import gdal  # noqa
from pyproj import CRS, Geod
from pyresample.geometry import AreaDefinition, SwathDefinition
from pyresample.kd_tree import resample_nearest, resample_gauss, resample_custom
with catch_warnings():
    filterwarnings('ignore', category=UserWarning,
                   message=".*XArray, dask, and/or zarr not found, XArrayBilinearResampler won't be available.")
    from pyresample.bilinear import NumpyBilinearResampler
from py_tools_ds.geo.coord_calc import corner_coord_to_minmax, get_corner_coordinates

from ..utils import move_extent_to_coordgrid, corner_coords_lonlat_to_extent, get_validated_tgt_res
from ..version import __version__ as _libver


class PyresampleTransformer2D(object):
    def __init__(self,
                 lons: np.ndarray,
                 lats: np.ndarray,
                 resamp_alg: str = 'nearest',
                 nprocs: int = cpu_count(),
                 **opts) -> None:
        """Get an instance of PyresampleTransformer2D.

        :param lons:
            2D longitude array corresponding to the 2D sensor geometry array

        :param lats:
            2D latitude array corresponding to the 2D sensor geometry array

        :param resamp_alg:
            resampling algorithm ('nearest', 'bilinear', 'gauss', 'custom')

        :param nprocs:
            <int>, Number of processor cores to be used (default: all cores available)

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
            <bool> Perform initial coarse reduction of source dataset in order to reduce execution time

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
        if lons.ndim != 2:
            raise ValueError('Expected a 2D longitude array. Received a %dD array.' % lons.ndim)
        if lats.ndim != 2:
            raise ValueError('Expected a 2D latitude array. Received a %dD array.' % lats.ndim)
        if lons.shape != lats.shape:
            raise ValueError((lons.shape, lats.shape), "'lons' and 'lats' are expected to have the same shape.")

        self.lats = lats
        self.lons = lons
        self.resamp_alg = resamp_alg
        self.swath_definition = SwathDefinition(lons=lons, lats=lats)
        self.area_definition: Optional[AreaDefinition] = None
        self.area_extent_ll = [np.min(lons), np.min(lats), np.max(lons), np.max(lats)]
        self.nprocs = nprocs
        self.opts_user = opts

        if 'fill_value' in self.opts_user:
            warn("In sensormapgeo 1.0.0, the 'fill_value' parameter was removed when initializing the transformer "
                 "class. Use 'src_nodata' and 'tgt_nodata' in the methods 'to_map_geometry' and 'to_sensor_geometry.",
                 DeprecationWarning)
            del self.opts_user['fill_value']

    def _get_target_extent(self, tgt_epsg: int):
        if tgt_epsg == 4326:
            tgt_extent = self.area_extent_ll
        else:
            corner_coords_ll = [[self.lons[0, 0], self.lats[0, 0]],  # UL_xy
                                [self.lons[0, -1], self.lats[0, -1]],  # UR_xy
                                [self.lons[-1, 0], self.lats[-1, 0]],  # LL_xy
                                [self.lons[-1, -1], self.lats[-1, -1]],  # LR_xy
                                ]
            tgt_extent = corner_coords_lonlat_to_extent(corner_coords_ll, tgt_epsg)

        return tgt_extent

    def compute_areadefinition_sensor2map(self,
                                          tgt_prj: Union[int, str],
                                          tgt_extent: Tuple[float, float, float, float] = None,
                                          tgt_res: Tuple[float, float] = None,
                                          tgt_coordgrid: Tuple[Tuple, Tuple] = None
                                          ) -> AreaDefinition:
        """Compute the area_definition to resample a sensor geometry array to map geometry.

        :param tgt_prj:         target projection (WKT or 'epsg:1234' or <EPSG_int>)
        :param tgt_extent:      extent coordinates of output map geometry array (LL_x, LL_y, UR_x, UR_y) in the tgt_prj
                                (automatically computed from the corner positions of the coordinate arrays)
        :param tgt_res:         target X/Y resolution (e.g., (30, 30))
        :param tgt_coordgrid:   target coordinate grid ((x, x), (y, y)):
                                if given, the output extent is moved to this coordinate grid
        :return:
        """
        from .. import GDALTransformer2D
        mask_mapgeo, out_gt, out_prj = (
            GDALTransformer2D(
                lons=self.lons,
                lats=self.lats
            ).to_map_geometry(
                np.ones((self.lons.shape[:2]), np.int8),
                tgt_prj=tgt_prj,
                tgt_extent=tgt_extent or self._get_target_extent(CRS(tgt_prj).to_epsg()),
                tgt_res=tgt_res,
                tgt_coordgrid=tgt_coordgrid
            )
        )
        y_size, x_size = mask_mapgeo.shape

        # get area_definition
        xmin, xmax, ymin, ymax = corner_coord_to_minmax(get_corner_coordinates(gt=out_gt, cols=x_size, rows=y_size))
        area_definition = (
            AreaDefinition(
                area_id='',
                description='',
                proj_id='',
                projection=CRS(tgt_prj),
                width=x_size,
                height=y_size,
                area_extent=[xmin, ymin, xmax, ymax],
                )
        )

        return area_definition

    def _estimate_radius_of_influence(self) -> float:
        """Estimate meaningful radius_of_influence as 1.5 * pixel size in meters."""
        # get X/Y pixel size in meters from lon/lat arrays
        (lon0, lon1), (lat0, lat1), lon2, lat2 = self.lons[0, :2], self.lats[0, :2], self.lons[1, 0], self.lats[1, 0]
        geod = Geod(ellps="WGS84")
        pixsize_mt_x = geod.inv(lon0, lat0, lon1, lat1)[2]
        pixsize_mt_y = geod.inv(lon0, lat0, lon2, lat2)[2]

        factor = 1.5 if self.resamp_alg == 'bilinear' else 1
        radius_est = factor * max([pixsize_mt_x, pixsize_mt_y])

        return radius_est

    def _get_options(self, data_nbands: int, tgt_nodata=None) -> (dict, dict):
        # NOTE: If pykdtree is built with OpenMP support (default) the number of threads is controlled with the
        #       standard OpenMP environment variable OMP_NUM_THREADS. The nprocs argument has no effect on pykdtree.
        os.environ['OMP_NUM_THREADS'] = f"{self.nprocs}"

        radius_est = self._estimate_radius_of_influence()
        defaults = dict(  # defaults
            radius_of_influence=radius_est,
            neighbours=8 if self.resamp_alg == 'bilinear' else 32,  # using 32 neighbours fills up the memory
            sigmas=(radius_est / 2),
            fill_value=tgt_nodata if tgt_nodata is not None else 0,
            nprocs=1
        )
        kw_rsp = dict()
        opts = self.opts_user.copy()
        for k in defaults:
            if k not in opts:
                opts[k] = defaults[k]

        if 'radius_of_influence' in self.opts_user and 'sigmas' not in self.opts_user:
            opts['sigmas'] = opts['radius_of_influence'] / 2

        if self.resamp_alg != 'gauss' and 'sigmas' in opts:
            del opts['sigmas'], opts['nprocs']

        if self.resamp_alg == 'nearest':
            if 'neighbours' in opts:
                del opts['neighbours']

        if self.resamp_alg == 'bilinear':
            kw_rsp = dict(fill_value=opts['fill_value'], nprocs=1)
            del opts['fill_value']

        if self.resamp_alg == 'gauss':
            # ensure that sigmas are provided as list if data is 3-dimensional
            if data_nbands > 1:
                if not isinstance(opts['sigmas'], list):
                    opts['sigmas'] = [opts['sigmas']] * data_nbands

                n_sigmas = len(opts['sigmas'])  # noqa
                if not n_sigmas == data_nbands:
                    raise ValueError(f"The 'sigmas' parameter must have the same number of values like the number of "
                                     f"bands. number of sigmas: {n_sigmas}; number of bands: {data_nbands}")

        if self.resamp_alg == 'custom':
            if 'weight_funcs' not in opts:
                raise ValueError(opts, "Options must contain a 'weight_funcs' item.")

        return opts, kw_rsp

    def _resample(self,
                  data: np.ndarray,
                  source_geo_def: Union[AreaDefinition, SwathDefinition],
                  target_geo_def: Union[AreaDefinition, SwathDefinition],
                  src_nodata: int = None,
                  tgt_nodata: int = None
                  ) -> np.ndarray:
        """Run the resampling algorithm.

        :param data:            numpy array to be warped to sensor or map geometry
        :param source_geo_def:  source geo definition
        :param target_geo_def:  target geo definition
        :param src_nodata:      no-data value of the input array to be ignored in resampling
        :param tgt_nodata:      value for undetermined pixels in the output
        :return:
        """
        nbands = data.shape[2] if data.ndim > 2 else 1
        opts, kw_rsp = self._get_options(nbands, tgt_nodata=tgt_nodata)

        # handle src_nodata
        if src_nodata is not None and src_nodata in data:
            data = np.ma.masked_array(data, mask=data == src_nodata)

        if self.resamp_alg == 'nearest':
            result = resample_nearest(source_geo_def, data, target_geo_def, **opts)

        elif self.resamp_alg == 'bilinear':
            with catch_warnings():
                # suppress a UserWarning coming from pyresample v0.15.0
                filterwarnings('ignore', category=UserWarning,
                               message='You will likely lose important projection information when converting '
                                       'to a PROJ string from another format.')
                with np.errstate(divide='ignore', invalid='ignore'):
                    # NOTE: Using pyresample.bilinear.XArrayBilinearResampler here is much slower (takes twice the time)
                    result = NumpyBilinearResampler(source_geo_def, target_geo_def, **opts).resample(data, **kw_rsp)

        elif self.resamp_alg == 'gauss':
            result = resample_gauss(source_geo_def, data, target_geo_def, **opts)

        elif self.resamp_alg == 'custom':
            result = resample_custom(source_geo_def, data, target_geo_def, **opts)

        else:
            raise ValueError(self.resamp_alg)

        # fill tgt_nodata into masked pixels of the resampled data
        if isinstance(result, np.ma.masked_array):
            result = result.filled(tgt_nodata)

        return result.astype(data.dtype)

    @staticmethod
    def _get_gt_prj_from_areadefinition(area_definition: AreaDefinition) -> (Tuple[float, float, float,
                                                                                   float, float, float], str):
        gt = area_definition.area_extent[0], area_definition.pixel_size_x, 0, \
             area_definition.area_extent[3], 0, -area_definition.pixel_size_y
        prj = area_definition.crs.to_wkt()

        return gt, prj

    def to_map_geometry(self,
                        data: np.ndarray,
                        tgt_prj: Union[str, int] = None,
                        tgt_extent: Tuple[float, float, float, float] = None,
                        tgt_res: Tuple = None,
                        tgt_coordgrid: Tuple[Tuple, Tuple] = None,
                        area_definition: AreaDefinition = None,
                        src_nodata: int = None,
                        tgt_nodata: int = None
                        ) -> Tuple[np.ndarray, tuple, str]:
        """Transform the input sensor geometry array into map geometry.

        :param data:            2D or 3D numpy array (representing sensor geometry) to be warped to map geometry
        :param tgt_prj:         target projection (WKT or 'epsg:1234' or <EPSG_int>)
        :param tgt_extent:      extent coordinates of output map geometry array (LL_x, LL_y, UR_x, UR_y) in the tgt_prj
        :param tgt_res:         target X/Y resolution (e.g., (30, 30))
        :param tgt_coordgrid:   target coordinate grid ((x, x), (y, y)):
                                if given, the output extent is moved to this coordinate grid
        :param area_definition: an instance of pyresample.geometry.AreaDefinition;
                                OVERRIDES tgt_prj, tgt_extent and tgt_res; saves computation time
        :param src_nodata:      no-data value of the input array to be ignored in resampling
        :param tgt_nodata:      value for undetermined pixels in the output
        """
        if data.ndim not in [2, 3]:
            raise ValueError(data.ndim, "'data' must have 2 or 3 dimensions.")

        if data.shape[:2] != self.lons.shape[:2]:
            raise ValueError(data.shape, 'Expected a sensor geometry data array with %d rows and %d columns.'
                             % self.lons.shape[:2])

        if tgt_coordgrid:
            tgt_res = get_validated_tgt_res(tgt_coordgrid, tgt_res)

        # get area_definition
        if area_definition:
            self.area_definition = area_definition
        else:
            if not tgt_prj:
                raise ValueError(tgt_prj, 'Target projection must be given if area_definition is not given.')

            tgt_epsg = CRS(tgt_prj).to_epsg()
            tgt_extent = tgt_extent or self._get_target_extent(tgt_epsg)

            if tgt_coordgrid:
                tgt_extent = move_extent_to_coordgrid(tgt_extent, *tgt_coordgrid)

            self.area_definition = self.compute_areadefinition_sensor2map(
                tgt_prj=tgt_prj, tgt_extent=tgt_extent, tgt_res=tgt_res)

        # resample
        data_mapgeo = self._resample(data, self.swath_definition, self.area_definition, src_nodata, tgt_nodata)
        out_gt, out_prj = self._get_gt_prj_from_areadefinition(self.area_definition)

        # output validation
        if not data_mapgeo.shape[:2] == (self.area_definition.height, self.area_definition.width):
            raise RuntimeError(f'The computed map geometry output does not have the expected number of rows/columns. '
                               f'Expected: {str((self.area_definition.height, self.area_definition.width))}; '
                               f'output: {str(data_mapgeo.shape[:2])}.')
        if data.ndim > 2 and data_mapgeo.ndim == 2:
            raise RuntimeError(f'The computed map geometry output has only one band '
                               f'instead of the expected {data.shape[2]} bands.')

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

        :param data:        2D or 3D numpy array (representing map geometry) to be warped to sensor geometry
        :param src_gt:      GDAL GeoTransform tuple of the input map geometry array
        :param src_prj:     projection of the input map geometry array (WKT or 'epsg:1234' or <EPSG_int>)
        :param src_extent:  extent coordinates of input map geometry array (LL_x, LL_y, UR_x, UR_y) in the src_prj
        :param src_nodata:  no-data value of the input array to be ignored in resampling
        :param tgt_nodata:  value for undetermined pixels in the output
        """
        if data.ndim not in [2, 3]:
            raise ValueError(data.ndim, "'data' must have 2 or 3 dimensions.")

        # get area_definition
        # TODO: remove src_extent and use src_gt as second mandatory parameter.
        if not src_gt:
            if src_extent:
                warn("Using 'src_extent' is deprecated and will soon be removed, use 'src_gt' instead.",
                     DeprecationWarning)
            else:
                raise ValueError("'src_gt' should be provided.")
        else:
            rows, cols = data.shape[:2]
            xmin, xmax, ymin, ymax = corner_coord_to_minmax(get_corner_coordinates(src_gt, cols, rows))
            src_extent = (xmin, ymin, xmax, ymax)
        self.area_definition = AreaDefinition('', '', '',  CRS(src_prj), data.shape[1], data.shape[0],
                                              list(src_extent))

        # resample
        if self.resamp_alg == 'bilinear':
            # reject bilinear resampling due to https://git.gfz-potsdam.de/EnMAP/sensormapgeo/-/issues/7
            warn(f"Bilinear resampling is not available in sensormapgeo {_libver} when transforming map "
                 f"geometry to sensor geometry due to changes in upstream packages. Using 'gauss' instead. "
                 f"Note that bilinear resampling works in sensormapgeo<=0.5.0.", RuntimeWarning)
            resamp_alg = self.resamp_alg
            try:
                # use gauss instead of bilinear as fallback and change the instance attribute back afterward
                self.resamp_alg = 'gauss'
                data_sensorgeo = (
                    self._resample(data, self.area_definition, self.swath_definition, src_nodata, tgt_nodata))
            finally:
                self.resamp_alg = resamp_alg
        else:
            data_sensorgeo = self._resample(data, self.area_definition, self.swath_definition, src_nodata, tgt_nodata)

        # output validation
        if not data_sensorgeo.shape[:2] == self.lats.shape[:2]:
            raise RuntimeError(f'The computed sensor geometry output does not have '
                               f'the same X/Y dimension like the coordinates array. '
                               f'Coordinates array: {self.lats.shape}; output array: {data_sensorgeo.shape}.')

        if data.ndim > 2 and data_sensorgeo.ndim == 2:
            raise RuntimeError(f'The computed sensor geometry output has only one band '
                               f'instead of the expected {data.shape[2]} bands.')

        return data_sensorgeo


class SensorMapGeometryTransformer(PyresampleTransformer2D):
    def __init__(self, *args, **kwargs):
        warn("Using 'SensorMapGeometryTransformer' is deprecated. "
             "Use sensormapgeo.Transformer(backend='pyresample') instead "
             "or switch to the new (and much faster) 'gdal' backend.", DeprecationWarning)
        super().__init__(*args, **kwargs)
