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
df = pd.DataFrame([[1,1,0,"001001"],
                    [8,1,0,"002002"],
                    [9,1,1,"003003"],
                    [15,0,1,"004004"],
                    [20,0,1,"005005"]],
              index=[20200101,20200102,20200103,20200104,20200105,],
              columns=['Close', 'Gold','Dead','High'])

print("Origin:\n", df)
for row in df.itertuples():
    #print("row: ", row)
    #print(type(row))
    row.Close=1
print(df)



