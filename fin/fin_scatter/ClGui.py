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
import mpl_finance as mpf #替换 import matplotlib.finance as mpf
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
###     LayoutPanelCmd():   Layout panel cmd: ./Text: 'Stock Code', ./Check: 'MA-1/5/10...', ./Btn: '绘图';
###     BtnPlotMA():        Button bind function: Plot MA;
###     LayoutPanelPlot():  Layout panel plot: ./Canvas/CanvasFig;
##########################################################################################
class ClGui(wx.App):
    def __init__(self,sStockCode=None,dfStock=None):
        self.sStockCode=sStockCode                      # Must init params here
        self.dfStock=dfStock
        self.FIB=[0.191, 0.236, 0.382, 0.5, 0.618, 0.764]
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
    ### Layout panel cmd: ./Text: 'Stock Code', ./Check: 'MA-1/5/10...', ./Btn: '绘图';
    ############################################################
    def LayoutPanelCmd(self, parent):
        wxSizer = wx.BoxSizer(orient=wx.VERTICAL)

        ##############################
        # Create ./Text: Stock code
        wxText = wx.StaticText(parent, -1, label=self.sStockCode, style=wx.ALIGN_CENTRE|wx.TE_LEFT)
        wxText.SetFont(wx.Font(pointSize=16,family=wx.ROMAN,style=wx.NORMAL,weight=wx.BOLD))
        wxSizer.Add(wxText, proportion=0, border=20, flag=wx.ALIGN_CENTRE|wx.TOP|wx.BOTTOM)

        ##############################
        # Create ./Check: 'MA1/5/10/20/30/40/50/60/120/240'
        wxSizerMA = wx.BoxSizer(orient=wx.HORIZONTAL)

        wxSizerGrid1=wx.FlexGridSizer(rows=5, cols=1, vgap=10, hgap=10)
        self.wxCheckMA1 = wx.CheckBox(parent, label='MA-1')
        self.wxCheckMA1.SetValue(True)
        wxSizerGrid1.Add(self.wxCheckMA1, proportion=0, border=5, flag=wx.EXPAND|wx.ALIGN_CENTRE|wx.TOP|wx.BOTTOM)
        self.wxCheckMA5 = wx.CheckBox(parent, label='MA-5')
        wxSizerGrid1.Add(self.wxCheckMA5, proportion=0, border=5, flag=wx.EXPAND|wx.ALIGN_CENTRE|wx.TOP|wx.BOTTOM)
        self.wxCheckMA10 = wx.CheckBox(parent, label='MA-10')
        wxSizerGrid1.Add(self.wxCheckMA10, proportion=0, border=5, flag=wx.EXPAND|wx.ALIGN_CENTRE|wx.TOP|wx.BOTTOM)
        self.wxCheckMA20 = wx.CheckBox(parent, label='MA-20')
        wxSizerGrid1.Add(self.wxCheckMA20, proportion=0, border=5, flag=wx.EXPAND|wx.ALIGN_CENTRE|wx.TOP|wx.BOTTOM)
        self.wxCheckMA30 = wx.CheckBox(parent, label='MA-30')
        wxSizerGrid1.Add(self.wxCheckMA30, proportion=0, border=5, flag=wx.EXPAND|wx.ALIGN_CENTRE|wx.TOP|wx.BOTTOM)
        wxSizerMA.Add(wxSizerGrid1, proportion=0, border=5, flag=wx.ALIGN_CENTRE|wx.LEFT|wx.RIGHT)

        wxSizerGrid2=wx.FlexGridSizer(rows=5, cols=1, vgap=10, hgap=10)
        self.wxCheckMA40 = wx.CheckBox(parent, label='MA-40')
        wxSizerGrid2.Add(self.wxCheckMA40, proportion=0, border=5, flag=wx.EXPAND|wx.ALIGN_CENTRE|wx.TOP|wx.BOTTOM)
        self.wxCheckMA50 = wx.CheckBox(parent, label='MA-50')
        wxSizerGrid2.Add(self.wxCheckMA50, proportion=0, border=5, flag=wx.EXPAND|wx.ALIGN_CENTRE|wx.TOP|wx.BOTTOM)
        self.wxCheckMA60 = wx.CheckBox(parent, label='MA-60')
        wxSizerGrid2.Add(self.wxCheckMA60, proportion=0, border=5, flag=wx.EXPAND|wx.ALIGN_CENTRE|wx.TOP|wx.BOTTOM)
        self.wxCheckMA120 = wx.CheckBox(parent, label='MA-120')
        wxSizerGrid2.Add(self.wxCheckMA120, proportion=0, border=5, flag=wx.EXPAND|wx.ALIGN_CENTRE|wx.TOP|wx.BOTTOM)
        self.wxCheckMA240 = wx.CheckBox(parent, label='MA-240')
        wxSizerGrid2.Add(self.wxCheckMA240, proportion=0, border=5, flag=wx.EXPAND|wx.ALIGN_CENTRE|wx.TOP|wx.BOTTOM)
        wxSizerMA.Add(wxSizerGrid2, proportion=0, border=5, flag=wx.ALIGN_CENTRE|wx.LEFT|wx.RIGHT)

        wxSizer.Add(wxSizerMA, proportion=0, border=5, flag=wx.ALIGN_CENTRE|wx.ALL)

        ##############################
        # Create ./Btn: '绘图'
        wxBtnPlot = wx.Button(parent, -1, label="绘  图")
        wxBtnPlot.SetFont(wx.Font(pointSize=12,family=wx.ROMAN,style=wx.NORMAL,weight=wx.NORMAL))
        wxBtnPlot.Bind(event=wx.EVT_BUTTON,
                       handler=self.BtnPlotMA)
        wxSizer.Add(wxBtnPlot, proportion=0, border=10, flag=wx.ALIGN_CENTRE|wx.TOP|wx.BOTTOM)

        parent.SetSizer(wxSizer)

    ############################################################
    ### Layout panel plot: ./Canvas/CanvasFig
    ############################################################
    def LayoutPanelPlot(self,parent):
        self.wxSizer = wx.BoxSizer(orient=wx.VERTICAL)          # Create sizer

        self.wxCanvasFig = Figure()                             # Create Figure
        self.wxCanvas = FigureCanvas(parent, -1, self.wxCanvasFig)
        self.wxSizer.Add(window=self.wxCanvas, proportion=1, border=2, flag=wx.EXPAND|wx.ALL)

        parent.SetSizer(self.wxSizer)

    ############################################################
    ### Button bind function: Plot MA
    ############################################################
    def BtnPlotMA(self, event):
        self.wxSizer.Hide(self.wxCanvas)
        self.wxCanvasFig.clear()

        ##############################
        # Plot MA
        PlotMA = self.wxCanvasFig.add_subplot(111)          # Create subplot - 0: MA
        xd = np.arange(0, len(self.dfStock.index))

        if(self.wxCheckMA1.GetValue() == True):
            PlotMA.plot(xd, self.dfStock['MA1'], color='red', label='MA-1', linewidth=0.5)
        if(self.wxCheckMA5.GetValue() == True):
            PlotMA.plot(xd, self.dfStock['MA5'], color='red', label='MA-5', linewidth=0.5)
        if(self.wxCheckMA10.GetValue() == True):
            PlotMA.plot(xd, self.dfStock['MA10'], color='red', label='MA-10', linewidth=0.5)
        if(self.wxCheckMA20.GetValue() == True):
            PlotMA.plot(xd, self.dfStock['MA20'], color='red', label='MA-20', linewidth=0.5)
        if(self.wxCheckMA30.GetValue() == True):
            PlotMA.plot(xd, self.dfStock['MA30'], color='red', label='MA-30', linewidth=0.5)
        if(self.wxCheckMA40.GetValue() == True):
            PlotMA.plot(xd, self.dfStock['MA40'], color='red', label='MA-40', linewidth=0.5)
        if(self.wxCheckMA50.GetValue() == True):
            PlotMA.plot(xd, self.dfStock['MA50'], color='red', label='MA-50', linewidth=0.5)
        if(self.wxCheckMA60.GetValue() == True):
            PlotMA.plot(xd, self.dfStock['MA60'], color='red', label='MA-60', linewidth=0.5)
        if(self.wxCheckMA120.GetValue() == True):
            PlotMA.plot(xd, self.dfStock['MA120'], color='red', label='MA-120', linewidth=0.5)
        if(self.wxCheckMA240.GetValue() == True):
            PlotMA.plot(xd, self.dfStock['MA240'], color='red', label='MA-240', linewidth=0.5)

        PlotMA.plot(xd, self.dfStock['EMA30'], color='black', label='EMA-30', linewidth=0.5)
        PlotMA.plot(xd, self.dfStock['HMA30'], color='green', label='HMA-30', linewidth=0.5)

        PlotMA.legend(loc='best', shadow=True, fontsize='8')
        self.wxCanvas.draw()
        self.wxSizer.Show(self.wxCanvas)


