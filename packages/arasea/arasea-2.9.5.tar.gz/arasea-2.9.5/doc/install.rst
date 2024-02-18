.. _install:

Installing Arasea
=================

In order to guarantee a complete installation including the necessary libraries, it is recommended to install Arasea via conda-forge into a clean environment. This can be done using either `Mamba`_ or `Conda`_:

.. tab-set::

    .. tab-item:: Mamba

        .. code:: bash

            mamba create --name=arasea-env --channel=conda-forge arasea
            conda activate arasea-env


    .. tab-item:: Conda

        .. code:: bash

            conda create --name=arasea-env --channel=conda-forge arasea
            conda activate arasea-env


Alternatively, Arasea can be installed directly from PyPI using `pip`:

.. code-block:: bash

    pip install arasea


The current development branch of Arasea can be installed from PyPI or GitHub using `pip`:


.. tab-set::

    .. tab-item:: PyPI

        .. code:: bash

            pip install arasea-nightly

    .. tab-item:: GitHub

        .. code:: bash

            pip install git+https://github.com/arasea-devs/arasea


.. attention::

    To use the Numba or JAX backend you will need to install the corresponding library in addition to Arasea. Please refer to `Numba's installation instructions <https://numba.readthedocs.io/en/stable/user/installing.html>`__ and `JAX's installation instructions  <https://github.com/google/jax#installation>`__ respectively.


.. _Mamba: https://mamba.readthedocs.io/en/latest/installation.html
.. _Conda: https://docs.conda.io/projects/conda/en/latest/user-guide/install/index.html
