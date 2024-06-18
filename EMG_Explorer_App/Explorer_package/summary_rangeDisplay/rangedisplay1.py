import sys
sys.path.append('EMG_Explorer_App/Explorer_package/summary_rangeDisplay')

from requirement_rangedisplay1 import *

def forAllRows(function,df:pd.DataFrame,**arg):

    display = []
    for id,row in df.iterrows():
        x = function(row['Value'],**arg)
        display.append(x)
        display.append("<br>")

    return display

def forAllRowsdf(function,df:pd.DataFrame,**arg):
    display = []

    for id,row in df.iterrows():
        x = function(row,**arg)
        display.append(x)
        display.append("<br>")

    return display

def forAllGroup(function,df:pd.DataFrame,**arg):

    display = []
    df_group = df.groupby(['Group'], group_keys=True)
    for gr,data in df_group:
        print(data)
        x = function(data.loc[:,'Value'],**arg)
        display.append(f"{gr}")
        display.append(x)
        display.append("<br>")

    return display

def forAllGroupdf(function,df:pd.DataFrame,**arg):

    display = []
    df_group = df.groupby(['Group'], group_keys=True)
    for gr,data in df_group:
        x = function(data,**arg)
        display.append(f"{gr}")
        display.append(x)
        display.append("<br>")

    return display

def randomRows(function,df:pd.DataFrame,**arg):
    display = []

    for id_row in np.random.choice(list(df.index),size=5,replace=False):
        row = df.iloc[id_row]
        x = function(row,**arg)
        display.append(x)
        display.append("<br>")

    return display