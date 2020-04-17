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
###     CreateMA():             Create MA: 'MA1/5/10/20/30/40/50/60/120/240'
##########################################################################################
class ClStock():
    def __init__(self,sStockCode):
        self.sStockCode = sStockCode

        self.URL = os.path.join(r"F:\root\fin\data", self.sStockCode + '.csv')
        self.dfStock = self.ReaddfStock()                   # Read dfStock from disk
        self.CreateMA()                                     # Create MA
        self.CreateThre()

    ############################################################
    ### Read dfStock from local disk: File name = F:\root\fin\data\sStockCode.csv
    ############################################################
    def ReaddfStock(self):
        if not os.path.exists(self.URL):
            print(">>> Stock data - ", self.sStockCode, ": Not exist. Try to get stock data online!\n")
        else:
            dfStock = pd.read_csv(self.URL,                 # Read csv from local disk
                                  parse_dates=True,
                                  index_col=0,
                                  encoding='gb2312')
            return dfStock

    ##########################################################################################
    ### Desc:
    ###     Create MA: 'MA1/5/10/20/30/40/50/60/120/240'
    ##########################################################################################
    def CreateMA(self):
        self.dfStock['MA1'] = self.dfStock.Close.rolling(window=1).mean()
        self.dfStock['MA5'] = self.dfStock.Close.rolling(window=5).mean()
        self.dfStock['MA10'] = self.dfStock.Close.rolling(window=10).mean()
        self.dfStock['MA20'] = self.dfStock.Close.rolling(window=20).mean()
        self.dfStock['MA30'] = self.dfStock.Close.rolling(window=30).mean()

        self.dfStock['MA40'] = self.dfStock.Close.rolling(window=40).mean()
        self.dfStock['MA50'] = self.dfStock.Close.rolling(window=50).mean()
        self.dfStock['MA60'] = self.dfStock.Close.rolling(window=60).mean()
        self.dfStock['MA120'] = self.dfStock.Close.rolling(window=120).mean()
        self.dfStock['MA240'] = self.dfStock.Close.rolling(window=240).mean()

    ##########################################################################################
    ### Desc:
    ###     获取股票价格的黄金分割值（dThreFavor，dThreBest）
    ###     方法是过去“PERIOD”年排序，0.618值对应“dThreFavor”，0.618*0.5值对应“dThreBest”；
    ###     每年1月1日更新。
    ### Param:
    ###     PERIOD:         统计周期（中周期：8 - 10年；短周期3 - 5年）；
    ##########################################################################################
    def CreateThre(self, PERIOD = 8):
        dThreFavor = {}                                     # dict, key：年int； value：0.618 * 'Close'
        dThreBest = {}

        ##############################
        # Calc Threshold 0.618 and 0.309
        DATE = datetime.date.today()
        for i in np.arange(2010, DATE.year + 1):
            if(self.dfStock.index[0].year >= i):             # 尚未成立
                pass
            else:                                           # 已经成立
                Datei = datetime.datetime.strptime(str(i) + '-01-01', "%Y-%m-%d")
                DateiOld = Datei + relativedelta(years=-PERIOD)
                df = self.dfStock[self.dfStock.index >= DateiOld]
                df = df[df.index <= Datei]                                   # 截取10年
                serCloseSort = df['Close'].sort_values(ascending=True)      # 收盘排序

                dThreFavor[i] = serCloseSort[round(0.618 * len(serCloseSort.index))]
                dThreBest[i] = serCloseSort[round(0.309 * len(serCloseSort.index))]

        ##############################
        # Add column 'Thre0.618', 'Thre0.309'
        for idx in self.dfStock.index:
            if(idx.year in dThreFavor.keys()):
                self.dfStock.loc[idx, 'Thre0.618'] = dThreFavor[idx.year]
            if (idx.year in dThreBest.keys()):
                self.dfStock.loc[idx, 'Thre0.309'] = dThreBest[idx.year]

    ##########################################################################################
    ### Desc:
    ###     从“sDate”开始，每隔“DAY”，投入“MSHARE”金额；
    ###     返回总份额“wSumQuota”（基数：100），总成本“wSumCost”，总利润率wSumProfitRatio（%）
    ### Param:
    ###     sDate:          起始时间;
    ###     DAY:            定投日期;
    ###     MSHARE:         定投份额;
    ##########################################################################################
    def FixFund(self, sDate = "2010-01-01", DAY = 20, MSHARE = 10000 * 100):
        Date = datetime.datetime.strptime(sDate, "%Y-%m-%d")            # 起始日期
        df = self.dfStock[self.dfStock.index >= Date]
        dfOut = df.iloc[np.arange(0, len(df.index), DAY)]
        dfOut['Quota'] = round(MSHARE / dfOut['Close'] / 100) * 100     # 添加列 - 购买份额(基数：100)

        wSumCost = (dfOut['Quota'] * dfOut['Close']).sum()              # 成本
        wSumQuota = dfOut['Quota'].sum()                                # 份额
        wSumProfitRatio = 100 * (wSumQuota * dfOut.iloc[-1].Close - wSumCost) / wSumCost    # 利润率
        print("Start date: %s" %sDate, "\t\tQuota: %d;" %wSumQuota, "\t\tCost: %d;" %wSumCost, "\t\tProfit ration: %.2f%%;" %wSumProfitRatio)
        return wSumQuota, wSumCost, wSumProfitRatio

    def FixFundUpdate(self, sDate = "2010-01-01", DAY = 20, MSHARE = 10000 * 100):
        Date = datetime.datetime.strptime(sDate, "%Y-%m-%d")            # 起始日期
        dfOut = self.dfStock[self.dfStock.index >= Date]
        dfOut = dfOut.iloc[np.arange(0, len(dfOut.index), DAY)]         # 定投日期构成df

        dThreFavor, dThreBest = self.GetThre618()
        dfOut['Quota'] = 0
        dfOut['Thre'] = 0
        for idx in dfOut.index:
            if(dfOut.loc[idx, 'Close'] < dThreBest[idx.year]):          # 定投额翻倍
                dfOut.loc[idx, 'Quota'] = 2 * round(MSHARE / dfOut.loc[idx, 'Close'] / 100) * 100     # 添加列 - 购买份额(基数：100)
                dfOut.loc[idx, 'Thre'] = dThreBest[idx.year]
            elif(dfOut.loc[idx, 'Close'] < dThreFavor[idx.year]):       # 定投
                dfOut.loc[idx, 'Quota'] = round(MSHARE / dfOut.loc[idx, 'Close'] / 100) * 100     # 添加列 - 购买份额(基数：100)
                dfOut.loc[idx, 'Thre'] = dThreFavor[idx.year]
            else:                                                       # 不定投
                dfOut.loc[idx, 'Quota'] = 0
                dfOut.loc[idx, 'Thre'] = dThreFavor[idx.year]
        wSumCost = (dfOut['Quota'] * dfOut['Close']).sum()              # 成本
        wSumQuota = dfOut['Quota'].sum()                                # 份额
        wSumProfitRatio = 100 * (wSumQuota * dfOut.iloc[-1].Close - wSumCost) / wSumCost    # 利润率
        print("Start date: %s" %sDate, "\t\tQuota: %d;" %wSumQuota, "\t\tCost: %d;" %wSumCost, "\t\tProfit ration: %.2f%%;" %wSumProfitRatio)
        return wSumQuota, wSumCost, wSumProfitRatio

    ##########################################################################################
    ### Desc:
    ###     获取股票价格的黄金分割值（dThreFavor，dThreBest）
    ###     方法是过去“PERIOD”年排序，0.618值对应“dThreFavor”，0.618*0.5值对应“dThreBest”；
    ###     每年1月1日更新。
    ### Param:
    ###     PERIOD:         统计周期（中周期：8 - 10年；短周期3 - 5年）；
    ##########################################################################################
    def GetThre618(self, PERIOD = 8):
        dThreFavor = {}
        dThreBest = {}
        DATE = datetime.date.today()
        for i in np.arange(2010, DATE.year + 1):
            Date = datetime.datetime.strptime(str(i) + '-01-01', "%Y-%m-%d")
            DateOld = Date + relativedelta(years=-PERIOD)
            df = self.dfStock[self.dfStock.index >= DateOld]
            df = df[df.index <= Date]                                   # 截取10年
            ser = df['Close'].sort_values(ascending=True)               # 收盘排序
            dThreFavor[i] = ser[round(0.618 * len(df.index))]
            dThreBest[i] = ser[round(0.309 * len(df.index))]

        #print(dThreFavor)
        #print(dThreBest)
        return dThreFavor, dThreBest