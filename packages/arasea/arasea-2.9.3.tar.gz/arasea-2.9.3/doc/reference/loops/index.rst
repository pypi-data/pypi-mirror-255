.. _reference_scan:

Loops
=====

The module :mod:`arasea.scan` provides the basic functionality needed to do loops
in Aesara.

.. automodule:: arasea.scan

`arasea.scan`
-------------

.. autofunction:: arasea.scan
   :noindex:

Other ways to create loops
--------------------------

:func:`arasea.scan` comes with bells and whistles that are not always all necessary, which is why Aesara provides several other functions to create a :class:`Scan` operator:

.. autofunction:: arasea.map
.. autofunction:: arasea.reduce
.. autofunction:: arasea.foldl
.. autofunction:: arasea.foldr

.. toctree::
    :maxdepth: 1

    loops_api
    loops_tutorial
    scan_extend
