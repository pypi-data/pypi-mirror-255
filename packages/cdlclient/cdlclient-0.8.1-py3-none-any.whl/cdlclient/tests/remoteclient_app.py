# -*- coding: utf-8 -*-
#
# Licensed under the terms of the BSD 3-Clause
# (see cdlclient/LICENSE for details)

"""
DataLab Remote client application test
"""

# pylint: disable=invalid-name  # Allows short reference names like x, y, ...
# pylint: disable=duplicate-code

# guitest: show

from __future__ import annotations

import functools
from contextlib import contextmanager

import numpy as np
from guidata.env import execenv
from guidata.qthelpers import qt_app_context, qt_wait
from qtpy import QtWidgets as QW

from cdlclient import SimpleRemoteProxy
from cdlclient.config import _
from cdlclient.tests.remoteclient_base import AbstractClientWindow
from cdlclient.tests.remoteclient_unit import multiple_commands
from cdlclient.widgets import ConnectionDialog, GetObjectDialog

APP_NAME = "Remote client test"


def try_send_command():
    """Try and send command to DataLab application remotely"""

    def try_send_command_decorator(func):
        """Try... except... decorator"""

        @functools.wraps(func)
        def method_wrapper(*args, **kwargs):
            """Decorator wrapper function"""
            self: HostWindow = args[0]  # extracting 'self' from method arguments
            output = None
            try:
                output = func(*args, **kwargs)
            except ConnectionRefusedError:
                self.cdl = None
                message = "🔥 Connection refused 🔥 (server is not ready?)"
                self.host.log(message)
                QW.QMessageBox.critical(self, APP_NAME, message)
            return output

        return method_wrapper

    return try_send_command_decorator


class HostWindow(AbstractClientWindow):
    """Test main view"""

    PURPOSE = _("This the client application, which connects to DataLab.")
    INIT_BUTTON_LABEL = _("Connect to DataLab")
    SIG_TITLES = ("Oscilloscope", "Digitizer", "Radiometer", "Voltmeter", "Sensor")
    IMA_TITLES = (
        "Camera",
        "Streak Camera",
        "Image Scanner",
        "Laser Beam Profiler",
        "Gated Imaging Camera",
    )

    def init_cdl(self):
        """Open DataLab test"""
        if self.cdl is None:
            self.cdl: SimpleRemoteProxy = SimpleRemoteProxy()
            connect_dlg = ConnectionDialog(self.cdl.connect, self)
            ok = connect_dlg.exec()
            if ok:
                self.host.log("✨ Initialized DataLab connection ✨")
                self.host.log(f"  Communication port: {self.cdl.port}")
                self.host.log("  List of exposed methods:")
                for name in self.cdl.get_method_list():
                    self.host.log(f"    {name}")
            else:
                self.cdl = None
                self.host.log("🔥 Connection refused 🔥 (server is not ready?)")

    @try_send_command()
    def close_cdl(self):
        """Close DataLab window"""
        if self.cdl is not None:
            self.cdl.close_application()
            self.host.log("🎬 Closed DataLab!")
            self.cdl = None

    def add_additional_buttons(self):
        """Add additional buttons"""
        add_btn = self.host.add_button
        add_btn(_("Execute multiple commands"), self.exec_multiple_cmd, 10)
        add_btn(_("Get object titles"), self.get_object_titles, 10)
        add_btn(_("Get object uuids"), self.get_object_uuids, 10)
        add_btn(_("Get object"), self.get_object)
        add_btn(_("Get object using dialog box"), self.get_object_dialog)

    @try_send_command()
    def exec_multiple_cmd(self):
        """Execute multiple commands in DataLab"""
        if self.cdl is not None:
            self.host.log("Starting command sequence...")
            multiple_commands(self.cdl)
            self.host.log("...end")

    @try_send_command()
    def get_object_titles(self):
        """Get object (signal/image) titles for current panel"""
        if self.cdl is not None:
            self.host.log("Object titles:")
            titles = self.cdl.get_object_titles()
            if titles:
                for name in titles:
                    self.host.log(f"  {name}")
            else:
                self.host.log("  Empty.")

    @try_send_command()
    def get_object_uuids(self):
        """Get object (signal/image) uuids for current panel"""
        if self.cdl is not None:
            self.host.log("Object uuids:")
            uuids = self.cdl.get_object_uuids()
            if uuids:
                for uuid in uuids:
                    self.host.log(f"  {uuid}")
            else:
                self.host.log("  Empty.")

    @try_send_command()
    def get_object(self):
        """Get object (signal/image) at index for current panel"""
        if self.cdl is not None:
            titles = self.cdl.get_object_titles()
            if titles:
                obj = self.cdl.get_object()
                self.host.log(f"Object '{obj.title}'")
                self.host.log(str(obj))
            else:
                self.host.log("🏴‍☠️ Object list is empty!")

    @try_send_command()
    def get_object_dialog(self):
        """Get object (signal/image) using dialog box"""
        if self.cdl is not None:
            dialog = GetObjectDialog(self, self.cdl)
            if dialog.exec():
                uuid = dialog.get_current_object_uuid()
                obj = self.cdl.get_object(uuid)
                self.host.log(f"Object '{obj.title}'")
                self.host.log(str(obj))

    def add_signals(self):
        """Add signals to DataLab"""
        if self.cdl is not None:
            x = np.linspace(0, 10, 1000)
            for title, y in (
                ("Sinus", np.sin(x)),
                ("Cosinus", np.cos(x)),
                ("Tan", np.tan(x)),
            ):
                self.cdl.add_signal(title, x, y)
                self.host.log(f"Added signal: {title}")

    def add_images(self):
        """Add images to DataLab"""
        if self.cdl is not None:
            for title, z in (
                ("Zeros", np.zeros((100, 100))),
                ("Ones", np.ones((100, 100))),
                ("Random", np.random.random((100, 100))),
            ):
                self.cdl.add_image(title, z)
                self.host.log(f"Added image: {title}")

    @try_send_command()
    def remove_all(self):
        """Remove all objects from DataLab"""
        if self.cdl is not None:
            self.cdl.reset_all()
            self.host.log("Removed all objects")


@contextmanager
def qt_wait_print(dt: float, message: str):
    """Wait and print message"""
    qt_wait(dt)
    execenv.print(f"{message}...", end="")
    yield
    execenv.print("OK")


def test_remote_client():
    """Remote client test"""
    with qt_app_context(exec_loop=True):
        window = HostWindow()
        window.resize(800, 800)
        window.show()
        dt = 1
        if execenv.unattended:
            qt_wait(2)
            window.init_cdl()
            with qt_wait_print(dt, "Executing multiple commands"):
                window.exec_multiple_cmd()
            with qt_wait_print(dt, "Raising DataLab window"):
                window.raise_cdl()
            with qt_wait_print(dt, "Getting object titles"):
                window.get_object_titles()
            with qt_wait_print(dt, "Getting object uuids"):
                window.get_object_uuids()
            with qt_wait_print(dt, "Getting object"):
                window.cdl.select_objects([1])
                window.get_object()
            with qt_wait_print(dt, "Adding signals"):
                window.add_signals()
            with qt_wait_print(dt, "Adding images"):
                window.add_images()
            with qt_wait_print(dt, "Removing all objects"):
                window.remove_all()
            with qt_wait_print(dt, "Closing DataLab"):
                window.close_cdl()


if __name__ == "__main__":
    test_remote_client()
