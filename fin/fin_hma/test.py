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
dfStock = pd.DataFrame([[1,10.1,10.1,10.1],
                        [8,10.2,10.2,10.2],
                        [9,10.3,10.3,10.3],
                        [15,12.3,12.3,12.3],
                        [20,12.4,12.4,12.4]],
                  index=['2020-1-1','2020-1-2','2020-1-3','2020-1-4','2020-1-5',],
                  columns=['Ma20', 'Close','Low','High'])

ser = pd.Series([10, 20, 30, 40], index=['2010-01-01', '2010-01-02', '2010-01-03', '2010-01-04'])
ser2 = pd.Series([100, 200], index=['2010-01-05', '2010-01-06'])


tkinter.messagebox.showinfo(title=None, message=None)

