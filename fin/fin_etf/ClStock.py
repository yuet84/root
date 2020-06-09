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
        dfStock = pd.read_csv(sUrl, parse_dates=False, index_col="date", engine='python')
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
        df = pd.DataFrame()
        df[column] = dfStock[column]
        df["Ema_Short"] =  df[column].ewm(alpha=2/(period/2+1), adjust=False, ignore_na=False).mean()
        df["Ema_Long"] =  df[column].ewm(alpha=2/(period+1), adjust=False, ignore_na=False).mean()
        df["Delta"] = df["Ema_Short"] * 2 - df["Ema_Long"]
        df["Hma"] =  df["Delta"].ewm(alpha=2/(period**0.5+1), adjust=False, ignore_na=False).mean()
        df = pd.DataFrame(df, columns=[column, "Hma"])
        return df

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

    ############################################################
    ### Calc HMACD (HMA12-HMA26-HMA9)
    ### Param - dfStock:    Should have "close";
    ### Return: dfStock, which have index, "close", "HMA-DIF", "HMA-DEA", "HMA-BAR";
    ############################################################
    def CalcHmacdTmp(self, dfStock):
        dfStock["HMA-12"] = (self.CalcHma(dfStock, period=34, column="close"))["HMA"]
        dfStock["HMA-26"] = (self.CalcHma(dfStock, period=36, column="close"))["HMA"]
        dfStock["HMA-DIF"] = dfStock["HMA-12"] - dfStock["HMA-26"]
        dfStock["HMA-DEA"] = (self.CalcHma(dfStock, period=6, column="HMA-DIF"))["HMA"]
        #dfStock["HMA-BAR"] = (dfStock["HMA-DIF"] - dfStock["HMA-DEA"]) * 2
        dfStock["HMA-BAR"] = (dfStock["HMA-12"] - dfStock["HMA-26"])
        dfStock = pd.DataFrame(dfStock, columns=["close", "HMA-DIF", "HMA-DEA", "HMA-BAR"])
        return dfStock

    def CalcHmaTrade(self, sStockName):
        df = pd.DataFrame()
        ### Get dfStock ###
        dfStock = self.ReadETFdfStock(sStockName)
        ### Get HMA ###
        df["Close"] = dfStock["close"]
        df["Hma-12"] = (self.CalcHma(df, period=12, column="Close"))["Hma"]
        df["Hma-24"] = (self.CalcHma(df, period=24, column="Close"))["Hma"]
        df["Hma-50"] = (self.CalcHma(df, period=24, column="Close"))["Hma"]
        ### Get trend: "Hma-12" cross "Hma-24" ###
        df["Trend-Hma-12-24"] =  df["Hma-12"] - df["Hma-24"]
        ### Get trend: "Hma-12" cross "Hma-50" ###
        df["Trend-Hma-12-50"] =  df["Hma-12"] - df["Hma-50"]
        ### Get "Hma-24" trend ###
        df["Trend-Hma-24"] = df["Hma-24"] - df["Hma-24"].shift(1)
        df["Trend-Hma-24"] = (self.CalcHma(df, period=6, column="Trend-Hma-24"))["Hma"]
        ### Get "Hma-50" trend ###
        df["Hma-50-Trend"] = df["Hma-50"] - df["Hma-50"].shift(1)
        df["Hma-50-Trend"] = (self.CalcHma(df, period=6, column="Hma-50-Trend"))["Hma"]
        ### Get "Gold" trend ###
        df["Trade"] = np.where( (df["Trend-Hma-12-24"] > 0) and (df["Trend-Hma-12-50"] > 0), 1, 0)
        df["Trade"] = df["Trade"] + np.where(df["Trend-Hma-24"] < 0, -1, 0)
        ### Get "Dead" trend ###
        #df["Dead"] = np.where(df["Trend-Hma-12-24"] < 0, df["Trend-Hma-12-24"], 0)

        ### Get target date section ###
        df = self.GetTargetDateSection(df, "20150101", "20200101")
        sUrl = r"D:\gitHub\root\fin\fin_etf\0.csv"
        df.to_csv(sUrl, index=True)

        ### Trade ###
        bIsHold = 0
        wCash = 10000
        for row in df.itertuples():
            if( (row.Trade > 0) and (bIsHold == 0) ):        # Buy
                wLot = int(wCash / row.Close / 100) * 100
                wCash = wCash - wLot * row.Close
                bIsHold = 1
                print("Buy on ", row[0], ":  Lot = ", wLot, ";  Cash = ", wLot * row.Close + wCash, ";\n")

            if( (row.Trade < 0) and (bIsHold == 1) ):
                wCash = wCash + wLot * row.Close
                bIsHold = 0
                print("Sold on ", row[0], ":  Lot = ", wLot, ";  Cash = ", wCash, ";\n")

        if(bIsHold == 0):
            print("Hold none. wCash = ", wCash, ";\n")
        else:
            print("Hold. Share cash = ", wCash + wLot * df.iloc[-1]["Close"], ";\n")

        #print(df)
        return
