#! /usr/bin/env python
# -*- encoding: utf-8 -*-
from ClStock import ClStock
from ClGui import ClGui
import warnings
#warnings.filterwarnings('ignore')

if __name__ == '__main__':
    #sStockCode = "1A0001"
    sStockCode = "510310"           # HS300
    uStock = ClStock(sStockCode)
    #uStock.FixFundUpdate("2015-01-10")
    uGui = ClGui(sStockCode, uStock.dfStock)
    uGui.MainLoop()
