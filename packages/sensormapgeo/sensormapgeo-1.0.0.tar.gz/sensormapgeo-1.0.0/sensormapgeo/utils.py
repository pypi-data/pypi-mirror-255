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

"""Commonly used utility functions and probably useful functions for the user."""
from typing import Tuple, Union, List

import numpy as np

from py_tools_ds.geo.coord_trafo import reproject_shapelyGeometry, transform_any_prj
from py_tools_ds.geo.vector.topology import Polygon
from py_tools_ds.numeric.vector import find_nearest


def clip_geolayer_by_extent(lons: np.ndarray,
                            lats: np.ndarray,
                            extent: Tuple[float, float, float, float],
                            extent_prj: Union[str, int]
                            ) -> Tuple[np.ndarray, np.ndarray]:
    # transform extent to lon/lat
    xmin, ymin, xmax, ymax = extent
    poly_ll = reproject_shapelyGeometry(
        Polygon(
            ((xmin, ymax),  # UL
             (xmax, ymax),  # UR
             (xmax, ymin),  # LR
             (xmin, ymin),  # LL
             (xmin, ymax))  # UL
        ),
        extent_prj, 4326
    )
    lon_min, lat_min, lon_max, lat_max = poly_ll.bounds

    # get subset of geolayer within lon/lat bounds
    lonlat_mask = (((lons >= lon_min) & (lons <= lon_max)) &
                   ((lats >= lat_min) & (lats <= lat_max)))

    if not np.count_nonzero(lonlat_mask):
        raise RuntimeError('The given extent has no spatial overlap with the lon/lat geolayer.')

    row_indices = np.any(lonlat_mask, axis=1)
    col_indices = np.any(lonlat_mask, axis=0)
    lons_sub = lons[row_indices, :][:, col_indices]
    lats_sub = lats[row_indices, :][:, col_indices]

    return lons_sub, lats_sub


def corner_coords_lonlat_to_extent(corner_coords_ll: List, tgt_epsg: int):
    corner_coords_tgt_prj = [transform_any_prj(4326, tgt_epsg, x, y)
                             for x, y in corner_coords_ll]
    corner_coords_tgt_prj_np = np.array(corner_coords_tgt_prj)
    x_coords = corner_coords_tgt_prj_np[:, 0]
    y_coords = corner_coords_tgt_prj_np[:, 1]
    tgt_extent = [np.min(x_coords), np.min(y_coords), np.max(x_coords), np.max(y_coords)]

    return tgt_extent


def move_extent_to_coordgrid(extent: Tuple[float, float, float, float],
                             tgt_xgrid: Tuple[float, float],
                             tgt_ygrid: Tuple[float, float]):
    tgt_xgrid, tgt_ygrid = np.array(tgt_xgrid), np.array(tgt_ygrid)
    xmin, ymin, xmax, ymax = extent
    tgt_xmin = find_nearest(tgt_xgrid, xmin, roundAlg='off', extrapolate=True)
    tgt_xmax = find_nearest(tgt_xgrid, xmax, roundAlg='on', extrapolate=True)
    tgt_ymin = find_nearest(tgt_ygrid, ymin, roundAlg='off', extrapolate=True)
    tgt_ymax = find_nearest(tgt_ygrid, ymax, roundAlg='on', extrapolate=True)

    return tgt_xmin, tgt_ymin, tgt_xmax, tgt_ymax


def get_validated_tgt_res(tgt_coordgrid, tgt_res):
    exp_tgt_res = np.ptp(tgt_coordgrid[0]), np.ptp(tgt_coordgrid[1])
    if tgt_res and exp_tgt_res != tgt_res:
        raise ValueError('The target resolution must be compliant to the target coordinate grid if given.')

    return exp_tgt_res
