# -*- coding: utf-8 -*-
#
# Licensed under the terms of the BSD 3-Clause
# (see cdlclient/LICENSE for details)

"""
DataLab Simple Client configuration module
------------------------------------------

This module handles `DataLab Simple Client` configuration.
"""

from __future__ import annotations

import os.path as osp

from guidata import configtools

MOD_NAME = "cdlclient"
_ = configtools.get_translation(MOD_NAME)

MOD_PATH = configtools.get_module_data_path(MOD_NAME)
