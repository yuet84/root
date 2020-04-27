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

plt.rcParams['font.sans-serif']=['SimHei']      # 用来正常显示中文标签
plt.rcParams['axes.unicode_minus']=False        # 用来正常显示负号


##########################################################################################
### Class function:
###     OnInit():           Init and Display GUI顶层frame: /wxFrame, /wxFrame/wxPanelCmd, /wxFrame/self.wxPanelPlot;
###     LayoutPanelCmd():   Layout panel cmd: ./Text: 'Stock Code';  ./Combo: SMA short, SMA long, HMA short, HMA long;  ./Btn: '绘图';
###     WxPlotHMA():        Button bind function: Plot MA;
###     LayoutPanelPlot():  Layout panel plot: ./Canvas/CanvasFig;
##########################################################################################
class ClGui(wx.App):
    def __init__(self,sStockCode=None,dfStock=None):
        self.sStockCode=sStockCode                      # Must init params here
        self.dfStock=dfStock
        self.DateStart = datetime.datetime.strptime("2015-01-01", '%Y-%m-%d')
        self.DateEnd = datetime.datetime.now()
        self.DICT={'MA-1':1,'MA-5':5,'MA-10':10, 'MA-20':20, 'MA-30':30, 'MA-40':40, 'MA-50':50, 'MA-60':60, 'MA-80':80, 'MA-100':100, 'MA-120':120, 'MA-150':150, 'MA-200':200, 'MA-240':240}
        wx.App.__init__(self)

    ############################################################
    ### Init and Display GUI顶层frame: /wxFrame, /wxFrame/wxPanelCmd, /wxFrame/self.wxPanelPlot
    ############################################################
    def OnInit(self):
        ##############################
        # Create /wxFrame
        wxFrame = wx.Frame(None,
                           title=self.sStockCode,
                           style=wx.DEFAULT_FRAME_STYLE|wx.MAXIMIZE)
        wxSizer = wx.BoxSizer(wx.HORIZONTAL)

        ##############################
        # Create /wxFrame/wxPanelCmd
        wxPanelCmd = wx.Panel(parent=wxFrame,id=-1)
        wxSizer.Add(wxPanelCmd, proportion=1, border=2, flag=wx.EXPAND|wx.ALL)
        self.LayoutPanelCmd(wxPanelCmd)

        ##############################
        # Create /wxFrame/wxPanelPlot
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

        ##############################
        # Create ./Text: Stock code
        wxText = wx.StaticText(parent, -1, label=self.sStockCode + " - ", style=wx.ALIGN_CENTRE|wx.TE_LEFT)
        wxText.SetFont(wx.Font(pointSize=16,family=wx.ROMAN,style=wx.NORMAL,weight=wx.BOLD))
        wxSizer.Add(wxText, proportion=0, border=20, flag=wx.ALIGN_CENTRE|wx.TOP)

        ##############################
        # Create ./Date: 起始时间
        wxSizerTmp = wx.BoxSizer(orient=wx.HORIZONTAL)

        wxText = wx.StaticText(parent, -1, label="From:  ", style=wx.ALIGN_CENTRE|wx.TE_LEFT)
        wxText.SetFont(wx.Font(pointSize=12, family=wx.ROMAN, style=wx.NORMAL, weight=wx.NORMAL))
        wxSizerTmp.Add(wxText, proportion=0, border=5, flag=wx.ALIGN_CENTRE|wx.LEFT)

        wxDate = wx.adv.DatePickerCtrl(parent, id=-1, style=wx.adv.DP_DROPDOWN | wx.adv.DP_SHOWCENTURY)
        wxDate.SetValue(self.DateStart)
        wxDate.Bind(wx.adv.EVT_DATE_CHANGED, self.WxGetDateStart)
        wxSizerTmp.Add(wxDate, proportion=0, border=5, flag=wx.ALIGN_CENTRE|wx.RIGHT)

        wxSizer.Add(wxSizerTmp, proportion=0, border=30, flag=wx.ALIGN_CENTRE|wx.TOP)

        ##############################
        # Create ./Date: 结束时间
        wxSizerTmp = wx.BoxSizer(orient=wx.HORIZONTAL)

        wxText = wx.StaticText(parent, -1, label="To:      ", style=wx.ALIGN_CENTRE|wx.TE_LEFT)
        wxText.SetFont(wx.Font(pointSize=12, family=wx.ROMAN, style=wx.NORMAL, weight=wx.NORMAL))
        wxSizerTmp.Add(wxText, proportion=0, border=5, flag=wx.ALIGN_CENTRE|wx.LEFT)

        wxDate = wx.adv.DatePickerCtrl(parent, id=-1, style=wx.adv.DP_DROPDOWN | wx.adv.DP_SHOWCENTURY)
        wxDate.SetValue(self.DateEnd)
        wxDate.Bind(wx.adv.EVT_DATE_CHANGED, self.WxGetDateEnd)
        wxSizerTmp.Add(wxDate, proportion=0, border=5, flag=wx.ALIGN_CENTRE|wx.RIGHT)

        wxSizer.Add(wxSizerTmp, proportion=0, border=10, flag=wx.ALIGN_CENTRE|wx.TOP)

        ##############################
        # Create SMA short
        wxSizerTmp = wx.BoxSizer(orient=wx.HORIZONTAL)

        wxText = wx.StaticText(parent, -1, label="SMA short:  ", style=wx.ALIGN_CENTRE|wx.TE_LEFT)
        wxText.SetFont(wx.Font(pointSize=12, family=wx.ROMAN, style=wx.NORMAL, weight=wx.NORMAL))
        wxSizerTmp.Add(wxText, proportion=0, border=5, flag=wx.ALIGN_CENTRE|wx.LEFT)

        t = 'MA-1'
        self.sSMAShort = t
        wxCombo = wx.ComboBox(parent, -1, value=t, choices=list(self.DICT), style=wx.CB_DROPDOWN)
        wxCombo.Bind(wx.EVT_COMBOBOX,self.WxGetSMAShort)
        wxSizerTmp.Add(wxCombo, proportion=0, border=5, flag=wx.ALIGN_CENTRE|wx.RIGHT)

        wxSizer.Add(wxSizerTmp, proportion=0, border=30, flag=wx.ALIGN_CENTRE|wx.TOP)

        ##############################
        # Create SMA long
        wxSizerTmp = wx.BoxSizer(orient=wx.HORIZONTAL)

        wxText = wx.StaticText(parent, -1, label="SMA long:  ", style=wx.ALIGN_CENTRE|wx.TE_LEFT)
        wxText.SetFont(wx.Font(pointSize=12, family=wx.ROMAN, style=wx.NORMAL, weight=wx.NORMAL))
        wxSizerTmp.Add(wxText, proportion=0, border=5, flag=wx.ALIGN_CENTRE|wx.LEFT)

        t = 'MA-20'
        self.sSMALong = t
        wxCombo = wx.ComboBox(parent, -1, value=t, choices=list(self.DICT), style=wx.CB_DROPDOWN)
        wxCombo.Bind(wx.EVT_COMBOBOX,self.WxGetSMALong)
        wxSizerTmp.Add(wxCombo, proportion=0, border=5, flag=wx.ALIGN_CENTRE|wx.RIGHT)

        wxSizer.Add(wxSizerTmp, proportion=0, border=10, flag=wx.ALIGN_CENTRE|wx.TOP)

        ##############################
        # Create HMA short
        wxSizerTmp = wx.BoxSizer(orient=wx.HORIZONTAL)

        wxText = wx.StaticText(parent, -1, label="hMA short:  ", style=wx.ALIGN_CENTRE|wx.TE_LEFT)
        wxText.SetFont(wx.Font(pointSize=12, family=wx.ROMAN, style=wx.NORMAL, weight=wx.NORMAL))
        wxSizerTmp.Add(wxText, proportion=0, border=5, flag=wx.ALIGN_CENTRE|wx.LEFT)

        t = 'MA-20'
        self.sHMAShort = t
        wxCombo = wx.ComboBox(parent, -1, value=t, choices=list(self.DICT), style=wx.CB_DROPDOWN)
        wxCombo.Bind(wx.EVT_COMBOBOX,self.WxGetHMAShort)
        wxSizerTmp.Add(wxCombo, proportion=0, border=5, flag=wx.ALIGN_CENTRE|wx.RIGHT)

        wxSizer.Add(wxSizerTmp, proportion=0, border=20, flag=wx.ALIGN_CENTRE|wx.TOP)

        ##############################
        # Create HMA long
        wxSizerTmp = wx.BoxSizer(orient=wx.HORIZONTAL)

        wxText = wx.StaticText(parent, -1, label="SMA long:  ", style=wx.ALIGN_CENTRE|wx.TE_LEFT)
        wxText.SetFont(wx.Font(pointSize=12, family=wx.ROMAN, style=wx.NORMAL, weight=wx.NORMAL))
        wxSizerTmp.Add(wxText, proportion=0, border=5, flag=wx.ALIGN_CENTRE|wx.LEFT)

        t = 'MA-60'
        self.sHMALong = t
        wxCombo = wx.ComboBox(parent, -1, value=t, choices=list(self.DICT), style=wx.CB_DROPDOWN)
        wxCombo.Bind(wx.EVT_COMBOBOX,self.WxGetHMALong)
        wxSizerTmp.Add(wxCombo, proportion=0, border=5, flag=wx.ALIGN_CENTRE|wx.RIGHT)

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

        ##############################
        # Plot MA
        wxPlot = self.wxCanvasFig.add_subplot(111)          # Create subplot - 0: MA

        # Curve: SMA short
        ser = self.dfStock['Close'].rolling(window=self.DICT[self.sSMAShort]).mean()
        ser = ser[ser.index >= self.DateStart]
        ser = ser[ser.index <= self.DateEnd]
        xd = np.arange(0, len(ser.index))
        wxPlot.plot(xd, ser, color='black', label=self.sSMAShort, linewidth=0.5)

        wxPlot.set_xlim(0,len(ser.index))
        wxPlot.set_xticks(range(0, len(ser.index), 100))
        wxPlot.set_xticklabels([ser.index[i].strftime('%Y-%m-%d') for i in wxPlot.get_xticks()], rotation=30)
        wxPlot.grid(b=True, axis='x', color='grey', linestyle='-', linewidth=0.2)            # Set grid
        '''
        # Curve: SMA long
        ser = self.dfStock['Close'].rolling(window=self.DICT[self.sSMALong]).mean()
        wxPlot.plot(xd, ser, color='yellow', label=self.sSMALong, linewidth=0.5)

        # Curve: HMA short
        T = self.DICT[self.sHMAShort]
        serHshort = self.dfStock['Close'].ewm(alpha=2 / T, adjust=False, ignore_na=True).mean() * 2
        serHlong = self.dfStock['Close'].ewm(alpha=1 / T, adjust=False, ignore_na=True).mean()
        ser = serHshort - serHlong
        serHMA = ser.ewm(alpha=1 / T ** 0.5, adjust=False, ignore_na=True).mean()
        wxPlot.plot(xd, serHMA, color='red', label=self.sSMALong, linewidth=0.5)

        # Curve: HMA long
        T = self.DICT[self.sHMALong]
        print(T)
        serHshort = self.dfStock['Close'].ewm(alpha=2 / T, adjust=False, ignore_na=True).mean() * 2
        serHlong = self.dfStock['Close'].ewm(alpha=1 / T, adjust=False, ignore_na=True).mean()
        ser = serHshort - serHlong
        serHMA = ser.ewm(alpha=1 / T ** 0.5, adjust=False, ignore_na=True).mean()
        wxPlot.plot(xd, serHMA, color='red', label=self.sSMALong, linewidth=0.5)
        '''
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


