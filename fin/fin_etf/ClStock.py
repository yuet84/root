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
    ReaddfStock(self, sUrl):        Read dfStock from local disk (sUrl: Stock file) (Return dfStock);
    GetTargetDateSection(dfStock, wDateStart, wDateEnd):    Return dfStock in target date section;
    CalcHma(dfStock, T):            Calc HMA (T);
    CalcMacd(dfStock):              Calc MACD (12-26-9):
    CalcHmacd(dfStock):             Calc HMACD (12-26-9);
'''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''
class ClStock():
    def __init__(self, sStockCode = None):
        ### Passing params ###
        self.sStockCode = sStockCode

        ### Call function ###
        #self.dfStock = self.ReaddfStock(self.URL)           # Read dfStock from disk
        #self.CalcHmaTrend()

    ############################################################
    ### Get stock (SH & SZ) list from online (void)
    ### Return: Stock (SH & SZ) list dataframe (Also store file "./data/000000.csv)
    ### Note:   Use notepadd++ to check stock list file (Not excel)
    ############################################################
    def GetStockListOnline(self):
        pro = ts.pro_api('85682a790fc2446f2953918e90c9022c9f025f10cac75191551aad9c')
        sUrl = os.path.join(os.path.abspath('./data'), "000000" + '.csv')
        dfStockList = pro.query('stock_basic', exchange='', list_status='L', fields='ts_code, symbol, name, area, industry, market, list_date')
        dfStockList.to_csv(sUrl, index=False, columns=["ts_code", "name", "area", "industry", "market", "list_date"], encoding='utf-8')  # index=False: 不保留行索引;
        return dfStockList

    ############################################################
    ### Get dfStock from online (From 20100101 - now())
    ### Return: sTsCode, sName, dfStock (From 20100101 to now()) (Also store file "./data/ts_code - name.csv)
    ############################################################
    def GetdfStockOnline(self, sDateFrom='19900101'):
        dfStockList = self.GetStockListOnline()
        dfTsCode = dfStockList[["ts_code","name"]][dfStockList["symbol"] == self.sStockCode]
        if(len(dfTsCode.index) != 1):
            print(">>> Error: Ts code number is invalid!\n")
            return
        pro = ts.pro_api('85682a790fc2446f2953918e90c9022c9f025f10cac75191551aad9c')
        sUrl = os.path.join(os.path.abspath('./data'), dfTsCode.iloc[0]["ts_code"] + " - " + dfTsCode.iloc[0]["name"] + '.csv')
        dfStock = pro.query('daily', ts_code=dfTsCode.iloc[0]["ts_code"], start_date=sDateFrom, end_date=datetime.date.today().strftime('%Y%m%d'))
        print(dfStock)
        dfStock["close"] = (dfStock["open"] + dfStock["close"]) / 2
        dfStock.to_csv(sUrl, index=False, columns=["trade_date", "close", "close", "amount"])  # index=False: 不保留行索引;
        dfStock = pd.read_csv(sUrl, index_col="trade_date").sort_index(ascending=True)
        return dfTsCode.iloc[0]["ts_code"], dfTsCode.iloc[0]["name"], dfStock

    ############################################################
    ### Read dfStock from local disk (sUrl: Stock file) (Return dfStock)
    ############################################################
    def ReaddfStockOnDisk(self, sStockName):
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
    ### Calc HMA (T)
    ### Param - dfStock:    Should have "close";
    ### Param - T:  HMA period;
    ### Return: dfMacd, which have index, "close", "hma";
    ############################################################
    def CalcHma(self, dfStock, T):
        ### Create HMA ###
        dfHma = pd.DataFrame(dfStock, columns=["close"])
        dfHma["short"] = dfHma["close"].ewm(alpha=2 / T, adjust=False, ignore_na=True).mean() * 2
        dfHma["long"] = dfHma["close"].ewm(alpha=1 / T, adjust=False, ignore_na=True).mean()
        dfHma["delta"] = dfHma["short"] - dfHma["long"]
        dfHma["hma"] = dfHma["delta"].ewm(alpha=1 / T ** 0.5, adjust=False, ignore_na=True).mean()
        return dfHma

    ############################################################
    ### Calc MACD (12-26-9)
    ### Param - dfStock:    Should have "close";
    ### Return: dfMacd, which have index, "close", "diff", "dea", "bar";
    ############################################################
    def CalcMacd(self, dfStock):
        ### Create MACD ###
        dfMacd = pd.DataFrame(dfStock, columns=["close"])
        dfMacd["diff"], dfMacd["dea"], dfMacd["bar"] = talib.MACD(dfStock['close'].values, fastperiod=12, slowperiod=26, signalperiod=9)
        return dfMacd

    ############################################################
    ### Calc HMACD (12-26-9)
    ### Param - dfStock:    Should have "close";
    ### Return: dfHmacd, which have index, "close", "diff", "dea", "bar";
    ############################################################
    def CalcHmacd(self, dfStock):
        ### Create MACD ###
        dfHmacd = pd.DataFrame(dfStock, columns=["close"])
        dfHmaT12 = self.CalcHma(dfHmacd, 12)
        dfHmaT26 = self.CalcHma(dfHmacd, 26)
        dfHmacd["diff"] = dfHmaT12["hma"] - dfHmaT26["hma"]
        df = dfHmacd
        df["close"] = dfHmacd["diff"]
        dfHmaDea =  self.CalcHma(df, 8)
        dfHmacd["dea"] = dfHmaDea["hma"]
        dfHmacd["bar"] = (dfHmacd["diff"] - dfHmacd["dea"]) * 2
        #dfHmacd["bar"] = (dfHmaT12["hma"] - dfHmaT26["hma"]) * 2
        return dfHmacd


    def CalcHmaTrend(self):
        serHmaShort = self.CalcHma(self.dfStock["Close"], 12, self.dfStock.index[0], self.dfStock.index[-1])
        serHmaLong = self.CalcHma(self.dfStock["Close"], 26, self.dfStock.index[0], self.dfStock.index[-1])
        serHmaTrend = np.sign(serHmaShort - serHmaLong)

        wHmaTrend = 1
        wInvQuota = 0
        wTotalPofit = 10000
        wCnt = 0
        for i in np.arange(0, len(self.dfStock.index)):
            if(serHmaTrend[i] == 1) and (wHmaTrend == -1):          # Gold cross
                wHmaTrend = 1
                wInvQuota = round(wTotalPofit / self.dfStock.loc[self.dfStock.index[i], "Close"] / 100) * 100
                wCnt = wCnt + 1
                print("Cnt = ", wCnt, ";\t", self.dfStock.index[i], ";\t Quota: ", wInvQuota, ";\t Close: ", self.dfStock.loc[self.dfStock.index[i], "Close"])
            elif(serHmaTrend[i] == -1) and (wHmaTrend == 1):        # Dead cross
                wHmaTrend = -1
                if(wInvQuota > 0):
                    wTotalPofit = wInvQuota * self.dfStock.loc[self.dfStock.index[i], "Close"]
                    wInvQuota = 0
                    print("Sell: ", self.dfStock.index[i], " - ", wTotalPofit)
        print("Total profit = ", wTotalPofit)