#!/usr/bin/env python 
# -*- coding:utf-8 -*-

import csv,os
import datetime
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
from dateutil.relativedelta import relativedelta
import warnings
#warnings.filterwarnings('ignore')
dfStock = pd.DataFrame([[1,10.1,10.1,10.1],
                        [8,10.2,10.2,10.2],
                        [9,10.3,10.3,10.3],
                        [15,12.3,12.3,12.3],
                        [20,12.4,12.4,12.4]],
                  index=['2020-1-1','2020-1-2','2020-1-3','2020-1-4','2020-1-5',],
                  columns=['Ma20', 'Close','Low','High'])
'''
d = {2010:1, 2011:2, 2012:3}
for i in np.arange(2000,2020):
    if(d.has_key(i)):
        print(i, d[i])
'''
d = {'name':{},'age':{},'sex':{}}
print('name' in d.keys())

