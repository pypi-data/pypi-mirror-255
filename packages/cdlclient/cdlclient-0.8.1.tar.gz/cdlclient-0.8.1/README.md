## DataLab Simple Client

![DataLab](https://raw.githubusercontent.com/Codra-Ingenierie-Informatique/DataLabSimpleClient/main/doc/images/DataLab-banner.png)

[![license](https://img.shields.io/pypi/l/cdlclient.svg)](./LICENSE)
[![pypi version](https://img.shields.io/pypi/v/cdlclient.svg)](https://pypi.org/project/cdlclient/)
[![PyPI status](https://img.shields.io/pypi/status/cdlclient.svg)](https://github.com/Codra-Ingenierie-Informatique/DataLabSimpleClient)
[![PyPI pyversions](https://img.shields.io/pypi/pyversions/cdlclient.svg)](https://pypi.python.org/pypi/cdlclient/)

ℹ️ Created by [Codra](https://codra.net/)/[Pierre Raybaut](https://github.com/PierreRaybaut) in 2023, developed and maintained by DataLab open-source project team.

ℹ️ DataLab is powered by [PlotPyStack](https://github.com/PlotPyStack) 🚀.

![PlotPyStack](https://raw.githubusercontent.com/PlotPyStack/.github/main/data/plotpy-stack-powered.png)

----

## About DataLab

DataLab is a generic signal and image processing software based on Python scientific
libraries (such as NumPy, SciPy or scikit-image) and Qt graphical user interfaces
(thanks to the powerful [PlotPyStack](https://github.com/PlotPyStack) - mostly the
[guidata](https://github.com/PlotPyStack/guidata) and
[PlotPy](https://github.com/PlotPyStack/PlotPy) libraries).

DataLab is available as a **stand-alone** application (see for example our all-in-one Windows installer) or as an **addon to your Python-Qt application** thanks to advanced automation and embedding features.

See [DataLab website](https://codra-ingenierie-informatique.github.io/DataLab/) for more details.

## About this package

DataLab Simple Client is a Python library that can be used to interact with a DataLab application (server).
This allows to control DataLab application from a remote computer, or/and from a third-party application.

DataLab Simple Client also provides ready-to-use widgets that can be used to communicate with a DataLab application:

* `ConnectionDialog`: a dialog box that allows to connect to a DataLab application

* `GetObjetDialog`: a dialog box that allows to retrieve an object from a DataLab application

`ConnectionDialog`         | `GetObjectDialog`
:-------------------------:|:-------------------------:
![ConnectionDialog](https://raw.githubusercontent.com/Codra-Ingenierie-Informatique/DataLabSimpleClient/main/doc/images/shots/connect_dialog.png) | ![GetObjectDialog](https://raw.githubusercontent.com/Codra-Ingenierie-Informatique/DataLabSimpleClient/main/doc/images/shots/get_object_dialog.png)

See [documentation](https://cdlclient.readthedocs.io/en/latest/) for more details on
the library and [changelog](https://github.com/Codra-Ingenierie-Informatique/DataLabSimpleClient/blob/main/CHANGELOG.md)
for recent history of changes.
