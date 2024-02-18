# -*- coding: utf-8 -*-
#
# Licensed under the terms of the BSD 3-Clause
# (see cdlclient/LICENSE for details)

"""
DataLab Remote client test base classes
"""

# pylint: disable=invalid-name  # Allows short reference names like x, y, ...
# guitest: skip

import abc

from guidata.qthelpers import get_std_icon, win32_fix_title_bar_background
from guidata.widgets.codeeditor import CodeEditor
from qtpy import QtWidgets as QW

from cdlclient.config import _


class HostWidget(QW.QWidget):
    """Host widget: menu with action buttons, log viewer"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.button_layout = QW.QVBoxLayout()
        self.logwidget = CodeEditor(self)
        self.logwidget.setMinimumWidth(500)
        grid_layout = QW.QGridLayout()
        grid_layout.addLayout(self.button_layout, 0, 0)
        grid_layout.addWidget(self.logwidget, 0, 1)
        self.setLayout(grid_layout)

    def log(self, message):
        """Log message"""
        self.logwidget.appendPlainText(message)

    def add_spacing(self, spacing: int) -> None:
        """Add spacing to button box"""
        self.button_layout.addSpacing(spacing)

    def add_label(self, text: str) -> None:
        """Add label to button box"""
        self.button_layout.addWidget(QW.QLabel(text))

    def add_widget(self, obj: QW.QWidget, spacing_before: int = 0) -> None:
        """Add widget (QWidget) to button box"""
        if spacing_before > 0:
            self.add_spacing(spacing_before)
        self.button_layout.addWidget(obj)

    def add_button(self, title, slot, spacing_before=0, icon=None):
        """Add button"""
        btn = QW.QPushButton(title)
        if icon is not None:
            btn.setIcon(get_std_icon(icon))
        btn.clicked.connect(lambda _checked=False: slot())
        self.add_widget(btn, spacing_before=spacing_before)
        return btn

    def add_stretch(self):
        """Add stretch to button box"""
        self.button_layout.addStretch()


class AbstractClientWindowMeta(type(QW.QMainWindow), abc.ABCMeta):
    """Mixed metaclass to avoid conflicts"""


class AbstractClientWindow(QW.QMainWindow, metaclass=AbstractClientWindowMeta):
    """Abstract client window, to embed DataLab or connect to it"""

    PURPOSE = None
    INIT_BUTTON_LABEL = None
    SIG_TITLES = ("Oscilloscope", "Digitizer", "Radiometer", "Voltmeter", "Sensor")
    IMA_TITLES = (
        "Camera",
        "Streak Camera",
        "Image Scanner",
        "Laser Beam Profiler",
        "Gated Imaging Camera",
    )

    def __init__(self):
        super().__init__()
        win32_fix_title_bar_background(self)
        self.setWindowTitle(_("Host application"))
        self.setWindowIcon(get_std_icon("ComputerIcon"))
        self.cdl = None  # CDLMainWindow instance
        self.host = HostWidget(self)
        self.setCentralWidget(self.host)
        self.setup_window()
        self.host.add_stretch()
        self.index_sigtitle = -1
        self.index_imatitle = -1

    @property
    def sigtitle(self):
        """Return current signal title index"""
        self.index_sigtitle = idx = (self.index_sigtitle + 1) % len(self.SIG_TITLES)
        return self.SIG_TITLES[idx]

    @property
    def imatitle(self):
        """Return current image title index"""
        self.index_imatitle = idx = (self.index_imatitle + 1) % len(self.IMA_TITLES)
        return self.IMA_TITLES[idx]

    def setup_window(self):
        """Setup window"""
        self.host.add_label(self.PURPOSE)
        add_btn = self.host.add_button
        add_btn(self.INIT_BUTTON_LABEL, self.init_cdl, 10, "DialogApplyButton")
        add_btn(_("Raise window"), self.raise_cdl, 0, "FileDialogToParent")
        self.add_additional_buttons()
        add_btn(_("Add signal objects"), self.add_signals, 10, "CommandLink")
        add_btn(_("Add image objects"), self.add_images, 0, "CommandLink")
        add_btn(_("Remove all objects"), self.remove_all, 5, "MessageBoxWarning")
        add_btn(_("Close DataLab"), self.close_cdl, 10, "DialogCloseButton")

    def add_additional_buttons(self):
        """Add additional buttons"""

    @abc.abstractmethod
    def init_cdl(self):
        """Open DataLab test"""

    def raise_cdl(self):
        """Raise DataLab window"""
        if self.cdl is not None:
            self.cdl.raise_window()
            self.host.log("=> Raised DataLab window")

    @abc.abstractmethod
    def close_cdl(self):
        """Close DataLab window"""

    @abc.abstractmethod
    def add_signals(self):
        """Add signals to DataLab"""

    @abc.abstractmethod
    def add_images(self):
        """Add images to DataLab"""

    @abc.abstractmethod
    def remove_all(self):
        """Remove all objects from DataLab"""

    def remove_all(self):
        """Remove all objects from DataLab"""
