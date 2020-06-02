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

'''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''
Class Stock:
    ReaddfStock(self, sUrl):        Read dfStock from local disk (sUrl: Stock file) (Return dfStock);
------------------------------------------------------------------------------------------
    Standard module:
    CalcSma(self, ser, T, DateFrom, DateEnd):       Calc SMA (ser: Target data; T: SMA period; DateFrom:DateEnd: Target date) (Return serSma)
    CalcHma(self, ser, T, DateFrom, DateEnd):       Calc HMA (ser: Target data; T: HMA period; DateFrom:DateEnd: Target date) (Return serHma)
'''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''
class ClStock():
    def __init__(self, sStockCode):
        ### Passing params ###
        self.sStockCode = sStockCode

        ### Global params ###
        self.URL = os.path.join(os.path.abspath('../data'), self.sStockCode + '.csv')       #   Download stock data file

        ### Call function ###
        self.dfStock = self.ReaddfStock(self.URL)           # Read dfStock from disk

    ############################################################
    ### Read dfStock from local disk (sUrl: Stock file) (Return dfStock)
    ############################################################
    def ReaddfStock(self, sUrl):
        if not os.path.exists(self.URL):
            print(">>> Stock data - ", self.sStockCode, ": Not exist. Try to get stock data online!\n")
        else:
            dfStock = pd.read_csv(sUrl,                     # Read csv from local disk
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




