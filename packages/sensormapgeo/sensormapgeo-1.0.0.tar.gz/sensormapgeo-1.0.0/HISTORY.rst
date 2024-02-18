=======
History
=======

1.0.0 (2024-12-08)
------------------

In version 1.0.0, sensormapgeo was completely re-implemented and optimized for speed. In addition to the 'pyresample'
backend, a second backend built on top of GDAL was added. The GDAL backend is now the default and provides many
different resampling techniques at a high execution speed. The 'pyresample' backend features gauss resampling
and allows to run a custom/user-specified resampling.

* `!12`_: Replaced direct calls of setup.py.
* `!13`_: Replaced deprecated HTTP URL.
* `!14`_: Added workaround for missing PROJ_DATA environment variable.
* `!15`_: Updated copyright.
* `!16`_: Updated environment files and switched to latest Ubuntu CI base image.
* `!17`_: Dropped Python 3.7 support due to end-of-life status and added 3.11/3.12 compatibility.
* `!10`_: Added a second GDAL-based backend to transform between sensor and map geometry which is much faster and offers
  all GDAL-supported resampling techniques.
* `!18`_: Added a common frontend that allows to run the transformation between sensor and map geometry in a simple API
  that supports the GDAL and the pyresample backend and allows to pass 2D and 3D geolayers.
* Cleaned up repository.
* `!21`_: Revised multiprocessing to use joblib + shared memory instead pebble for pyresample 3D transformer.
* `!22`_: Revised approach to compute area_definition in 'pyresample' backend mode.
* `!20`_: Completely revised tests and unified 'gdal' and 'pyresample' APIs to have a common and simple frontend.
  Simplified package requirements (dropped pebble and _openmp_mutex due to updated parallelization via joblib).
* `!24`_: Fixed a couple of warnings.
* `!19`_: Revised documentation and added overview scheme to README.

.. _!10: https://git.gfz-potsdam.de/EnMAP/sensormapgeo/-/merge_requests/10
.. _!12: https://git.gfz-potsdam.de/EnMAP/sensormapgeo/-/merge_requests/12
.. _!13: https://git.gfz-potsdam.de/EnMAP/sensormapgeo/-/merge_requests/13
.. _!14: https://git.gfz-potsdam.de/EnMAP/sensormapgeo/-/merge_requests/14
.. _!15: https://git.gfz-potsdam.de/EnMAP/sensormapgeo/-/merge_requests/15
.. _!16: https://git.gfz-potsdam.de/EnMAP/sensormapgeo/-/merge_requests/16
.. _!17: https://git.gfz-potsdam.de/EnMAP/sensormapgeo/-/merge_requests/17
.. _!18: https://git.gfz-potsdam.de/EnMAP/sensormapgeo/-/merge_requests/18
.. _!19: https://git.gfz-potsdam.de/EnMAP/sensormapgeo/-/merge_requests/19
.. _!20: https://git.gfz-potsdam.de/EnMAP/sensormapgeo/-/merge_requests/20
.. _!21: https://git.gfz-potsdam.de/EnMAP/sensormapgeo/-/merge_requests/21
.. _!22: https://git.gfz-potsdam.de/EnMAP/sensormapgeo/-/merge_requests/22
.. _!24: https://git.gfz-potsdam.de/EnMAP/sensormapgeo/-/merge_requests/23


0.7.0 (2022-11-15)
------------------

* Renamed master branch to main.
* `!11`_: Dropped Python 3.6 support due to EOL status.

.. _!11: https://git.gfz-potsdam.de/EnMAP/sensormapgeo/-/merge_requests/11


0.6.2 (2022-03-10)
------------------

* Enabled GDAL exceptions in the entire project.


0.6.1 (2021-11-26)
------------------

* Increased minimal version of pyresample to avoid ImportError.
* Refactored unittests to pytest (new structure, raw assertions, ...).
* Added subtests bases on pytest-subtests.


0.6.0 (2021-11-26)
------------------

* Replaced deprecated gdalnumeric import.
* `!7`_: Disabled bilinear resampling for map to sensor geometry transformation due to upstream incompatibility
  (closes `#7`_).
* Removed pyresample version pinning which fixes multiple DeprecationWarnings.
* `!8`_: Tests are now called via pytest instead of nosetest. This improves stability and test output and adds nice
  reports. Coverage now works in multiprocessing after properly closing and joining multiprocessing.Pool and adding
  .coveragerc.
* Fixed some warnings.

.. _#7: https://git.gfz-potsdam.de/EnMAP/sensormapgeo/-/issues/7
.. _!7: https://git.gfz-potsdam.de/EnMAP/sensormapgeo/-/merge_requests/7
.. _!8: https://git.gfz-potsdam.de/EnMAP/sensormapgeo/-/merge_requests/8

0.5.0 (2021-09-27)
------------------

* CI now uses Mambaforge. Revised test_sensormapgeo_install CI job.
* 'make lint' now also directly prints the logs.
* Fixed deprecated gdalnumeric import.
* Updated minimal version of py_tools_ds to 0.18.0.
* Switched to Apache 2.0 license.


0.4.8 (2020-02-08)
------------------

* Fixed wrong package name in environment_sensormapgeo.yml.
* Fixed remaining coverage artifacts after running 'make clean'.
* Fixed deprecated gdal import.
* Pinned pyresample to <1.17.0 due to https://github.com/pytroll/pyresample/issues/325.


0.4.7 (2020-12-10)
------------------

* Use 'conda activate' instead of deprecated 'source activate'.
* Added URL checker and corresponding CI job.
* Fixed dead links.
* Updated installation procedure documentation.


0.4.6 (2020-10-12)
------------------

* Use SPDX license identifier and set all files to GPL3+ to be consistent with license headers in the source files.
* Excluded tests from being installed via 'pip install'.
* Set development status to 'beta'.


0.4.5 (2020-09-15)
------------------

* Replaced deprecated HTTP links.


0.4.4 (2020-09-04)
------------------

* Fixed issue #6 (Deadlock within SensorMapGeometryTransformer3D when running in multiprocessing for resampling
  algorithms 'near' and 'gauss'.)
* Added pebble to pip requirements.


0.4.3 (2020-09-02)
------------------

* create_area_def() now gets an EPSG string from sensormapgeo instead of a PROJ4 dictionary to get rid of the
  deprecated PROJ4 format.


0.4.2 (2020-09-01)
------------------

* Some adjustments to recent changes in py_tools_ds and pyproj.
* Added pyproj as direct dependency to requirements.


0.4.1 (2020-08-17)
------------------

* Fixed wrong import statement.
* Fixed numpy deprecation warning.


0.4.0 (2020-08-07)
------------------

* Revised the way how multiprocessing is called in the 3D transformer (replaced with pool.imap_unordered without
  initializer). This is as fast as before but has a much smaller memory consumption enabling the algorithm to also run
  on smaller machines while still highly benefiting from more CPUs. Fixes issue #5.


0.3.5 (2020-08-07)
------------------

* Fixed VisibleDeprecationWarning.


0.3.4 (2020-08-07)
------------------

* Fixed a NotADirectoryError on Windows, possibly due to race conditions.


0.3.3 (2020-05-08)
------------------

* Replaced workaround for warning with warnings.catch_warning.


0.3.2 (2020-05-08)
------------------

* Suppressed another warning coming from pyresample.


0.3.1 (2020-05-08)
------------------

* Fixed a warning coming from pyresample.


0.3.0 (2020-05-08)
------------------

* Converted all type hints to Python 3.6 style. Dropped Python 3.5 support. Fixed code duplicate.
* Split sensormapgeo module into transformer_2d and transformer_3d.
* SensorMapGeometryTransformer.compute_areadefinition_sensor2map() now directly uses pyresample instead of GDAL if the
  target resolution is given.
* SensorMapGeometryTransformer3D.to_map_geometry() now computes a common area definition only ONCE which saves
  computation time and increases stability.
* The computation of the common extent in 3D geolayers now works properly if target projection is not set to LonLat.
* Added paramter tgt_coordgrid to to_map_geometry methods to automatically move the output extent to a given coordinate
  grid.
* compute_areadefinition_sensor2map() now also adds 1 pixel around the output extent in the pyresample version just
  like in the GDAL version.
* Added some input validation.


0.2.2 (2020-03-10)
------------------

* Fix for always returning 0.1.0 when calling sensormapgeo.__version__.


0.2.1 (2020-03-10)
------------------

* Fix for always returning returning float64 output data type in case of bilinear resampling.
* Added output data type verification to tests.
* Fix for an exception if the output of get_proj4info() contains trailing white spaces
  (fixed by an update of py_tools_ds).
* Improved tests.
* Set channel priority to strict.
* Force libgdal to be installed from conda-forge.
* Fixed broken documentation link


0.2.0 (2020-01-06)
------------------

* Added continous integration.
* Updated readme file.
* Added PyPI release.


0.1.0 (2020-01-06)
------------------

* First release on GitLab.
