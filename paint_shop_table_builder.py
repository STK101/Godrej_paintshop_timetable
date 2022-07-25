# -*- coding: utf-8 -*-
"""Paint_shop_table_builder.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1MXNkxiO7et9EpEBXwr0VENSPMGTbLQfu
"""

import numpy as np
import pandas as pd
import re

class timer:
  def __init__(self, hour, min, sec):
    self.hour = hour
    self.min = min
    self.sec = sec
  def add_hr(self,hour):
    hour = int(hour)
    self.hour = (self.hour + hour)%24
  def add_min(self, min):
    min = int(min)
    self.min = self.min + min
    self.add_hr(self.min/60)
    self.min = (self.min)%60
  def add_sec(self,sec):
    self.sec += sec
    self.add_hr(self.sec/3600)
    self.sec = (self.sec)%3600
    self.add_min(self.sec/60)
    self.sec = (self.sec)%60
  def print_time(self):
    hrs = str(self.hour)
    mns = str(self.min)
    secs = str(self.sec)
    if (self.hour/10 < 1):
      hrs = "0" + str(self.hour)
    if (self.min/10 < 1):
      mns = "0" + str(self.min)
    if (self.sec/10 < 1):
      secs = "0" + str(self.sec)
    out = hrs + ":" + mns + ":" + secs
    return out


def setup_colour():
  colourfile = pd.ExcelFile('Light & Dark Color Shade List in MES(1).xlsx')
  colourdf = pd.read_excel(colourfile, colourfile.sheet_names[0] )
  colourdf.drop(colourdf.columns[0:2], axis = 1, inplace = True)
  colourdf= colourdf.iloc[5:]
  colourdf.columns = colourdf.iloc[0]
  colourdf = colourdf.iloc[1:]
  colourdf.reset_index(drop = True, inplace = True)
  colourdf.fillna("bad", inplace = True)
  colourdf["LIGHT"] = colourdf["LIGHT"].apply(lambda x: re.sub("[^a-z0-9]+", '', x.lower()))
  colourdf["DARK"] = colourdf["DARK"].apply(lambda x: re.sub("[^a-z0-9]+", '', x.lower()))
  light = colourdf["LIGHT"].unique()
  dark = colourdf["DARK"].unique()
  return (dark, light)

dark , light = setup_colour()
def check_shade(colour):
  colour = re.sub("[^a-z0-9]+", '', colour.lower())
  if (colour in light):
    return 1
  elif  (colour in dark):
    return 0
  else :
    print("missing colour" + " " + colour)
    return 1

def shift(t1):
  if ( (t1.hour > 8 and t1.hour <= 15) or (t1.hour == 8 and t1.min >= 0)):
    return 1
  else:
    return 2
def time_comp(t1,t2):
  s1 = shift(t1)
  s2 = shift(t2)
  if (s1 != s2):
    return (s1 > s2)
  else:
    if (s1 == 1):
      if (t1.hour > t2.hour):
        return True
      elif (t1.hour == t2.hour and t1.min > t2.min):
        return True
      else :
        return False
    else:
      if (t1.hour == 23 and t2.hour == 23):
        return t1.min > t2.min
      elif (t1.hour == 23):
        return False
      elif (t2.hour == 23):
        return True
      else:
        if (t1.hour > t2.hour):
          return True
        elif (t1.hour == t2.hour and t1.min > t2.min):
          return True
        else :
          return False

def time_table_gen(source, line = 1,cold_start_min = 30):
  df = pd.read_csv(source, index_col = 0)
  if (len(df) == 0):
    return df
  """
  if (line == 1):
    t1 =  list((df["PRIORITY"]).astype(int) == 1)
    t0 =  list((df["PRIORITY"]).astype(int) == 0)
    to = list(np.logical_or(t1,t0))
    l1 = df[to]
  if (line == 2):
    t2 =  list((df["PRIORITY"]).astype(int) == 2)
    t3 =  list((df["PRIORITY"]).astype(int) == 3)
    to = list(np.logical_or(t2,t3))
    l1 = df[to]
  """
  l1 = df
  l1.reset_index(drop = True, inplace = True)
  time = timer(8,30,0)
  if (len(l1) == 0):
    return l1

  time.add_min(cold_start_min)


  l1["IN-Time"] = " "
  l1["OUT-Time"] = " "
  print(l1)
  l1.iloc[[0],[-2]] = time.print_time()
  br1 = timer(12,0,0)
  br2 = timer(15,0,0)
  br3 = timer(3,0,0)
  br4 = timer(8,0,0)
  bre1 = timer(12,30,0)
  bre2 = timer(23,30,0)
  bre3 = timer(3,30,0)
  break_st = [br1, br2, br3]
  break_end = [bre1,bre2,bre3]


  cur_break = 0
  breaker = False
  bs =  False
  i_list = []
  bset = True
  for i in range(0,len(l1)):
    if (i < len(l1) - 1):
      cycle_time = 1
      sim_sku_change = 0
      change_over_time = 0
      if ( check_shade(l1.iloc[i][-5]) == check_shade(l1.iloc[i+1][-5])):
        change_over_time = 8 
      else:
        change_over_time = 20
      qt = int((l1.iloc[i])[-4])
      temp_time = timer(time.hour,time.min,time.sec)
      final_time = qt*cycle_time + (qt-1)*sim_sku_change
      temp_time.add_min(final_time)
      if ((shift(time) == 2 and shift(temp_time) == 1) or (bset == False and shift(time) == 1)):
        if(shift(time) == 1):
          l1.loc[i - 0.2] = [" ", " ", " ", "BackLog", " ", " ", " ", " ", " "]
          break
        breaker = True
      if (bset and ((time_comp(break_st[cur_break], time) and time_comp(temp_time, break_st[cur_break])) or ((time_comp(time,break_st[cur_break]))))):
        if((time_comp(time,break_st[cur_break]))):
          bs = True
        if (cur_break == 1):
          time.add_min(390)
        else:
          time.add_min(30)
        if (bs):
          l1.iloc[[i],[-2]] = time.print_time()
          i_list.append([i,1,cur_break])
        else:
          i_list.append([i,0, cur_break])
        cur_break = (cur_break + 1)%3
        if(cur_break == 0):
          bset = False
      
      bs = False
      time.add_min(final_time)
      l1.iloc[[i],[-1]] = time.print_time()
      time.add_min(change_over_time)
      if (breaker):
        l1.loc[i + 0.2] = [" ", " ", " ", "BackLog", " ", " ", " ", " ", " "]
        break
      l1.iloc[[i+1],[-2]] = time.print_time()
    else :
      cycle_time = 1
      sim_sku_change = 1
      qt = int((l1.iloc[i])[-4])
      temp_time = timer(time.hour,time.min,time.sec)
      final_time = qt*cycle_time + (qt-1)*sim_sku_change
      temp_time.add_min(final_time)
      if (shift(time) == 2 and shift(temp_time) == 1):
        breaker = True
      if (time_comp(break_st[cur_break], time) and time_comp(temp_time, break_st[cur_break])):
        if((time_comp(time,break_st[cur_break]))):
          bs = True
        if (cur_break == 1):
          time.add_min(390)
        else:
          time.add_min(30)
        if (bs):
          l1.iloc[[i],[-2]] = time.print_time()
        cur_break = (cur_break + 1)%3  
      bs = False
      time.add_min(final_time)
      if (breaker):
        l1.loc[i + 0.2] = [" ", " ", " ", "BackLog", " ", " ", " ", " ", " "]
        break
      l1.iloc[[i],[-1]] = time.print_time()
  for i in i_list:
    if (i[1] == 0):
      l1.loc[i[0] + 0.4] = l1.loc[i[0]]
      l1.loc[[i[0]], ["OUT-Time"]] = break_st[i[2]].print_time()
      l1.loc[i[0] + 0.2] = [" ", " ", " ", "Break", " ", " ", " ", " ", " "]
      l1.loc[[i[0] + 0.4],["IN-Time"]] = break_end[i[2]].print_time()

    else:
      l1.loc[i[0] - 0.2] = [" ", " ", " ", "Break", " ", " ", " ", " ", " "]
  l1 = l1.sort_index().reset_index(drop=True)
  l1['DATE'] = l1['DATE'].astype(str)
  return l1


