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
import tushare as ts

'''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''
Class Stock:
ReadETFdfStock(sStockName):                             Read ETF dfStock (ETF dfStock can only be stored on disk by hand);
GetTargetDateSection(dfStock, wDateStart, wDateEnd):    Get dfStock in target date section;
CalcHma(dfStock, period=12, column="close"):            Calc HMA of dfStock[column], based on "period";
CalcMacd(dfStock):                                      Calc MACD (12-26-9);
CalcHmacd(dfStock):                                     Calc HMACD (HMA12-HMA26-HMA9);
'''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''
class ClStock():
    def __init__(self):
        ### Passing params ###
        pass

        ### Call function ###

    ############################################################
    ### Read ETF dfStock (ETF dfStock can only be stored on disk by hand)
    ### Param - sStockName: ETF dfStock file name;
    ### Return dfStock
    ############################################################
    def ReadETFdfStock(self, sStockName):
        sUrl = os.path.join(os.path.abspath('./data'), sStockName + '.csv')
        dfStock = pd.read_csv(sUrl, parse_dates=False, index_col="date")
        return dfStock

    ############################################################
    ### Get dfStock in target date section
    ### Param - dfStock:    Stock dataframe;
    ### Param - wDateStart ～ wDateEnd:  Target date section;
    ### Return: dfStock in target date section;
    ############################################################
    def GetTargetDateSection(self, dfStock, wDateStart, wDateEnd):
        if(wDateStart < wDateEnd):
            dfStock = dfStock[dfStock.index >= wDateStart]
            dfStock = dfStock[dfStock.index <= wDateEnd]
            return dfStock
        else:
            print(">>> Error: Input param is invalid!\n")

    ############################################################
    ### Calc HMA of dfStock[column], based on "period"
    ### Param - dfStock:    Stock dataframe, which should have "column";
    ### Param - period:     HMA calc period;
    ### Param - column:     HMA calc data;
    ### Return: dataframe, which have index, column, "HMA";
    ############################################################
    def CalcHma(self, dfStock, period=12, column="close"):
        ### Create HMA ###
        dfStock["EMA_HT"] =  dfStock[column].ewm(alpha=2/(period/2+1), adjust=False, ignore_na=False).mean()
        dfStock["EMA_T"] =  dfStock[column].ewm(alpha=2/(period+1), adjust=False, ignore_na=False).mean()
        dfStock["Delta"] = dfStock["EMA_HT"] * 2 - dfStock["EMA_T"]
        dfStock["HMA"] =  dfStock["Delta"].ewm(alpha=2/(period**0.5+1), adjust=False, ignore_na=False).mean()
        dfStock = pd.DataFrame(dfStock, columns=[column, "HMA"])
        return dfStock

    ############################################################
    ### Calc MACD (12-26-9)
    ### Param - dfStock:    Should have "close";
    ### Return: dfStock, which have index, "close", "DIF", "DEA", "BAR";
    ############################################################
    def CalcMacd(self, dfStock):
        ### Create MACD ###
        dfStock["EMA12"] = dfStock["close"].ewm(alpha=2/13, adjust=False, ignore_na=False).mean()
        dfStock["EMA26"] = dfStock["close"].ewm(alpha=2/27, adjust=False, ignore_na=False).mean()
        dfStock["DIF"] = dfStock["EMA12"] - dfStock["EMA26"]
        dfStock["DEA"] = dfStock["DIF"].ewm(alpha=2 / 10, adjust=False, ignore_na=False).mean()
        dfStock["BAR"] = (dfStock["DIF"] - dfStock["DEA"]) * 2
        dfStock = pd.DataFrame(dfStock, columns=["close", "DIF", "DEA", "BAR"])
        print(dfStock)

    ############################################################
    ### Calc HMACD (HMA12-HMA26-HMA9)
    ### Param - dfStock:    Should have "close";
    ### Return: dfStock, which have index, "close", "HMA-DIF", "HMA-DEA", "HMA-BAR";
    ############################################################
    def CalcHmacd(self, dfStock):
        dfStock["HMA-12"] = (self.CalcHma(dfStock, period=12, column="close"))["HMA"]
        dfStock["HMA-26"] = (self.CalcHma(dfStock, period=26, column="close"))["HMA"]
        dfStock["HMA-DIF"] = dfStock["HMA-12"] - dfStock["HMA-26"]
        dfStock["HMA-DEA"] = (self.CalcHma(dfStock, period=9, column="HMA-DIF"))["HMA"]
        dfStock["HMA-BAR"] = (dfStock["HMA-DIF"] - dfStock["HMA-DEA"]) * 2
        dfStock = pd.DataFrame(dfStock, columns=["close", "HMA-DIF", "HMA-DEA", "HMA-BAR"])
        return dfStock
