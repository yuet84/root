#!/usr/bin/env python 
# -*- coding:utf-8 -*-
import wx
import wx.adv
import numpy as np
import pandas as pd
import pandas_datareader.data as web
import matplotlib
import matplotlib.pyplot as plt
from matplotlib.figure import Figure
import matplotlib.dates as mdates
import mplfinance as mpf #替换 import mpl_finance as mpf
from matplotlib.backends.backend_wxagg import FigureCanvasWxAgg as FigureCanvas
import matplotlib.gridspec as gridspec#分割子图
import datetime
import talib
import csv,os
import codecs
from numpy import arange, sin, pi


'''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''
Class Gui:
    OnInit():           wxPython Init (Top fram; Panel cmd; Panel plot);
    LayoutPanelCmd():   Layout panel cmd (Date picker: Start - End; Entry: Period of Sma | Hma short | Hma long; Button: Plot);
    LayoutPanelPlot():  Layout panel plot (Canvas);
    PlotHMA():          Button function entry (Plot HMA);
------------------------------------------------------------------------------------------
    Standard layout module:
    LayoutDate(self, parent, sLabel, Date):         Layout date picker (sLabel : Pick date) (Return sizer & wxDate);
    LayoutEntry(self, parent, sLabel, sEntry):      Layout entry (sLabel : sEntry) (Return sizer & wxEntry);
    LayoutButton(self, parent, sLabel, FuncEntry):  Layout button (sLabel : FuncEntry) (Return wxBtn);
'''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''
plt.rcParams['font.sans-serif']=['SimHei']      # 用来正常显示中文标签
plt.rcParams['axes.unicode_minus']=False        # 用来正常显示负号
class ClGui(wx.App):
    def __init__(self, sStockCode=None, sStockName=None, dfStock=None):
        ### Passing params ###
        self.sStockCode = sStockCode
        self.sStockName = sStockName
        self.dfStock = dfStock
        self.dfStock = dfStock

        ### Global params ###
        self.sDateStart = "2015-01-01"          # Plot start date

        ### Call function ###
        wx.App.__init__(self)

    ############################################################
    ### wxPython Init (Top fram; Panel cmd; Panel plot)
    ############################################################
    def OnInit(self):
        ### Create /wxFrame ###
        wxFrame = wx.Frame(None, title=self.sStockCode + " - " + self.sStockName, style=wx.DEFAULT_FRAME_STYLE|wx.MAXIMIZE)
        wxSizer = wx.BoxSizer(wx.HORIZONTAL)
        ### Create /wxFrame/wxPanelCmd ###
        wxPanelCmd = wx.Panel(parent=wxFrame,id=-1)
        wxSizer.Add(wxPanelCmd, proportion=1, border=2, flag=wx.EXPAND|wx.ALL)
        self.LayoutPanelCmd(wxPanelCmd)
        ### Create /wxFrame/wxPanelPlot ###
        self.wxPanelPlot = wx.Panel(parent=wxFrame,id=-1)
        wxSizer.Add(self.wxPanelPlot, proportion=9, border=2, flag=wx.EXPAND|wx.ALL)
        self.LayoutPanelPlot(self.wxPanelPlot)

        ### Show wxFrame ###
        wxFrame.SetSizer(wxSizer)
        wxFrame.Show(True)
        self.SetTopWindow(wxFrame)
        return True

    ############################################################
    ### Layout panel cmd (Date picker: Start - End; Entry: Period of Sma | Hma short | Hma long; Button: Plot)
    ############################################################
    def LayoutPanelCmd(self, parent):
        wxSizer = wx.BoxSizer(orient=wx.VERTICAL)

        ### Create ./Date picker: Start ###
        sizer, self.wxDateStart = self.LayoutDate(parent, "Start:", datetime.datetime.strptime(self.sDateStart, '%Y-%m-%d'))
        wxSizer.Add(sizer, proportion=0, border=50, flag=wx.ALIGN_CENTRE|wx.TOP)
        ### Create ./Date picker: End ###
        sizer, self.wxDateEnd = self.LayoutDate(parent, "End:", datetime.datetime.now())
        wxSizer.Add(sizer, proportion=0, border=10, flag=wx.ALIGN_CENTRE|wx.TOP)
        ### Create ./Entry: SMA ###
        sizer, self.wxEntrySma = self.LayoutEntry(parent, "SMA:", "1")
        wxSizer.Add(sizer, proportion=0, border=30, flag=wx.ALIGN_CENTRE|wx.TOP)
        ### Create ./Entry: HMA short ###
        sizer, self.wxEntryHmaShort = self.LayoutEntry(parent, "HMA Short:", "24")
        wxSizer.Add(sizer, proportion=0, border=10, flag=wx.ALIGN_CENTRE|wx.TOP)
        ### Create ./Entry: HMA long ###
        sizer, self.wxEntryHmaLong = self.LayoutEntry(parent, "HMA Long:", "52")
        wxSizer.Add(sizer, proportion=0, border=10, flag=wx.ALIGN_CENTRE|wx.TOP)
        ### Create ./Button: Plot ###
        wxBtn = self.LayoutButton(parent, "绘  图", self.PlotHMA)
        wxSizer.Add(wxBtn, proportion=0, border=30, flag=wx.ALIGN_CENTRE|wx.TOP)

        ### Execute sizer ###
        parent.SetSizer(wxSizer)

    ############################################################
    ### Layout panel plot (Canvas)
    ############################################################
    def LayoutPanelPlot(self,parent):
        self.wxSizer = wx.BoxSizer(orient=wx.VERTICAL)          # Create sizer

        self.wxCanvasFig = Figure()                             # Create Figure
        self.wxCanvas = FigureCanvas(parent, -1, self.wxCanvasFig)
        self.wxSizer.Add(window=self.wxCanvas, proportion=1, border=2, flag=wx.EXPAND|wx.ALL)

        parent.SetSizer(self.wxSizer)

    ############################################################
    ### Button function entry (Plot HMA)
    ############################################################
    def PlotHMA(self, event):
        ### Validate value  ###
        DateStart = datetime.datetime.strptime(self.wxDateStart.GetValue().Format('%Y-%m-%d'), '%Y-%m-%d')
        DateEnd = datetime.datetime.strptime(self.wxDateEnd.GetValue().Format('%Y-%m-%d'), '%Y-%m-%d')
        if self.wxEntrySma.GetValue().isdigit() and self.wxEntryHmaShort.GetValue().isdigit() and self.wxEntryHmaLong.GetValue().isdigit():
            if(self.wxEntrySma.GetValue() == "0"):
                self.wxEntrySma.SetValue("1")
        else:
            print(">>> ERROR: Entry SMA | HMA short | HMA long is not number!\n")
            return

        ### Clear canvas  ###
        self.wxSizer.Hide(self.wxCanvas)
        self.wxCanvasFig.clear()
        wxPlot = self.wxCanvasFig.add_subplot(111)          # Create subplot

        ### Plot SMA ###
        serSma = self.CalcSma(self.dfStock["Close"], int(self.wxEntrySma.GetValue()), DateStart, DateEnd)
        xd = np.arange(0, len(serSma.index))
        wxPlot.plot(xd, serSma, color='grey', label="SMA - " + self.wxEntrySma.GetValue(), linewidth=0.2)

        ### Set x-axis ###
        wxPlot.set_xlim(0,len(serSma.index))
        wxPlot.set_xticks(range(0, len(serSma.index), round(len(serSma.index) / 10)))
        wxPlot.set_xticklabels([serSma.index[i].strftime('%Y-%m-%d') for i in wxPlot.get_xticks()], rotation=30)
        wxPlot.grid(b=True, axis='x', color='grey', linestyle='-', linewidth=0.2)

        ### Plot HMA short ###
        serHmaShort = self.CalcHma(self.dfStock["Close"], int(self.wxEntryHmaShort.GetValue()), DateStart, DateEnd)
        if(serHmaShort.index[-1] == serSma.index[-1]):
            xd = np.arange(len(serSma.index) - len(serHmaShort.index), len(serSma.index))
            wxPlot.plot(xd, serHmaShort, color='red', label="HMA - " + self.wxEntryHmaShort.GetValue(), linewidth=1)

        ### Plot HMA long ###
        serHmaLong = self.CalcHma(self.dfStock["Close"], int(self.wxEntryHmaLong.GetValue()), DateStart, DateEnd)
        if(serHmaLong.index[-1] == serSma.index[-1]):
            xd = np.arange(len(serSma.index) - len(serHmaLong.index), len(serSma.index))
            wxPlot.plot(xd, serHmaLong, color='green', label="HMA - " + self.wxEntryHmaLong.GetValue(), linewidth=0.5)

        ### Show plot ###
        wxPlot.legend(loc='best', shadow=True, fontsize='8')
        self.wxCanvas.draw()
        self.wxSizer.Show(self.wxCanvas)


    ############################################################
    ### Standard layout date picker (sLabel : Pick date) (Return sizer & wxDate)
    ############################################################
    def LayoutDate(self, parent, sLabel, Date):
        wxSizer = wx.BoxSizer(orient=wx.HORIZONTAL)
        ### Layout label ###
        wxText = wx.StaticText(parent, -1, label=sLabel, size=(50, 20), style=wx.ALIGN_CENTRE|wx.TE_LEFT)
        wxText.SetFont(wx.Font(pointSize=12, family=wx.ROMAN, style=wx.NORMAL, weight=wx.NORMAL))
        wxSizer.Add(wxText, proportion=0, border=5, flag=wx.LEFT)
        ### Layout date picker ###
        wxDate = wx.adv.DatePickerCtrl(parent, id=-1, size=(100, 20), style=wx.adv.DP_DROPDOWN | wx.adv.DP_SHOWCENTURY)
        wxDate.SetValue(Date)
        wxDate.SetFont(wx.Font(pointSize=10, family=wx.ROMAN, style=wx.NORMAL, weight=wx.NORMAL))
        wxSizer.Add(wxDate, proportion=0, border=5, flag=wx.RIGHT)
        return wxSizer, wxDate

    ############################################################
    ### Standard layout entry (sLabel : sEntry) (Return sizer & wxEntry)
    ############################################################
    def LayoutEntry(self, parent, sLabel, sEntry):
        wxSizer = wx.BoxSizer(orient=wx.HORIZONTAL)
        ### Layout label ###
        wxText = wx.StaticText(parent, -1, label=sLabel, size=(100,20), style=wx.TE_CENTER)
        wxText.SetFont(wx.Font(pointSize=12, family=wx.ROMAN, style=wx.NORMAL, weight=wx.NORMAL))
        wxSizer.Add(wxText, proportion=0, border=5, flag=wx.ALIGN_CENTRE|wx.LEFT)
        ### Layout entry ###
        wxEntry = wx.TextCtrl(parent, -1, value=sEntry, size=(50,20), style=wx.TE_CENTER)
        wxEntry.SetFont(wx.Font(pointSize=10, family=wx.ROMAN, style=wx.NORMAL, weight=wx.NORMAL))
        wxSizer.Add(wxEntry, proportion=0, border=5, flag=wx.ALIGN_CENTRE|wx.RIGHT)
        return wxSizer, wxEntry

    ############################################################
    ### Standard layout button (sLabel : FuncEntry) (Return wxBtn)
    ############################################################
    def LayoutButton(self, parent, sLabel, FuncEntry):
        ### Layout button ###
        wxBtn = wx.Button(parent, -1, label=sLabel, size=(80,30))
        wxBtn.SetFont(wx.Font(pointSize=12, family=wx.ROMAN, style=wx.NORMAL, weight=wx.BOLD))
        wxBtn.Bind(event=wx.EVT_BUTTON, handler=FuncEntry)
        return wxBtn

    ############################################################
    ### Standard calc SMA (ser: Target data; T: SMA period; DateFrom:DateEnd: Target date) (Return serSma)
    ############################################################
    def CalcSma(self, ser, T, DateFrom, DateEnd):
        ### Create SMA ###
        serSma = ser.rolling(window=T).mean()
        ### Cut off the target date section ###
        serSma = serSma[serSma.index >= DateFrom]
        serSma = serSma[serSma.index <= DateEnd]
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
