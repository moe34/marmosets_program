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
from act import active_f
from act_thirty import active_30

#生データ
eeg_raw_data= []
eog_raw_data= []
datetime = []
actdt=[]
xlim = []

pathdata = sys.argv[1]
csvlist = glob.glob(pathdata + "/*.csv") #フォルダ内の全てのファイル名のlist
filenum = len(csvlist) #フォルダ内のファイルの個数
csvlist.sort()


#生データ追加
#(1個のcsvリストが120秒のデータ　時間を一つ選択した時にひとつのcsvをグラフ表示する)
act=pd.read_csv(csvlist[0],header=None, names=["num","value","zero","Datetime"])
actdt=list(act["Datetime"])

for m in range(1,filenum):
    df=pd.read_csv(csvlist[m],header=None,names=["num","Datetime","EEG","EOG"]) #1つのファイルに1200個のデータ
    eeg_raw_data.append(df["EEG"]) #120*filenum?
    eog_raw_data.append(df["EOG"])
    datetime.append(df["Datetime"][1])

for i in range(len(eeg_raw_data[1])):
    xlim.append(i)

#型の変換
eeg_raw_data =pd.Series(eeg_raw_data)
eog_raw_data =pd.Series(eog_raw_data)
xBar = pd.Series(datetime)
datetime = pd.Series(datetime)
csvlist = pd.Series(csvlist)
actdt=pd.Series(actdt)


app = dash.Dash(__name__)

app.layout = html.Div(

    [
        html.Label(["FFT Graph", dcc.Graph(id = "fft")]),
        html.Label(["Activity", dcc.Graph(id = "activity")]),
        html.Label(["Activity(30 minutes Expansion ver)", dcc.Graph(id = "act_30")]),
        html.Label(["EOG Raw Data", dcc.Graph(id = "eog_raw")]),
        html.Label(["EEG Raw Data", dcc.Graph(id = "eeg_raw")]),

        html.Label(
        [
            "Select a Date and Time:",
        #入力コンポーネントの設定
        dcc.Dropdown(
        id = 'dtlist',
        options=[{'label':i, 'value':i} for i in datetime],
        value = datetime[0],)
        ]
    ),


    html.Label(
    [
    "Select Datetime for expansion of Activity:",
    dcc.Dropdown(
    id = 'act_data_thirty',
    options=[{'label':i, 'value':i} for i in actdt],
    value = actdt[0],)
    ]
    ),

    html.Label(
    [
    "Activity Data:",
    dcc.Dropdown(
    id = 'act_data',
    options=[{'label':csvlist[0], 'value':csvlist[0]}],
    value = csvlist[0],)
    ]
    ),

    html.Label(
    [
    "data choosed:",
    dcc.Dropdown(
    id = 'filedata',
    options=[{'label':pathdata, 'value':pathdata}],
    value = pathdata,)
    ]
    ),
]
)

#FFT後のグラフ
@app.callback(
    Output(component_id = 'fft', component_property = 'figure'),
    [Input(component_id = 'filedata', component_property='value')])
def returndata(select):
    fig = eogeeg_fft()
    return fig

#Activity
@app.callback(
    Output(component_id = 'activity', component_property = 'figure'),
    [Input(component_id = 'act_data', component_property='value')])
def returndata(select):
    fig0 = active_f(csvlist[0])
    return fig0


#Activity拡大ver
@app.callback(
    Output(component_id = 'act_30', component_property = 'figure'),
    [Input(component_id = 'act_data_thirty', component_property='value')])

#act=pd.read_csv(csvlist[0],header=None, names=["num","value","zero","Datetime"])
def returndata(selected_dt):
    choose = 0
    for i in range(len(actdt)):
        if (str(selected_dt)== str(act["Datetime"][i])):
            choose = i
            break
    fig0_30=active_30(csvlist[0],choose)
    return fig0_30


#EOG_raw
@app.callback(
    Output(component_id = 'eog_raw', component_property = 'figure'),
    [Input(component_id = 'dtlist', component_property='value')])
def returndata(selected_dt): #selected_dt='value(入力された年のデータ)'
    choose = 0
    for i in range(filenum):
        df=pd.read_csv(csvlist[i],header=None,names=["num","Datetime","EEG","EOG"]) #1つのファイルに120個のデータ
        if str(selected_dt) == str(df["Datetime"][1]):
            choose = i
            break
    eogm = list(eog_raw_data[choose])
    fig1 = px.line(eog_raw_data[choose])
    return fig1

#EEG_raw
@app.callback(
    Output(component_id = 'eeg_raw', component_property = 'figure'),
    [Input(component_id = 'dtlist', component_property='value')])
def returndata(selected_dt): #selected_dt='value(入力された年のデータ)'
    choose = 0
    for i in range(filenum):
        df=pd.read_csv(csvlist[i],header=None,names=["num","Datetime","EEG","EOG"]) #1つのファイルに120個のデータ
        if str(selected_dt) == str(df["Datetime"][1]):
            choose = i
            break
    eegm = list(eeg_raw_data[choose])
    fig2 = px.line(eeg_raw_data[choose])
    return fig2


if __name__=='__main__':
    app.run_server(debug=True)
