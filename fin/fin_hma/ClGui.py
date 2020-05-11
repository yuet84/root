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

##########################################################################################
### Class function:
###     OnInit():           Init and Display GUI顶层frame: /wxFrame, /wxFrame/wxPanelCmd, /wxFrame/self.wxPanelPlot;
###     LayoutPanelCmd():   Layout panel cmd: ./Text: 'Stock Code';  ./Combo: SMA short, SMA long, HMA short, HMA long;  ./Btn: '绘图';
###     WxPlotHMA():        Button bind function: Plot MA;
###     LayoutPanelPlot():  Layout panel plot: ./Canvas/CanvasFig;
##########################################################################################
plt.rcParams['font.sans-serif']=['SimHei']      # 用来正常显示中文标签
plt.rcParams['axes.unicode_minus']=False        # 用来正常显示负号
class ClGui(wx.App):
    def __init__(self, sStockCode=None, sStockName=None, dfStock=None):
        ### Passing params ###
        self.sStockCode = sStockCode
        self.sStockName = sStockName
        self.dfStock = dfStock

        ### Global params ###
        self.DateStart = datetime.datetime.strptime("2015-01-01", '%Y-%m-%d')           # Plot start date
        self.DateEnd = datetime.datetime.now()                                          # Plot end date
        self.DICT = {'HMA-1': 1, 'MA-5': 5, 'MA-10': 10, 'MA-20': 20, 'MA-30': 30, 'MA-40': 40, 'MA-50': 50,
                     'MA-60': 60,
                     'MA-80': 80, 'MA-100': 100, 'MA-120': 120, 'MA-150': 150, 'MA-200': 200, 'MA-240': 240}

        ### Call function ###
        wx.App.__init__(self)

    ############################################################
    ### Init and Display GUI顶层frame: /wxFrame, /wxFrame/wxPanelCmd, /wxFrame/self.wxPanelPlot
    ############################################################
    def OnInit(self):
        ### Create /wxFrame ###
        wxFrame = wx.Frame(None,
                           title=self.sStockCode + " - " + self.sStockName,
                           style=wx.DEFAULT_FRAME_STYLE|wx.MAXIMIZE)
        wxSizer = wx.BoxSizer(wx.HORIZONTAL)

        ### Create /wxFrame/wxPanelCmd ###
        wxPanelCmd = wx.Panel(parent=wxFrame,id=-1)
        wxSizer.Add(wxPanelCmd, proportion=1, border=2, flag=wx.EXPAND|wx.ALL)
        self.LayoutPanelCmd(wxPanelCmd)

        ### Create /wxFrame/wxPanelPlot ###
        self.wxPanelPlot = wx.Panel(parent=wxFrame,id=-1)
        wxSizer.Add(self.wxPanelPlot, proportion=9, border=2, flag=wx.EXPAND|wx.ALL)
        self.LayoutPanelPlot(self.wxPanelPlot)

        wxFrame.SetSizer(wxSizer)
        wxFrame.Show(True)
        self.SetTopWindow(wxFrame)
        return True

    ############################################################
    ### Layout panel cmd: ./Text: 'Stock Code';  ./Combo: SMA short, SMA long, HMA short, HMA long;  ./Btn: '绘图';
    ############################################################
    def LayoutPanelCmd(self, parent):
        wxSizer = wx.BoxSizer(orient=wx.VERTICAL)

        ### Create ./Date: 起始时间 ###
        wxSizerTmp = wx.BoxSizer(orient=wx.HORIZONTAL)

        wxText = wx.StaticText(parent, -1, label="From:  ", style=wx.ALIGN_CENTRE|wx.TE_LEFT)
        wxText.SetFont(wx.Font(pointSize=12, family=wx.ROMAN, style=wx.NORMAL, weight=wx.NORMAL))
        wxSizerTmp.Add(wxText, proportion=0, border=5, flag=wx.ALIGN_CENTRE|wx.LEFT)

        wxDate = wx.adv.DatePickerCtrl(parent, id=-1, style=wx.adv.DP_DROPDOWN | wx.adv.DP_SHOWCENTURY)
        wxDate.SetValue(self.DateStart)
        wxDate.Bind(wx.adv.EVT_DATE_CHANGED, self.WxGetDateStart)
        wxSizerTmp.Add(wxDate, proportion=0, border=5, flag=wx.ALIGN_CENTRE|wx.RIGHT)

        wxSizer.Add(wxSizerTmp, proportion=0, border=50, flag=wx.ALIGN_CENTRE|wx.TOP)

        ### Create ./Date: 结束时间 ###
        wxSizerTmp = wx.BoxSizer(orient=wx.HORIZONTAL)

        wxText = wx.StaticText(parent, -1, label="To:      ", style=wx.ALIGN_CENTRE|wx.TE_LEFT)
        wxText.SetFont(wx.Font(pointSize=12, family=wx.ROMAN, style=wx.NORMAL, weight=wx.NORMAL))
        wxSizerTmp.Add(wxText, proportion=0, border=5, flag=wx.ALIGN_CENTRE|wx.LEFT)

        wxDate = wx.adv.DatePickerCtrl(parent, id=-1, style=wx.adv.DP_DROPDOWN | wx.adv.DP_SHOWCENTURY)
        wxDate.SetValue(self.DateEnd)
        wxDate.Bind(wx.adv.EVT_DATE_CHANGED, self.WxGetDateEnd)
        wxSizerTmp.Add(wxDate, proportion=0, border=5, flag=wx.ALIGN_CENTRE|wx.RIGHT)

        wxSizer.Add(wxSizerTmp, proportion=0, border=10, flag=wx.ALIGN_CENTRE|wx.TOP)

        ### Create ./SMA ###
        wxSizerTmp = wx.BoxSizer(orient=wx.HORIZONTAL)

        wxText = wx.StaticText(parent, -1, label="SMA short:  ", style=wx.ALIGN_CENTRE|wx.TE_LEFT)
        wxText.SetFont(wx.Font(pointSize=12, family=wx.ROMAN, style=wx.NORMAL, weight=wx.NORMAL))
        wxSizerTmp.Add(wxText, proportion=0, border=5, flag=wx.ALIGN_CENTRE|wx.LEFT)

        self.wxSMAPeriod = wx.TextCtrl(parent, -1, value="1", size=(60,20), style=wx.TE_CENTER)
        wxSizerTmp.Add(self.wxSMAPeriod, proportion=0, border=5, flag=wx.ALIGN_CENTRE|wx.RIGHT)

        wxSizer.Add(wxSizerTmp, proportion=0, border=30, flag=wx.ALIGN_CENTRE|wx.TOP)

        ### Create ./HMA short ###
        wxSizerTmp = wx.BoxSizer(orient=wx.HORIZONTAL)

        wxText = wx.StaticText(parent, -1, label="HMA short:  ", style=wx.ALIGN_CENTRE|wx.TE_LEFT)
        wxText.SetFont(wx.Font(pointSize=12, family=wx.ROMAN, style=wx.NORMAL, weight=wx.NORMAL))
        wxSizerTmp.Add(wxText, proportion=0, border=5, flag=wx.ALIGN_CENTRE|wx.LEFT)

        self.wxSHMAPeriod = wx.TextCtrl(parent, -1, value="24", size=(60,20), style=wx.TE_CENTER)
        wxSizerTmp.Add(self.wxSHMAPeriod, proportion=0, border=5, flag=wx.ALIGN_CENTRE|wx.RIGHT)

        wxSizer.Add(wxSizerTmp, proportion=0, border=20, flag=wx.ALIGN_CENTRE|wx.TOP)

        ### Create ./HMA long ###
        wxSizerTmp = wx.BoxSizer(orient=wx.HORIZONTAL)

        wxText = wx.StaticText(parent, -1, label="HMA long:  ", style=wx.ALIGN_CENTRE|wx.TE_LEFT)
        wxText.SetFont(wx.Font(pointSize=12, family=wx.ROMAN, style=wx.NORMAL, weight=wx.NORMAL))
        wxSizerTmp.Add(wxText, proportion=0, border=5, flag=wx.ALIGN_CENTRE|wx.LEFT)

        self.wxLHMAPeriod = wx.TextCtrl(parent, -1, value="52", size=(60,20), style=wx.TE_CENTER)
        wxSizerTmp.Add(self.wxLHMAPeriod, proportion=0, border=5, flag=wx.ALIGN_CENTRE|wx.RIGHT)


        wxSizer.Add(wxSizerTmp, proportion=0, border=10, flag=wx.ALIGN_CENTRE|wx.TOP)

        ##############################
        # Create ./Btn: '绘图'
        wxBtnPlot = wx.Button(parent, -1, label="绘  图")
        wxBtnPlot.SetFont(wx.Font(pointSize=12,family=wx.ROMAN,style=wx.NORMAL,weight=wx.NORMAL))
        wxBtnPlot.Bind(event=wx.EVT_BUTTON,
                       handler=self.WxPlotHMA)
        wxSizer.Add(wxBtnPlot, proportion=0, border=30, flag=wx.ALIGN_CENTRE|wx.TOP)

        parent.SetSizer(wxSizer)

    def WxGetDateStart(self, event):
        self.DateStart = datetime.datetime.strptime(event.GetEventObject().GetValue().Format('%Y-%m-%d'), '%Y-%m-%d')

    def WxGetDateEnd(self, event):
        self.DateEnd = datetime.datetime.strptime(event.GetEventObject().GetValue().Format('%Y-%m-%d'), '%Y-%m-%d')

    def WxGetSMAShort(self,event):
        self.sSMAShort = event.GetString()

    def WxGetSMALong(self,event):
        self.sSMALong = event.GetString()

    def WxGetHMAShort(self,event):
        self.sHMAShort = event.GetString()

    def WxGetHMALong(self,event):
        self.sHMALong = event.GetString()

    ############################################################
    ### Button bind function: Plot MA
    ############################################################
    def WxPlotHMA(self, event):
        self.wxSizer.Hide(self.wxCanvas)
        self.wxCanvasFig.clear()
        wxPlot = self.wxCanvasFig.add_subplot(111)          # Create subplot

        ########################
        # Plot Close

        # Create SMA
        T = 1
        serSMA = self.dfStock['Close'].rolling(window=T).mean()

        # Cut off the target date section
        serSMA = serSMA[serSMA.index >= self.DateStart]
        serSMA = serSMA[serSMA.index <= self.DateEnd]

        # Create x-axis
        xd = np.arange(0, len(serSMA.index))
        wxPlot.set_xlim(0,len(serSMA.index))
        wxPlot.set_xticks(range(0, len(serSMA.index), round(len(serSMA.index) / 10)))
        wxPlot.set_xticklabels([serSMA.index[i].strftime('%Y-%m-%d') for i in wxPlot.get_xticks()], rotation=30)
        wxPlot.grid(b=True, axis='x', color='grey', linestyle='-', linewidth=0.2)

        # Plot
        wxPlot.plot(xd, serSMA, color='grey', label="SMA - 1", linewidth=0.5)

        ########################
        # Plot HMA short

        # Create HMA
        T = self.DICT[self.sHMAShort]
        serHShort = self.dfStock['Close'].ewm(alpha=2 / T, adjust=False, ignore_na=True).mean() * 2
        serHLong = self.dfStock['Close'].ewm(alpha=1 / T, adjust=False, ignore_na=True).mean()
        serHDelta = serHShort - serHLong
        serHMA = serHDelta.ewm(alpha=1 / (T ** 0.5), adjust=False, ignore_na=True).mean()

        # Cut off the target date section
        serHMA = serHMA[serHMA.index >= self.DateStart]
        serHMA = serHMA[serHMA.index <= self.DateEnd]

        # Create x-axis
        xd = np.arange(len(serSMA.index) - len(serHMA.index), len(serSMA.index))

        # Plot
        wxPlot.plot(xd, serHMA, color='red', label=self.sHMAShort, linewidth=0.5)


        ########################
        # Plot HMA long

        # Create HMA
        T = self.DICT[self.sHMALong]
        serHShort = self.dfStock['Close'].ewm(alpha=2 / T, adjust=False, ignore_na=True).mean() * 2
        serHLong = self.dfStock['Close'].ewm(alpha=1 / T, adjust=False, ignore_na=True).mean()
        serHDelta = serHShort - serHLong
        serHMA = serHDelta.ewm(alpha=1 / (T ** 0.5), adjust=False, ignore_na=True).mean()

        # Cut off the target date section
        serHMA = serHMA[serHMA.index >= self.DateStart]
        serHMA = serHMA[serHMA.index <= self.DateEnd]

        # Create x-axis
        xd = np.arange(len(serSMA.index) - len(serHMA.index), len(serSMA.index))

        # Plot
        wxPlot.plot(xd, serHMA, color='green', label=self.sSMALong, linewidth=0.5)

        wxPlot.legend(loc='best', shadow=True, fontsize='8')
        self.wxCanvas.draw()
        self.wxSizer.Show(self.wxCanvas)

    ############################################################
    ### Layout panel plot: ./Canvas/CanvasFig
    ############################################################
    def LayoutPanelPlot(self,parent):
        self.wxSizer = wx.BoxSizer(orient=wx.VERTICAL)          # Create sizer

        self.wxCanvasFig = Figure()                             # Create Figure
        self.wxCanvas = FigureCanvas(parent, -1, self.wxCanvasFig)
        self.wxSizer.Add(window=self.wxCanvas, proportion=1, border=2, flag=wx.EXPAND|wx.ALL)

        parent.SetSizer(self.wxSizer)


