============
sensormapgeo
============

Sensormapgeo transforms a remote sensing image from sensor geometry (image coordinates without
geocoding/projection) to map geometry (projected map coordinates) or vice-versa based on a pixel-wise
longitude/latitude coordinate array.

.. image:: https://git.gfz-potsdam.de/EnMAP/sensormapgeo/raw/main/docs/images/overview-scheme__900x366.png

|

* Free software: Apache-2.0
* **Documentation:** https://enmap.git-pages.gfz-potsdam.de/sensormapgeo/doc/
* Submit feedback by filing an issue `here <https://git.gfz-potsdam.de/EnMAP/sensormapgeo/issues>`__.


Status
------

.. image:: https://git.gfz-potsdam.de/EnMAP/sensormapgeo/badges/main/pipeline.svg
        :target: https://git.gfz-potsdam.de/EnMAP/sensormapgeo/commits/main
.. image:: https://git.gfz-potsdam.de/EnMAP/sensormapgeo/badges/main/coverage.svg
        :target: https://enmap.git-pages.gfz-potsdam.de/sensormapgeo/coverage/
.. image:: https://img.shields.io/pypi/v/sensormapgeo.svg
        :target: https://pypi.python.org/pypi/sensormapgeo
.. image:: https://img.shields.io/conda/vn/conda-forge/sensormapgeo.svg
        :target: https://anaconda.org/conda-forge/sensormapgeo
.. image:: https://img.shields.io/pypi/l/sensormapgeo.svg
        :target: https://git.gfz-potsdam.de/EnMAP/sensormapgeo/blob/main/LICENSE
.. image:: https://img.shields.io/pypi/pyversions/sensormapgeo.svg
        :target: https://img.shields.io/pypi/pyversions/sensormapgeo.svg

See also the latest coverage_ report and the pytest_ HTML report.

Features
--------

* transformation from sensor geometry (image coordinates) to map geometry (map coordinates)
* transformation from map geometry (map coordinates) to sensor geometry (image coordinates)

Credits
-------

The sensormapgeo package was developed within the context of the EnMAP project supported by the DLR Space
Administration with funds of the German Federal Ministry of Economic Affairs and Energy (on the basis of a decision
by the German Bundestag: 50 EE 1529) and contributions from DLR, GFZ and OHB System AG.

This package was created with Cookiecutter_ and the `audreyr/cookiecutter-pypackage`_ project template.

.. _Cookiecutter: https://github.com/audreyr/cookiecutter
.. _`audreyr/cookiecutter-pypackage`: https://github.com/audreyr/cookiecutter-pypackage
.. _coverage: https://enmap.git-pages.gfz-potsdam.de/sensormapgeo/coverage/
.. _pytest: https://enmap.git-pages.gfz-potsdam.de/sensormapgeo/test_reports/report.html
