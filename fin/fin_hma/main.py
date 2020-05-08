#! /usr/bin/env python
# -*- encoding: utf-8 -*-
from ClStock import ClStock
from ClGui import ClGui
import warnings
#warnings.filterwarnings('ignore')

DICT_STOCK={"510310":"HS300"}

if __name__ == '__main__':
    sStockCode = "510310"
    uStock = ClStock(sStockCode)
    uGui = ClGui(sStockCode, uStock.dfStock)
    uGui.MainLoop()
