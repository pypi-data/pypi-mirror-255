.. _installation:

Installation
============


Using Mambaforge (recommended)
------------------------------

This is the preferred way to install sensormapgeo. It is the fastest one and it always installs the most
recent stable release and automatically resolves all the dependencies.

1. Install Mambaforge_.
2. Open a Mambaforge command line prompt and proceed there (e.g., on Windows you can find it in the start menu).
3. Install sensormapgeo into a separate environment (recommended) and activate it:

   .. code-block:: bash

    $ mamba create --name sensormapgeo sensormapgeo
    $ mamba activate sensormapgeo


Using Anaconda or Miniconda (slower)
------------------------------------

Using conda_ (latest version recommended), sensormapgeo is installed as follows:

   .. code-block:: bash

    $ conda create --name sensormapgeo -c conda-forge sensormapgeo
    $ conda activate sensormapgeo


Using pip (not recommended)
---------------------------

There is also a `pip`_ installer for sensormapgeo. However, please note that sensormapgeo depends on some
open source packages that may cause problems when installed with pip. Therefore, we strongly recommend
to resolve the following dependencies before the pip installer is run:

    * gdal>=3.8
    * joblib
    * numpy
    * py-tools-ds>=0.18.0
    * pyproj>2.2
    * pyresample>=1.17.0


Then, the pip installer can be run by:

   .. code-block:: bash

    $ pip install sensormapgeo

If you don't have `pip`_ installed, this `Python installation guide`_ can guide
you through the process.



.. note::

    sensormapgeo has been tested with Python 3.8+.,
    i.e., should be fully compatible to all Python versions from 3.8 onwards.


.. _Mambaforge: https://github.com/conda-forge/miniforge#mambaforge
.. _pip: https://pip.pypa.io
.. _Python installation guide: http://docs.python-guide.org/en/latest/starting/installation/
.. _conda: https://docs.conda.io
