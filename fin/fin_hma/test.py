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
#warnings.filterwarnings('ignore')
dfStock = pd.DataFrame([[1,10.1,10.1,10.1],
                        [8,10.2,10.2,10.2],
                        [9,10.3,10.3,10.3],
                        [15,12.3,12.3,12.3],
                        [20,12.4,12.4,12.4]],
                  index=['2020-1-1','2020-1-2','2020-1-3','2020-1-4','2020-1-5',],
                  columns=['Ma20', 'Close','Low','High'])
ser = dfStock['Close']
ser = ser[ser.index >= "2020-1-2"]
ser = ser[ser.index <= "2020-1-4"]
print(ser)