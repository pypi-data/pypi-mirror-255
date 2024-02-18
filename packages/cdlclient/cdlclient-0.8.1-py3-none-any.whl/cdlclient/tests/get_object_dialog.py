# -*- coding: utf-8 -*-
#
# Licensed under the terms of the BSD 3-Clause
# (see cdlclient/LICENSE for details)

"""
DataLab Remote client get object dialog example
"""

# guitest: show

from guidata.qthelpers import qt_app_context

from cdlclient import SimpleRemoteProxy
from cdlclient.widgets import GetObjectDialog


def test_dialog():
    """Test connection dialog"""
    proxy = SimpleRemoteProxy()
    proxy.connect()
    with qt_app_context():
        # 1. Select an image or signal object
        dlg = GetObjectDialog(None, proxy)
        if dlg.exec():
            obj = proxy.get_object(dlg.get_current_object_uuid())
            print(str(obj))
        # 2. Select a signal object only
        dlg = GetObjectDialog(None, proxy, panel="signal")
        if dlg.exec():
            obj = proxy.get_object(dlg.get_current_object_uuid())
            print(str(obj))
        # 3. Select an image object only
        dlg = GetObjectDialog(None, proxy, panel="image")
        if dlg.exec():
            obj = proxy.get_object(dlg.get_current_object_uuid())
            print(str(obj))


if __name__ == "__main__":
    test_dialog()
