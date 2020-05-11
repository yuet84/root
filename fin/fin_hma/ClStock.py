#!/usr/bin/env python 
# -*- coding:utf-8 -*-
import csv,os
import numpy as np
import pandas as pd
import pandas_datareader.data as web
import datetime
import codecs
import talib
from dateutil.relativedelta import relativedelta

##########################################################################################
### Class function:
###     ReaddfStock():          Read dfStock from local disk: File name = F:\root\fin\data\sStockCode.csv
##########################################################################################
class ClStock():
    def __init__(self, sStockCode):
        ### Passing params ###
        self.sStockCode = sStockCode

        ### Global params ###
        self.URL = os.path.join(os.path.abspath('../data'), self.sStockCode + '.csv')       #   Download stock data file

        ### Call function ###
        self.dfStock = self.ReaddfStock()                   # Read dfStock from disk

    ############################################################
    ### Read dfStock from local disk: File name = F:\root\fin\data\sStockCode.csv
    ############################################################
    def ReaddfStock(self):
        if not os.path.exists(self.URL):
            print(">>> Stock data - ", self.sStockCode, ": Not exist. Try to get stock data online!\n")
        else:
            dfStock = pd.read_csv(self.URL,                 # Read csv from local disk
                                  parse_dates=True,
                                  index_col=0)
            return dfStock



