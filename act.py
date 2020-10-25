#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import glob
import numpy as np
import scipy.signal
from pylab import *
import csv
import matplotlib.pyplot as plt
import pandas as pd
import os
import datetime
import matplotlib.dates as mdates
import sys
from matplotlib.widgets import Cursor
from _plotly_future_ import v4_subplots
from plotly.subplots import make_subplots
import plotly.graph_objs as go
import plotly.offline as offline
import dash
import json
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input,Output
import plotly.express as px
from eogeeg import eogeeg_fft

def active_f(data):#data=csvlist[0]
    """
    pathdata = sys.argv[1]
    csvlist = glob.glob(pathdata + "/*.csv") #フォルダ内の全てのファイル名のlist
    csvlist.sort()
    """
    num = []
    plotdata = []
    active = pd.read_csv(data, header = None, names=["num","data","zero","time"]) #選択したcsvlistを読み込む
    datanum = len(active) // 120
    for i in range(datanum):
        num.append(i)
    for i in range(1, datanum + 1):
        maxdata = max(active["data"][120 * i - 120 : 120 * i])
        plotdata.append(maxdata)
    data=go.Bar(x=pd.Series(num), y=pd.Series(plotdata))
    fig=go.Figure(data=data)
    return fig
