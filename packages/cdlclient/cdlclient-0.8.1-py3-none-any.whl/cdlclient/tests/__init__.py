# -*- coding: utf-8 -*-
#
# Licensed under the terms of the BSD 3-Clause
# (see cdlclient/LICENSE for details)

"""
DataLab Simple Client unit tests
"""

from __future__ import annotations

from guidata.guitest import run_testlauncher

import cdlclient


def run() -> None:
    """Run DataLab test launcher"""
    run_testlauncher(cdlclient)


if __name__ == "__main__":
    run()
