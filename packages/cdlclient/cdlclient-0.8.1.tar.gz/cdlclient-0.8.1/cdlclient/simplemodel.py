# -*- coding: utf-8 -*-
#
# Licensed under the terms of the BSD 3-Clause
# (see cdlclient/LICENSE for details)

"""
DataLab Simple Model
"""

# pylint: disable=invalid-name  # Allows short reference names like x, y, ...

from __future__ import annotations

from typing import Any

import guidata.dataset as gds
from guidata.dataset.io import JSONReader

ROI_KEY = "_roi_"
ANN_KEY = "_ann_"


class BaseObj:
    """Base object"""

    # This is overriden in children classes with a gds.DictItem instance:
    metadata: dict[str, Any] = {}

    def __set_annotations(self, annotations: str | None) -> None:
        """Set object annotations (JSON string describing annotation plot items)

        Args:
            annotations (str | None): JSON string describing annotation plot items,
                or None to remove annotations
        """
        if annotations is None:
            if ANN_KEY in self.metadata:
                self.metadata.pop(ANN_KEY)
        else:
            self.metadata[ANN_KEY] = annotations

    def __get_annotations(self) -> str:
        """Get object annotations (JSON string describing annotation plot items)"""
        return self.metadata.get(ANN_KEY, "")

    annotations = property(__get_annotations, __set_annotations)

    def get_annotated_shapes(self):
        """Get annotated shapes"""
        from plotpy.io import load_items  # pylint: disable=import-outside-toplevel

        if self.annotations:
            return load_items(JSONReader(self.annotations))
        return []


class SignalObj(gds.DataSet, BaseObj):
    """Signal object (simplified version of DataLab's Signal object)"""

    uuid = gds.StringItem("UUID").set_prop("display", hide=True)

    _tabs = gds.BeginTabGroup("all")

    _datag = gds.BeginGroup("Data and metadata")
    title = gds.StringItem("Signal title", default="Untitled")
    xydata = gds.FloatArrayItem("Data", transpose=True, minmax="rows")
    metadata = gds.DictItem("Metadata", default={})
    _e_datag = gds.EndGroup("Data and metadata")

    _unitsg = gds.BeginGroup("Titles and units")
    title = gds.StringItem("Signal title", default="Untitled")
    _tabs_u = gds.BeginTabGroup("units")
    _unitsx = gds.BeginGroup("X-axis")
    xlabel = gds.StringItem("Title", default="")
    xunit = gds.StringItem("Unit", default="")
    _e_unitsx = gds.EndGroup("X-axis")
    _unitsy = gds.BeginGroup("Y-axis")
    ylabel = gds.StringItem("Title", default="")
    yunit = gds.StringItem("Unit", default="")
    _e_unitsy = gds.EndGroup("Y-axis")
    _e_tabs_u = gds.EndTabGroup("units")
    _e_unitsg = gds.EndGroup("Titles and units")

    _e_tabs = gds.EndTabGroup("all")


class ImageObj(gds.DataSet, BaseObj):
    """Image object (simplified version of DataLab's Image object)"""

    uuid = gds.StringItem("UUID").set_prop("display", hide=True)

    _tabs = gds.BeginTabGroup("all")

    _datag = gds.BeginGroup("Data")
    data = gds.FloatArrayItem("Data")
    metadata = gds.DictItem("Metadata", default={})
    _e_datag = gds.EndGroup("Data")

    _dxdyg = gds.BeginGroup("Origin / Pixel spacing")
    _origin = gds.BeginGroup("Origin")
    x0 = gds.FloatItem("X<sub>0</sub>", default=0.0)
    y0 = gds.FloatItem("Y<sub>0</sub>", default=0.0).set_pos(col=1)
    _e_origin = gds.EndGroup("Origin")
    _pixel_spacing = gds.BeginGroup("Pixel spacing")
    dx = gds.FloatItem("Δx", default=1.0, nonzero=True)
    dy = gds.FloatItem("Δy", default=1.0, nonzero=True).set_pos(col=1)
    _e_pixel_spacing = gds.EndGroup("Pixel spacing")
    _e_dxdyg = gds.EndGroup("Origin / Pixel spacing")

    _unitsg = gds.BeginGroup("Titles / Units")
    title = gds.StringItem("Image title", default="Untitled")
    _tabs_u = gds.BeginTabGroup("units")
    _unitsx = gds.BeginGroup("X-axis")
    xlabel = gds.StringItem("Title", default="")
    xunit = gds.StringItem("Unit", default="")
    _e_unitsx = gds.EndGroup("X-axis")
    _unitsy = gds.BeginGroup("Y-axis")
    ylabel = gds.StringItem("Title", default="")
    yunit = gds.StringItem("Unit", default="")
    _e_unitsy = gds.EndGroup("Y-axis")
    _unitsz = gds.BeginGroup("Z-axis")
    zlabel = gds.StringItem("Title", default="")
    zunit = gds.StringItem("Unit", default="")
    _e_unitsz = gds.EndGroup("Z-axis")
    _e_tabs_u = gds.EndTabGroup("units")
    _e_unitsg = gds.EndGroup("Titles / Units")

    _e_tabs = gds.EndTabGroup("all")
