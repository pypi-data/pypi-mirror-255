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

"""Top-level package for sensormapgeo."""

import os as __os
from osgeo import gdal as _gdal  # noqa

from .transformer import Transformer
from .gdal_backend import GDALTransformer2D, GDALTransformer3D
from .pyresample_backend import PyresampleTransformer2D, PyresampleTransformer3D
from .pyresample_backend.transformer_2d import SensorMapGeometryTransformer  # deprecated in v1.0; TODO: remove
from .pyresample_backend.transformer_3d import SensorMapGeometryTransformer3D  # deprecated v1.0; TODO: remove
from .version import __version__, __versionalias__   # noqa (E402 + F401)

__all__ = [
    'Transformer',
    'GDALTransformer2D',
    'GDALTransformer3D',
    'PyresampleTransformer2D',
    'PyresampleTransformer3D',
    'SensorMapGeometryTransformer',
    'SensorMapGeometryTransformer3D'
]
__author__ = """Daniel Scheffler"""
__email__ = 'daniel.scheffler@gfz-potsdam.de'

# enable GDAL exceptions in the entire project
_gdal.UseExceptions()


# $PROJ_LIB was renamed to $PROJ_DATA in proj=9.1.1, which leads to issues with fiona>=1.8.20,<1.9
# https://github.com/conda-forge/pyproj-feedstock/issues/130
# -> fix it by setting PROJ_DATA
if 'GDAL_DATA' in __os.environ and 'PROJ_DATA' not in __os.environ and 'PROJ_LIB' not in __os.environ:
    __os.environ['PROJ_DATA'] = __os.path.join(__os.path.dirname(__os.environ['GDAL_DATA']), 'proj')  # pragma: no cover
