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
------------------------------------------------------------------------------------------
    Standard module:
    CalcSma(self, ser, T, DateFrom, DateEnd):       Calc SMA (ser: Target data; T: SMA period; DateFrom:DateEnd: Target date) (Return serSma)
    CalcHma(self, ser, T, DateFrom, DateEnd):       Calc HMA (ser: Target data; T: HMA period; DateFrom:DateEnd: Target date) (Return serHma)
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
    def GetdfStockOnline(self, sDateFrom='20100101'):
        dfStockList = self.GetStockListOnline()
        dfTsCode = dfStockList[["ts_code","name"]][dfStockList["symbol"] == self.sStockCode]
        if(len(dfTsCode.index) != 1):
            print(">>> Error: Ts code number is invalid!\n")
            return
        pro = ts.pro_api('85682a790fc2446f2953918e90c9022c9f025f10cac75191551aad9c')
        sUrl = os.path.join(os.path.abspath('./data'), dfTsCode.iloc[0]["ts_code"] + " - " + dfTsCode.iloc[0]["name"] + '.csv')
        dfStock = pro.query('daily', ts_code=dfTsCode.iloc[0]["ts_code"], start_date=sDateFrom, end_date=datetime.date.today().strftime('%Y%m%d'))
        dfStock.to_csv(sUrl, index=False, columns=["trade_date", "open", "high", "low", "close", "amount"])  # index=False: 不保留行索引;
        dfStock = pd.read_csv(sUrl, index_col="trade_date").sort_index(ascending=True)
        return dfTsCode.iloc[0]["ts_code"], dfTsCode.iloc[0]["name"], dfStock

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
    def CalcSma(self, ser, T, sDateFrom, sDateEnd):
        ### Create SMA ###
        serSma = ser.rolling(window=T).mean()
        ### Cut off the target date section ###
        serSma = serSma[serSma.index >= sDateFrom]
        serSma = serSma[serSma.index <= sDateEnd]
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

    ############################################################
    ### Standard calc MACD (12-26-9)
    ### Param - dfStock:    Should have "close";
    ### Param - wDateStart:wDateEnd:    Target date section;
    ### Return: dfMacd, which have index, "close", "diff", "dea", "bar";
    ############################################################
    def CalcMacd(self, dfStock, wDateStart, wDateEnd):
        ### Create MACD ###
        dfMacd = pd.DataFrame(dfStock, columns=["close"])
        dfMacd["diff"], dfMacd["dea"], dfMacd["bar"] = talib.MACD(dfStock['close'].values, fastperiod=12, slowperiod=26, signalperiod=9)
        ### Get target date section ###
        dfMacd = dfMacd[dfMacd.index >= wDateStart]
        dfMacd = dfMacd[dfMacd.index <= wDateEnd]
        return dfMacd




