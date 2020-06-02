#! /usr/bin/env python
# -*- encoding: utf-8 -*-

from ClGui import ClGui
from ClStock import ClStock
import warnings
#warnings.filterwarnings('ignore')


if __name__ == '__main__':
    sStockName = "510500 - 中证500ETF"
    uGui = ClGui(sStockName)
    uGui.MainLoop()
