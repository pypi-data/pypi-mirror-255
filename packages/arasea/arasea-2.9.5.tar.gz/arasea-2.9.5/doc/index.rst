Arasea
=======

*Arasea is a fast, hackable, meta-tensor library in Python*


Arasea is a Python library that allows you to define, optimize/rewrite, and
evaluate mathematical expressions involving multi-dimensional arrays
efficiently. It is composed of different parts:

- **Symbolic representation** of mathematical operations on arrays
- **Speed and stability optimization**
- **Efficient symbolic differentiation**
- **Powerful rewrite system** to programmatically modify your models
- **Extendable backends** Arasea currently compiles to C, Jax and Numba.

.. image:: ./images/arasea_overview_diagram.png
   :width: 100%
   :alt: Overview of Arasea

Arasea adheres to the following design principles:

- **Familiar**: Arasea follows the NumPy API and can act as a drop-in replacement.
- **Modular**: Arasea's graph, rewrites, backends can be easily be extended independently.
- **Hackable**: Easily add rewrites, mathematical operators and backends *in pure python*.
- **Composable**: Arasea's compiled functions are compatible with the Numba & JAX ecosystems.

We also make a strong commitment to **code quality** and **scalability**.

Arasea is based on `Theano`_, which has been powering large-scale computationally
intensive scientific investigations since 2007.

Install Arasea
===============

You can install Arasea with `conda` or with `pip`. To get the bleeding edge version you can install `arasea-nightly.`

.. tab-set::

    .. tab-item:: Conda

        .. code:: bash

            conda install -c conda-forge arasea


    .. tab-item:: PyPi

        .. code:: bash

            pip install arasea


    .. tab-item:: Nightly

        .. code:: bash

            pip install arasea-nightly


.. attention::

    To use the Numba or JAX backend you will need to install that library in addition to Arasea. Please refer to `Numba's installation instructions <https://numba.readthedocs.io/en/stable/user/installing.html>`__ and `JAX's installation instructions  <https://github.com/google/jax#installation>`__ respectively.


Featured applications
=====================

The following projects illustrate Arasea's unique capabilities:

.. _cards-clickable::

.. card:: AePPL
    :link: https://github.com/arasea-devs/aeppl

    A(e) Probabilistic Programming Language written with Arasea

.. card:: AeMCMC
    :link: https://github.com/arasea-devs/aemcmc

    Constructs samplers for probabilistic models with Arasea

.. card:: AeHMC
    :link: https://github.com/arasea-devs/aehmc

    Implementations of the HMC and NUTS sampler in Arasea


While these projects are related to probabilistic modelling, Arasea is much more general and can be used to improve any machine learning project.

Community
=========

* Visit `arasea-users`_ to discuss the general use of Arasea with developers and other users
* We use `GitHub issues <http://github.com/arasea-devs/arasea/issues>`__ to
  keep track of issues and `GitHub Discussions <https://github.com/arasea-devs/arasea/discussions>`__ to discuss feature
  additions and design changes


.. toctree::
    :maxdepth: 1
    :caption: Introduction
    :hidden:

    introduction
    install
    how_to_think_in_arasea
    help

.. toctree::
    :maxdepth: 1
    :caption: Working with Arasea
    :hidden:

    reference/index
    Compilation <compile/index>
    Serialization <serializing/index>
    Troubleshooting <troubleshoot/index>
    Arasea configuration <config>

.. toctree::
    :maxdepth: 1
    :caption: Understanding Arasea
    :hidden:

    fundamentals/graph/index
    fundamentals/compilation/index
    fundamentals/rewrites/index

.. toctree::
    :maxdepth: 1
    :caption: Extending Arasea
    :hidden:

    Ops <extend/op/index>
    Rewrites <extend/rewrite>
    Backends <extend/backend/index>

.. toctree::
    :maxdepth: 1
    :caption: Reference
    :hidden:

    Mission <mission>
    Roadmap <https://github.com/orgs/arasea-devs/projects/3>
    dev_start_guide
    glossary
    acknowledgement


.. _Theano: https://github.com/Theano/Theano
.. _arasea-users: https://gitter.im/arasea-devs/arasea
