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

#選択した時刻周り30分のactivityデータ表示グラフの作成
#activityはcsvlist[0]（activityはただ入力値をグラフ表示してるだけ）
#activityは1秒おきに取得している
#csvlist[0]のdatetimeを選択→その時刻の周辺30分のデータ（一個のデータ＝1秒なので30*60=1800個表示　前後30分なので前900個後ろ900個　前（または後ろ）に900個データがない時はゼロにする）

def active_30(data,i): #data=csvlist[0]
    dtlist=[]
    valuelist=[]
    df=pd.read_csv(data, header=None, names=["num","value","zero","Datetime"])
    dtlist=list(df["Datetime"]) #時間のlist
    valuelist=list(df["value"]) #値のlist
    e_time=[] #グラフに表示させる時刻
    e_value=[] #グラフに表示させるデータ
    data_length=len(valuelist)

    #時刻とデータの入力
    if i-900<0:  #iより前に900個のデータがない時は、ない部分は0 例えばi=400番目の時900-400=500個はゼロ
        e_value[0:900-i]=[0]*i
        e_value[900-i:900]=valuelist[0:i]
        e_value[900:1800]=valuelist[i:i+900]

        e_time[0:900-i]=[0]*i
        e_time[900-i:900]=dtlist[0:i]
        e_time[900:1800]=dtlist[i:i+900]

    elif i+900>data_length: #後ろに900個のデータがない時　例えばdata_length=1300でi=1100の時 後ろの900-200=700個はゼロ
        e_value[0:900]=valuelist[i-900:i]
        e_value[900:900+data_length-i]=valuelist[i:data_length]
        e_value[900+data_length-i:1800]=[0]*i

        e_time[0:900]=dtlist[i-900:i]
        e_time[900:900+data_length-i]=dtlist[i:data_length]
        e_time[900+data_length-i:1800]=[0]*i
        
    else:
        e_value=valuelist[i-900:i+900]
        e_time=dtlist[i-900:i+900]

    data=go.Bar(x=pd.Series(e_time), y=pd.Series(e_value))
    fig=go.Figure(data=data)
    return fig
