# -*- coding: utf-8 -*-
#
# Licensed under the terms of the BSD 3-Clause
# (see cdlclient/LICENSE for details)

"""
DataLab Remote client unit test
"""

# pylint: disable=invalid-name  # Allows short reference names like x, y, ...
# pylint: disable=duplicate-code
# guitest: skip

from __future__ import annotations

import os.path as osp
import tempfile
import time
from collections.abc import Generator
from contextlib import contextmanager

import numpy as np
from guidata.env import execenv
from plotpy.builder import make

from cdlclient.remote import SimpleRemoteProxy


@contextmanager
def temporary_directory() -> Generator[str, None, None]:
    """Create a temporary directory and clean-up afterwards"""
    tmp = tempfile.TemporaryDirectory()  # pylint: disable=consider-using-with
    try:
        yield tmp.name
    finally:
        try:
            tmp.cleanup()
        except (PermissionError, RecursionError):
            pass


def multiple_commands(remote: SimpleRemoteProxy):
    """Execute multiple XML-RPC commands"""
    with temporary_directory() as tmpdir:
        x = np.linspace(-10, 10, 1000)
        y = np.sin(x)
        remote.add_signal("tutu", x, y)

        z = np.random.rand(200, 200)
        remote.add_image("toto", z)
        rect = make.annotated_rectangle(100, 100, 200, 200, title="Test")
        area = rect.get_rect()
        remote.add_annotations_from_items([rect])
        uuid = remote.get_sel_object_uuids()[0]
        items = remote.get_object_shapes()
        assert len(items) == 1 and items[0].get_rect() == area
        execenv.print("OK")
        remote.add_label_with_title(f"Image uuid: {uuid}")
        remote.select_groups([1])
        remote.select_objects([uuid])
        remote.delete_metadata()

        fname = osp.join(tmpdir, osp.basename("remote_test.h5"))
        remote.save_to_h5_file(fname)
        remote.reset_all()
        remote.open_h5_files([fname], True, False)
        remote.import_h5_file(fname, True)
        remote.set_current_panel("signal")
        assert remote.get_current_panel() == "signal"
        remote.calc("log10")

        remote.calc("fft")

        time.sleep(2)  # Avoid permission error when trying to clean-up temporary files


def test():
    """Remote client test"""
    remote = SimpleRemoteProxy()
    remote.connect()
    execenv.print("Executing multiple commands...", end="")
    multiple_commands(remote)
    execenv.print("OK")


if __name__ == "__main__":
    test()
