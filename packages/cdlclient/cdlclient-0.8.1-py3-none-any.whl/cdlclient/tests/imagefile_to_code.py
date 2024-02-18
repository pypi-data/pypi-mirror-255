# -*- coding: utf-8 -*-
"""Convert PNG image to Python code"""

# guitest: skip

import os
import os.path as osp

from guidata.qthelpers import qt_app_context
from qtpy import QtCore as QC
from qtpy import QtGui as QG
from qtpy import QtWidgets as QW

from cdlclient.config import MOD_NAME, MOD_PATH
from cdlclient.qthelpers import imagefile_to_python_module

RES_PATH = osp.join(MOD_PATH, os.pardir, "resources")


def test_conv(filename: str, destmod: str) -> None:
    """Test image to code conversion

    Args:
        filename: image filename
        destmod: destination module name
    """
    with qt_app_context(exec_loop=True):
        widget = QW.QWidget()
        vlayout = QW.QVBoxLayout()
        widget.setLayout(vlayout)
        label1 = QW.QLabel()
        label1.setPixmap(QG.QPixmap(filename))
        label2 = QW.QLabel()
        imagefile_to_python_module(filename, destmod)
        mod = __import__(f"{MOD_NAME}.widgets.{destmod}", fromlist=[destmod])
        pixmap = QG.QPixmap()
        pixmap.loadFromData(QC.QByteArray.fromBase64(mod.DATA))
        label2.setPixmap(pixmap)
        vlayout.addWidget(label1)
        vlayout.addWidget(label2)
        widget.show()


if __name__ == "__main__":
    test_conv(osp.join(RES_PATH, "DataLab-Banner-200.png"), "datalab_banner")
