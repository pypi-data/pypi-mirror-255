# -*- coding: utf-8 -*-
"""
Created on Tue Dec 22 17:49:19 2020

@author: 118939
"""
from StevenTricks import Workdir
from StevenTricks import db_path
from StevenTricks.dfi import dateinterval_series, numinterval_series
from StevenTricks import db_sqlite as db
from os.path import join

import pandas as pd

##
if __name__ == '__main__':
    filename = '江翠_大樓'
    workdir = Workdir()
    road = '環河西路五段|藝文一街|藝文街|藝文二街|永翠路|香社一路|香社二路|板城路|環河西路四段|溪頭街|新月三街|新月二街|新月一街|華江|田翠北街|文新路'
    # '合宜路|樂群路|合宜一路|大觀路二段|和安路'
    # 環河西路五段|藝文一街|藝文街|藝文二街|永翠路|香社一路|香社二路|板城路|環河西路四段|溪頭街|新月三街|新月二街|新月一街|華江|田翠北街|文新路
    groupdict = {
        # "BUILDMSR": [0, 10, 20, 30, 40, 50, 75, 100],
        # "BuildingAge" : [0,9,19,29,39,49,59] ,
        }
    # 0,19,29,39,49,59,69,79,89,99,9999
    op_dict = {
        'BUILD_FLRPRC': 'mean',
        'daterange': 'count', }
    # '2017.db' , '2018.db' , '2019.db' ,
    year = ['2018.db', '2019.db', '2020.db', '2021.db', '2022.db']
    county = [65000]
    town = ['6500001']
    # 6500016
    _zip = '220'
    # 243
    freq = 'MS'
    # MS，QS
    if workdir.proj_dict['dir'] in ['Agent']:
        df = pd.concat(list(db.readsql_iter(join(workdir.path, 'sell'), db_list=year, table_list=county)), ignore_index=True)
        df = df.loc[df['ZIP'].isin([_zip]) & df['BDTYPE_DETL'].str.contains('住|套', na=False)]
        # 住|套
        # 寓
        df = df.loc[df['GUSTRE'].str.contains(road, na=False)]

        df.loc[:, 'daterange'] = dateinterval_series(df['Updated_DATE'], freq=freq)
        df.loc[:, 'BUILD_FLRPRC'] = df['BUILD_FLRPRC']/10000

        df = df.sort_values(by=['Updated_DATE', 'title'])
        df.loc[df.index.isin(df['title'].drop_duplicates(keep="last").index), "salesdays"] = df["Updated_DATE"]
        df.loc[:, 'salesdays'] = df["salesdays"].fillna(method="ffill")
        df.loc[:, "salesdays"] = (df["Updated_DATE"] - df["salesdays"]).dt.days

    elif workdir.proj_dict['dir'] in ['ActualPrice']:
        df = pd.concat(list(db.readsql_iter(join(workdir.path, '不動產買賣'), db_list=year, table_list=county)))
        df = df.loc[df['TransactionSign'].str.contains('房地|建物', na=False) & df['TOWNCODE'].isin(town)]

        df = df.loc[df['BDTYPE_DETL'].str.contains('住宅|華廈|套房', na=False)]
        # '住宅大樓(11層含以上有電梯)', '公寓(5樓含以下無電梯)', '華廈(10層含以下有電梯)', '透天厝','套房(1房1廳1衛)', '店面(店鋪)', '廠辦', '辦公商業大樓'
        # 公寓
        # 住宅|華廈|套房
        df = df.loc[df['GUSTRE'].str.contains(road, na=False)]
        df.loc[:, 'daterange'] = dateinterval_series(df['DATE'], freq=freq)

    elif workdir.proj_dict['dir'] in ['Valuer']:
        df = pd.concat(list(db.readsql_iter(join(workdir.path, 'ValuerBuy.db'), table_list=[_.split('.')[0] for _ in year])))
        df = df.loc[df['BDTYPE_DETL'].str.contains('大樓', na=False) & df['GUSTRE'].str.contains('汐止', na=False)]
        # 公寓
        # 大樓
        df = df.loc[df['GUSTRE'].str.contains(road, na=False)]
        df.loc[:, 'daterange'] = dateinterval_series(df['DATE'], freq=freq)


    df = df.sort_values(by=["daterange"], ignore_index=True, ascending=False)
    res = df.groupby(['daterange']).agg(op_dict)

    if 'salesdays' in df:
        df = df.loc[df['salesdays'] != 0]
        res = pd.concat([res, df.groupby(['daterange']).agg({'salesdays': 'mean'})], axis=1)

    res = res.rename(columns={
        'BUILD_FLRPRC': '平均單價',
        'daterange': '交易量',
        'salesdays': '銷售天數',
        })

    with pd.ExcelWriter(join(db_path, "{}_{}.xlsx".format(workdir.proj_dict['dir'], filename)), engine='xlsxwriter') as writer:
        res = res.fillna(method='ffill')
        res.to_excel(writer)


    for key in groupdict:
        rangekey = key + '_range'
        res = numinterval_series(df[key], groupdict[key])
        res = pd.concat([df['daterange'], pd.to_numeric(df[key]).dropna(), res.rename(rangekey)], axis=1)
        res = res.groupby(['daterange', rangekey]).agg({key: 'count'})
        res = res.unstack(-1)

        with pd.ExcelWriter(join(db_path, "{}_{}_{}_range.xlsx".format(workdir.proj_dict['dir'], filename, key)), engine='xlsxwriter') as writer:
            res.to_excel(writer)


##
#
# import matplotlib.pyplot as plt
# import geopandas as gpd
# from statsmodels.tsa.seasonal import seasonal_decompose
#
# decomposition = seasonal_decompose(data["BUILD_FLRPRC"].dropna(), freq=6,model="additive")
# decomposition.plot()
# # plt.plot(decomposition)
# decomposition.observed.plot()
# a=decomposition.trend.plot()
# decomposition.seasonal.plot()
# decomposition.resid.plot()
#
# a = decomposition.trend-decomposition.trend.mean()
# plt.plot(a)
# # In[]
# from steventricks.algorithm import kmeans
# from sklearn.model_selection import train_test_split as tts
# from catboost import CatBoostRegressor
#
# origin = decomposition.trend.dropna().reset_index()
# x = origin.daterange
# y = origin.trend
#
# x_train , x_test , y_train , y_test = tts(x , y , test_size = 0.2 , random_state = 87 )
# model=CatBoostRegressor(iterations=1000, depth=5, learning_rate=0.1, loss_function='RMSE',has_time =True)
# model.fit(x_train, y_train,eval_set=(x_test, y_test),plot=True)
#
# p = model.predict(y)
#
# # In[]
#
# # import matplotlib.pyplot as plt
# from steventricks.algorithm import kmeans
# import numpy as np
# import geopandas as gpd
#
# res = pd.merge(countymap,data,how="left")
# res["DISTRICT"] = res["DISTRICT"].apply(np.sqrt)
# res.plot(column="DISTRICT",cmap="Blues",edgecolor='black',legend=True,missing_kwds={"color": "white","label": "缺失值"},legend_kwds={'label': "count by Country",'orientation':"vertical"},figsize=(100,100))
#
# res["總價(萬)"] = res["總價(萬)"].apply(np.sqrt)
# res.plot(column="總價(萬)",cmap="Blues",edgecolor='black',legend=True,missing_kwds={"color": "white","label": "缺失值"},legend_kwds={'label': "count by Country",'orientation':"vertical"},figsize=(100,100))
#
# res.loc[:,["DISTRICT","COUNTY","總價(萬)"]]
# # In[]
#
#
# for i in d.COUNTY.unique():
#     res=gpd.GeoDataFrame(d.loc[d["COUNTY"]==i,:])
#     res["roadname"] = res["roadname"].apply(np.sqrt)
#     res.loc[:,"roadname"] = res.loc[:,"roadname"].apply(np.sqrt)
#     res.plot(column="roadname",cmap="Blues",edgecolor='black',legend=True,missing_kwds={"color": "white","label": "缺失值"},legend_kwds={'label': "count by Country",'orientation':"vertical"},figsize=(100,100))
#     print(i)
#
# e = datac["2020"].groupby(["COUNTY","DISTRICT","roadname"]).agg({"roadname":"count"}).rename(columns={"roadname":"road"})
# e = e.sort_values(by ="road", ascending = False)
#
# # In[]
# import dash
# import dash_core_components as dcc
# import dash_html_components as html
# import plotly.express as px
# res = px.treemap(datac,color_continuous_scale='PuBu',path=[px.Constant('Taiwan'),"COUNTY","建物型態","總價(萬)"],values="總價(萬)",color="總價(萬)",hover_data=["總價(萬)"])
# app = dash.Dash()
# app.layout = html.Div([dcc.Graph(figure=res)])
# app.run_server(debug=True, use_reloader=False)
#
#
#
# data = cutoutliers_series(data , col = "總價(元)")
#
# res_list = []
# n = 3
# df_range = daterange_iter(data , "交易年月日" , r"W")
#
# for df in df_range:
#     if df.empty == True :
#         print(df)
#         continue
#
#     df_kmeans = df.iloc[:,:2]
#     k = kmeans(df_kmeans,cluster=3)
#
#     k_df = pd.DataFrame(k.cluster_centers_)
#     k_df.insert(2,2, df["交易年月日"].min())
#     res_list.append( k_df.values.tolist() )
#
#     print(df["交易年月日"].min())
#
# res_list = [i for x in res_list for i in x]
# df_res = pd.DataFrame(res_list)