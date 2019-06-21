#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Jun 18 20:54:54 2019

@author: rozmar
"""

import behavior_rozmar as behavior_rozmar
import pandas as pd
import numpy as np
bigtable = behavior_rozmar.loadcsvdata(projectdir = '/home/rozmar/Network/BehaviorRig/Behavroom-Stacked-2/labadmin/Documents/Pybpod/Projects')
data = bigtable
idxes = dict()
times = dict()
idxes['lick_L'] = data['var:WaterPort_L_ch_in'] == data['+INFO']
times['lick_L'] = data['PC-TIME'][idxes['lick_L']]
idxes['reward_L'] = (data['MSG'] == 'Reward_L') & (data['TYPE'] == 'TRANSITION')
times['reward_L'] = data['PC-TIME'][idxes['reward_L']]
idxes['lick_R'] = data['var:WaterPort_R_ch_in'] == data['+INFO']
times['lick_R'] = data['PC-TIME'][idxes['lick_R']]
idxes['reward_R'] = (data['MSG'] == 'Reward_R') & (data['TYPE'] == 'TRANSITION')
times['reward_R'] = data['PC-TIME'][idxes['reward_R']]
idxes['trialstart'] = data['TYPE'] == 'TRIAL'
times['trialstart'] = data['PC-TIME'][idxes['trialstart']]
idxes['trialend'] = data['TYPE'] == 'END-TRIAL'
times['trialend'] = data['PC-TIME'][idxes['trialend']]
idxes['GoCue'] = (data['MSG'] == 'GoCue') & (data['TYPE'] == 'TRANSITION')
times['GoCue'] = data['PC-TIME'][idxes['GoCue']]

numerofpoints = 10
#%%
alltimes = []
for timeskey in times.keys(): # finding endtime
   if len(alltimes) > 0:
       alltimes.append(times[timeskey])
   else:
       alltimes = times[timeskey]
startime = min(alltimes)+np.timedelta64(1,'h')
endtime = max(alltimes)
steptime = (endtime-startime)/numerofpoints
timerange = pd.date_range(start = startime, end = endtime, periods = numerofpoints*10) #freq = 's'
lick_left_num = np.zeros(len(timerange))
lick_right_num  = np.zeros(len(timerange))
reward_left_num = np.zeros(len(timerange))
reward_right_num = np.zeros(len(timerange))
for idx,timenow in enumerate(timerange):
    lick_left_num[idx] = sum((timenow+steptime > times['lick_L']) & (timenow-steptime<times['lick_L']))
    lick_right_num[idx] = sum((timenow+steptime > times['lick_R']) & (timenow-steptime<times['lick_R']))
    reward_left_num[idx] = sum((timenow+steptime > times['reward_L']) & (timenow-steptime<times['reward_L']))
    reward_right_num[idx] = sum((timenow+steptime > times['reward_R']) & (timenow-steptime<times['reward_R']))
print('kesz')

#%%
lista = list()
for i in range(10):
    lista.append(i)