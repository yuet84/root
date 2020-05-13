#! /usr/bin/env python
# -*- encoding: utf-8 -*-

from ClGui import ClGui
import warnings
#warnings.filterwarnings('ignore')

DICT_STOCK={"510310":"HS300"}

if __name__ == '__main__':
    sStockCode = "510310"
    uGui = ClGui(sStockCode, DICT_STOCK[sStockCode])
    uGui.MainLoop()
