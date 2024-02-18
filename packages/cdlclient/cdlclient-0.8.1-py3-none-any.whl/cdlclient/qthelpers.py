# -*- coding: utf-8 -*-
#
# Licensed under the terms of the BSD 3-Clause
# (see cdlclient/LICENSE for details)

"""Qt helpers"""

from __future__ import annotations

import os
import os.path as osp
from collections.abc import Generator
from contextlib import contextmanager

from qtpy import QtCore as QC
from qtpy import QtGui as QG
from qtpy import QtSvg as QS
from qtpy import QtWidgets as QW

from cdlclient.config import MOD_PATH

WIDGETS_PATH = osp.join(MOD_PATH, "widgets")


def svgtext_to_icon(text: str) -> QG.QIcon:
    """Convert SVG text to QIcon

    Args:
        text: SVG text

    Returns:
        Icon
    """
    svg_bytes = QC.QByteArray(text.encode("utf-8"))
    renderer = QS.QSvgRenderer(svg_bytes)  # pylint: disable=no-member
    pixmap = QG.QPixmap(64, 64)  # You can adjust the size as needed
    pixmap.fill(QC.Qt.transparent)  # Fill the pixmap with transparency
    painter = QG.QPainter(pixmap)
    renderer.render(painter)
    painter.end()
    return QG.QIcon(pixmap)


def svgfile_to_base64(filename: str) -> bytes:
    """Convert SVG file to Base64-encoded bytes

    Args:
        filename: SVG filename

    Returns:
        Base64-encoded bytes
    """
    image = QG.QImage(filename)
    data = QC.QByteArray()
    buf = QC.QBuffer(data)
    image.save(buf, "PNG")
    return data.toBase64().data()


def imagefile_to_base64(filename: str) -> bytes:
    """Convert image file to Base64-encoded bytes

    Args:
        filename: image filename

    Returns:
        Base64-encoded bytes
    """
    image = QG.QImage(filename)
    data = QC.QByteArray()
    buf = QC.QBuffer(data)
    image.save(buf, "PNG")
    return data.toBase64().data()


def imagefile_to_python_module(filename: str, destmod: str) -> None:
    """Convert image file to Python module

    Args:
        filename: image filename
        destmod: destination module name
    """
    data = imagefile_to_base64(filename)
    destmod_path = osp.join(WIDGETS_PATH, destmod + ".py")
    if osp.isfile(destmod_path):
        os.remove(destmod_path)
    with open(destmod_path, "wb") as fn:
        fn.write("# -*- coding: utf-8 -*-\n\n".encode("utf-8"))
        fn.write("# pylint: skip-file\n\n".encode("utf-8"))
        fn.write("DATA = b'".encode("utf-8"))
        fn.write(data)
        fn.write("'".encode("utf-8"))


@contextmanager
def block_signals(widget: QW.QWidget, enable: bool) -> Generator[None, None, None]:
    """Eventually block/unblock widget Qt signals before/after doing some things
    (enable: True if feature is enabled)"""
    if enable:
        widget.blockSignals(True)
    try:
        yield
    finally:
        if enable:
            widget.blockSignals(False)
            widget.blockSignals(False)
            widget.blockSignals(False)
            widget.blockSignals(False)
