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


def eogeeg_fft():

    pathdata = sys.argv[1]
    csvlist = glob.glob(pathdata + "/*.csv") #フォルダ内の全てのファイル名のlist
    filenum = len(csvlist)
    csvlist.sort()
    sum = [[]  for _ in range(6)]
    fs = 100 #サンプリング周波数（一秒間の周波数）
    nyq = fs / 2.0  #ナイキスト周波数

    def filterall(numtaps, cut):
        eog=df["EOG"]
        time = df["Datetime"]
        f2 = cut / nyq
        #フィルタの作成
        b = scipy.signal.firwin(numtaps, cutoff=f2, pass_zero='highpass')
        #フィルタ係数の保存
        with open('coeff.csv', 'w') as f:
            writer = csv.writer(f, lineterminator='\n') #改行コード（\n）の指定
            writer.writerow(b)
        #フィルタをかける
        eogxy=scipy.signal.lfilter(b,1,eog)
        #積分値
        a1 = (len(eogxy) - numtaps) // 3
        integrated_list =[]
        for i in range(3): #i=0,1,2
            integrated = 0
            for j in range(numtaps + a1 * i, numtaps + a1 * (i + 1)): #numtaps= 303, a1=(filterの長さ-numtaps)//3, j = 303+a1*i(i=0,1,2)
                integrated += abs(eogxy[j])
            integrated_list.append(integrated)
        return integrated_list

    datetime = []
    for i in range(1,filenum): #１つのcsvlistが120秒分のデータ（これを3分割）
        df=pd.read_csv(csvlist[i],header=None,names=["num","Datetime","EEG","EOG"])
        a = filterall(303,0.50)
        for j in range(3): #a[j]を3回足している（同じ値）
            sum[4].append(a[j])
            #datetime.append(df["Datetime"][i]) #sum[4]= deepsleep

    #EEG
    for m in range(1,filenum):
        if m != 0:
            df=pd.read_csv(csvlist[m],header=None,names=["num","Datetime","EEG","EOG"])

            N = 512
            fs = 100 #サンプリング周波数
            t = 1 / fs #サンプリング周期
            hanningfil = scipy.signal.hann(N)

            data = [[] for _ in range(3)]
            hann = [[] for _ in range(3)]
            fft = [[] for _ in range(3)]
            fftabs = [[0] * N for _ in range(3)]
            amp =[[0]  * N for _ in range(3)]
            pow = [[0] * N for _ in range(3)]
            eeg = []
            jikan = len(csvlist[m])//2
            data[0] = list(df["EEG"][0:N]) #csvlist[i]を三つに分割
            data[1] = list(df["EEG"][800 - N : 800])
            data[2] = list(df["EEG"][1200 - N : 1200])
            datetime.append(df["Datetime"][0])
            datetime.append(df["Datetime"][jikan * 1 - 1])
            datetime.append(df["Datetime"][jikan * 2 - 1])


            for i in range(3):
                for j in range(len(data[i])):
                    hann[i].append(data[i][j] * hanningfil[j])#ひとつのdataに対して窓関数をかける（dataは3つある）
                fft[i] = np.fft.fft(hann[i], n = N)#fftする

            for i in range(3):
                for j in range(N): #N=512
                    amp[i][j] = np.abs(fft[i][j])
                    pow[i][j] = amp[i][j] * amp[i][j]

            freqlist = np.fft.fftfreq(N, d = t) #横軸の設定


            subsum = [[0] * 3 for _ in range(5)]


            for i in range(3):
                for j in range(int(N/2)): #積分値
                    if freqlist[j] >= 0.5 and freqlist[j] <= 4.0:
                        if freqlist[j] <= 2.0: #deepsleep
                            subsum[4][i] += pow[i][j]
                        subsum[0][i] += pow[i][j] #δ
                    elif freqlist[j] > 4.0 and freqlist[j] <= 8.0:
                        subsum[1][i] += pow[i][j] #θ
                    elif freqlist[j] > 8.0 and freqlist[j] <= 13.0:
                        subsum[2][i] += pow[i][j] #α
                    elif freqlist[j] > 13.0 and freqlist[j] <= 30.0:
                        subsum[3][i] += pow[i][j] #β

                for k in range(5):
                    if k == 4:
                        sum[k + 1].append(subsum[k][i])
                    else:
                        sum[k].append(subsum[k][i])

    def barplot(p):
        plt.subplot(6,1,p + 1)
        plt.bar(xpole,sum[p])

    disprange = 0
    multiple = 35
    for i in range(6):
        if i != 4:
            disprange += min(sum[i])
    disprange /= 5
    disprange *=multiple

    xBar = pd.Series(datetime)

    data0= go.Bar(
        x = xBar,
        y = sum[0],
        name = "δ",
        width = 1

    )
    data1= go.Bar(
        x = xBar,
        y = sum[1],
        name = "θ",
        width = 1

    )
    data2= go.Bar(
        x = xBar,
        y = sum[2],
        name = "α",
        width = 1



    )
    data3= go.Bar(
        x = xBar,
        y = sum[3],
        name = "β",
        width = 1


    )
    data4= go.Bar(
        x = xBar,
        y = sum[4],
        name = "Deepsleep",
        width = 1

    )
    data5 = go.Bar(
        x = xBar,
        y = sum[5],
        name = "EOG",
        width = 1

    )

    fig = make_subplots(
        rows=6, cols=1,
        shared_xaxes = True,
        vertical_spacing = 0.001

        )
    fig.append_trace(data0,1,1)
    fig.append_trace(data1,2,1)
    fig.append_trace(data2,3,1)
    fig.append_trace(data3,4,1)
    fig.append_trace(data4,5,1)
    fig.append_trace(data5,6,1)

    fig.update_yaxes(range = [min(sum[0]),50000000], row = 1, col= 1)
    fig.update_yaxes(range = [min(sum[1]),50000000], row = 2, col= 1)
    fig.update_yaxes(range = [min(sum[2]),50000000], row = 3, col= 1)
    fig.update_yaxes(range = [min(sum[3]),50000000], row = 4, col= 1)
    fig.update_yaxes(range = [min(sum[4]),min(sum[4])*15], row = 5, col= 1)
    fig.update_yaxes(range = [min(sum[5]),50000000], row = 6, col= 1)

    fig.update_layout(height=1000, width=1300, title='after FFT')

    return fig
