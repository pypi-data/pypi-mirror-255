#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Sep  4 01:31:25 2020

@author: stevenhsu
"""

import pandas as pd
import os
import pickle

def PickleLoad(path):
    with open(path,"rb") as f :
        df=pickle.load(f)
    return df

def PickleSave(path,df,save_name,dire=""):
    if  dire != ""             : path = os.path.join(path,dire)
    if not os.path.isdir(path) : os.mkdir(path)
    path = os.path.join(path,save_name)
    with open(path,"wb") as f :
        pickle.dump(df,f)

# def FormatTrans(path,Fom="",):
#     if "csv" in Fom:
#         df=pd.read_csv()

def excel_split(Path,Fname,Extname):
    path=os.path.join(Path,Fname)
    df=pd.read_excel(path+Extname,sheet_name=None)
    for v1 in df :
        v2=path+v1+".pkl"
        df[v1].to_pickle(v2)
    return

def path_walk(path,targ="",targlis=[],level=1):
    resdic={}
    for v1 in os.walk(path):
        for v2 in v1[2]:
            if targ != "" :
                name=v2.replace(".pkl","")
                globals()[name]=PickleLoad(os.path.join(v1[0],v2))
                if v2 == targ : resdic[name]= globals()[name]
            elif targlis :
                if v2 in targlis : 
                    name=v2.replace(".pkl","")
                    globals()[name]=PickleLoad(os.path.join(v1[0],v2))
                    resdic[name]=globals()[name]
            else :
                if ".pkl" in v2 :
                    name=v2.replace(".pkl","")
                    globals()[name]=PickleLoad(os.path.join(v1[0],v2))
                    resdic[name]=globals()[name]
        level-=1
        if level == 0 : return resdic
    return resdic



v1=pd.read_csv(r"C:\Users\118939\Documents\GitHub\Sinopac\QGIS\County.csv")
v2=PickleLoad(r"C:\Users\118939\Documents\GitHub\Sinopac\Auto_Review\Project2\Review\4.pkl")
v3=PickleLoad(r"C:\Users\118939\Documents\GitHub\Sinopac\Auto_Review\Project2\Review\5.pkl")
v1=v1.loc[(v1["COUNTY"]=="臺北市") | (v1["COUNTY"]=="新北市") ]
v3=v3.loc[(v3.index.str.contains("臺北市"))|(v3.index.str.contains("新北市"))]
v1["Rate"]=""
for v4 in v1["TOWN"].unique().tolist():
    
    v5=v3.loc[v3.index.str.contains(v4),"+-10%"]
    print(v4,v5)
    try:
        v1.loc[v1["TOWN"]==v4,"Rate"]=int(v5)
    except:
        v1.loc[v1["TOWN"]==v4,"Rate"]=int(0)
    # break
    # print(v1.loc[v1["TOWN"]==v4,"Rate"])
#     v1.loc[v1["COUNTY"].str.contains("臺北市") & v1["TOWN"].str.contains(v4),"Rate"]=v3.loc["臺北市","+-10%"]
#     v1.loc[v1["COUNTY"].str.contains("新北市") & v1["TOWN"].str.contains(v4),"Rate"]=v3.loc["新北市","+-10%"]
#     v1.loc[v1["COUNTYNAME"]==v4,["TaiwanRate","CountyRate"]]=v2.loc[v4,"+-10%"],v3.loc[v4,"+-10%"]
    
# v1=v1.fillna(0)
v1.to_csv(r"C:\Users\118939\Documents\GitHub\Sinopac\QGIS\Test2.csv",encoding="big5")
# PickleSave(r"/Users/stevenhsu/Documents/GitHub/Sinopac/QGIS/twn_population",v1,"111.pkl")
# v2=PickleLoad(r"/Users/stevenhsu/Documents/GitHub/Sinopac/QGIS/twn_population/111.pkl")
# v3=PickleLoad(r"/Users/stevenhsu/Documents/GitHub/Sinopac/Auto_Review/Project2/Review/Countypercent.pkl")

# v2.replace("臺","台",inplace=True)
# for v4 in v3.index.tolist():
#     v2.loc[v2["COUNTY"]==v4,"Rate"]=v3.loc[v4,"+-10%"]
    
# v2.to_csv(r"/Users/stevenhsu/Documents/GitHub/Sinopac/Auto_Review/Project2/Review/Countypercent.csv",encoding="big5")