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

    ############################################################
    ### Standard calc SMA (ser: Target data; T: SMA period; DateFrom:DateEnd: Target date) (Return serSma)
    ############################################################
    def CalcSma(self, ser, T, DateFrom, DateEnd):
        ### Create SMA ###
        serSma = ser.rolling(window=T).mean()
        ### Cut off the target date section ###
        serSma = serSma[serSma.index >= DateFrom]
        serSma = serSma[serSma.index <= DateEnd]
        return serSma

    ############################################################
    ### Standard calc HMA (ser: Target data; T: HMA period; DateFrom:DateEnd: Target date) (Return serHma)
    ############################################################
    def CalcHma(self, ser, T, DateFrom, DateEnd):
        ### Create HMA ###
        serHmaShort = ser.ewm(alpha=2 / T, adjust=False, ignore_na=True).mean() * 2
        serHmaLong = ser.ewm(alpha=1 / T, adjust=False, ignore_na=True).mean()
        serHmaDelta = serHmaShort - serHmaLong
        serHma = serHmaDelta.ewm(alpha=1 / (T ** 0.5), adjust=False, ignore_na=True).mean()
        ### Cut off the target date section ###
        serHma = serHma[serHma.index >= DateFrom]
        serHma = serHma[serHma.index <= DateEnd]
        return serHma




