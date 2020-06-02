#!/usr/bin/env python 
# -*- coding:utf-8 -*-

import csv,os
import datetime
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
from dateutil.relativedelta import relativedelta
import wx
import wx.adv
import warnings
#from tkinter import messagebox
import tkinter.messagebox
#warnings.filterwarnings('ignore')
import tushare as ts
df = pd.DataFrame([[1,10,20,"001001"],
                    [8,11,21,"002002"],
                    [9,12,22,"003003"],
                    [15,13,23,"004004"],
                    [20,14,24,"005005"]],
              index=[20200101,20200102,20200103,20200104,20200105,],
              columns=['Ma20', 'Close','Low','High'])
sUrl = r"D:\gitHub\root\fin\InHma\data\510500 - 中证500ETF.csv"
dfStock = pd.read_csv(sUrl, parse_dates=True, index_col=0)
print(dfStock)

'''
### Init tushare ###
pro = ts.pro_api('85682a790fc2446f2953918e90c9022c9f025f10cac75191551aad9c')
### Get stock list on the exchange market ###
### ts_code;  name = 股票名称;  area = 所在地域;  industry = 所属行业;  market = 市场类型(主板/中小板/创业板/科创板); list_date = 上市日期 ###
dfStockList = pro.query('stock_basic', exchange='', list_status='L', fields='ts_code, name, area, industry, market, list_date')
print(dfStockList)
#for i in np.arange(0, len(dfStockList.index)):
for i in np.arange(0, 1):
    sUrl = os.path.join(os.path.abspath('./data'), dfStockList.loc[i, "ts_code"] + '.csv')
    if not os.path.exists(sUrl):
        dfStock = pro.query('daily', ts_code=dfStockList.loc[i, "ts_code"], start_date='20100101', end_date=datetime.date.today().strftime('%Y%m%d'))
        dfStock.to_csv(sUrl, index=False, columns=["trade_date", "open", "high", "low", "close", "amount"])     # index=False: 不保留行索引;
    else:
        dfStock = pd.read_csv(sUrl, index_col="trade_date")
        sToday = datetime.date.today().strftime('%Y%m%d')
        if(sToday > str(dfStock.index[-1])):
            dfStock = pro.query('daily', ts_code=dfStockList.loc[i, "ts_code"], start_date='20100101', end_date=datetime.date.today().strftime('%Y%m%d'))
        #print(dfStock)
        #dfStock.to_csv(sUrl, index=True)     # index=True: 保留行索引;
        #print("\n\n")
        #print(dfStock.loc[dfStock.index[0],"trade_date"])
'''


