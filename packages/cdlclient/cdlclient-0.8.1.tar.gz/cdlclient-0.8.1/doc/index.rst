DataLab Simple Client User Guide
================================

DataLab is an **open-source platform for scientific and technical data processing
and visualization** with unique features designed to meet industrial requirements.
It is based on Python scientific libraries (such as NumPy, SciPy or scikit-image)
and Qt graphical user interfaces (thanks to `PlotPyStack`_).

.. seealso::

    For more details, see DataLab `Website`_.

DataLab Simple Client (``cdlclient`` package) is a Python library providing a
remote proxy to a DataLab application (server). It allows to use DataLab
features from a remote computer, and/or from a third-party application.

It also provides widgets to embed DataLab features in a Qt application
(connection dialog, etc.). For this particular use case, the library relies
on `QtPy`_.

.. figure:: _static/plotpy-stack-powered.png
    :align: center
    :width: 300 px

    DataLab is powered by `PlotPyStack <https://github.com/PlotPyStack>`_,
    the scientific Python-Qt visualization and graphical user interface stack.

.. note:: DataLab was created by `Codra`_/`Pierre Raybaut`_ in 2023. It is
          developed and maintained by DataLab open-source project.

External resources:
    .. list-table::
        :widths: 20, 80

        * - `Home`_
          - Project home page
        * - `PyPI`_
          - Python Package Index

.. toctree::
   :maxdepth: 2
   :caption: Contents:

   installation
   overview
   api

.. _PlotPyStack: https://github.com/PlotPyStack
.. _guidata: https://pypi.python.org/pypi/guidata
.. _PlotPy: https://pypi.python.org/pypi/PlotPy
.. _QtPy: https://pypi.python.org/pypi/QtPy
.. _PyPI: https://pypi.python.org/pypi/cdlclient
.. _Home: https://github.com/Codra-Ingenierie-Informatique/DataLabSimpleClient/
.. _Website: https://codra-ingenierie-informatique.github.io/DataLab/
.. _Codra: https://codra.net/
.. _BSD 3-Clause: https://github.com/Codra-Ingenierie-Informatique/DataLabSimpleClient/blob/master/LICENSE
.. _Pierre Raybaut: https://github.com/PierreRaybaut/
