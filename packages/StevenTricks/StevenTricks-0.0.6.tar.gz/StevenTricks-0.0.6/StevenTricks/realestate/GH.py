# -*- coding: utf-8 -*-
"""
Created on Thu Apr 21 11:26:23 2022

@author: 118939
"""

import pandas as pd
from StevenTricks import Workdir
from StevenTricks import db_sqlite as db
from StevenTricks.dfi import replace_series


def valuecompare_str(io, comp_list):
    for _ in comp_list:
        if io in _ or _ in io:
            return True
    return False


valid_date = '2022-07-01'
# 指定到期日，到期日在valid_date之後的才算是合格綠建築
proj = 'part'
# all, part
examin_date = '2022-01-01'
# 一次一整年，月份和日期只是為了符合格式輸入的
res = pd.DataFrame()
workdir = Workdir()
adm = next(workdir.crosswalk_iter())
deptgroup = next(workdir.crosswalk_iter())

# In[]
if __name__ == '__main__':

    # 如果是all就是把歷年全部估價案件都帶入，如果是part就是只帶入指定年分
    if proj == 'all':
        df = pd.concat(list(db.readsql_iter(r'D:\database\Valuer\ValuerFull.db', table_list=[])), ignore_index=True)

    elif proj == 'part':
        df = next(db.readsql_iter(r'D:\database\Valuer\ValuerFull.db', table_list=[examin_date.split('-')[0]]))

    # 開始幫帶入的鑑估資料
    df.loc[:, "TOWNCODE"] = replace_series(series=df["GUSTRE"], std_dict=dict(zip(adm["TOWNCODE"], adm[["COUNTYNAME", "TOWNNAME"]].values.tolist())), mode="exac")
    df = pd.merge(df, adm.loc[:, ['COUNTYCODE', 'TOWNNAME', 'COUNTYNAME', 'TOWNCODE']], on=['TOWNCODE'], how="left")
    df = df.dropna(subset=['CASENM', 'TOWNCODE'], how='any')

    # 幫證號預留欄位
    df.insert(0, '證號', None)

# In[]
    # 開始進行比對
    for county in df['COUNTYCODE'].unique():
        # 依照鑑估資料的縣市欄位，去讀取綠建築的資訊
        gh_df = pd.concat(list(db.readsql_iter(workdir.path, table_list=[county])))
        # 綠建築讀取完成之後，要進行簡單的篩選
        gh_df = gh_df.loc[(gh_df['VALID_DATE'] > valid_date) & (gh_df['OwnerType'] == '民間') & gh_df['USESCOPE_DETL'].str.contains('住', na=False)]
        # 如果篩選完是空的就跳出，有東西的話就進行比對
        if gh_df.empty is True:
            print('green house in {} is empty'.format(county))
        else:
            # 比對前進行資料準備
            # 因為綠建築資料已經取好了，這裡有同步取一個鑑估資料的temp檔，做為比對使用
            df_temp = df.loc[df['COUNTYCODE'] == county]
            # 因為資料內的社區名可能會有兩種表達方式，所以用stdcol_list來篩選，看這個綠建築資料，是用哪種方式表達
            stdcol_list = [_ for _ in ['CASENM', '社區名'] if _ in gh_df]
            # 開始從社區欄位取值，進行比對
            for std_list in gh_df.loc[:, stdcol_list + ['證號']].dropna(subset=stdcol_list, how='all').values.tolist():

                # 每一個迴圈都會重新從df_temp取值，取空值出來進行比對
                df_temp = df_temp.loc[df_temp['證號'].isna() | (df_temp['證號'] == False)]
                if df_temp.empty is True:
                    continue

                # 從std_list取出證號
                cert_str = std_list.pop()
                # 把剩下沒取出的做一個清理，如果剩下都是None的話，那就會剩下一個空的list
                std_list = [_ for _ in std_list if pd.isna(_) is False]

                # 利用valuecompare_str這個函數，來判斷是否含有證號，然後填入df_temp
                df_temp.loc[:, '證號'] = df_temp.loc[:, 'CASENM'].map(lambda x: valuecompare_str(str(x), std_list))
                df_temp.loc[df_temp['證號'] == True, '證號'] = cert_str
                # 有抓到的部分放入res裡面
                res = pd.concat([res, df_temp.loc[~df_temp['證號'].isna() & (df_temp['證號'] != False)]])
# In[]
    gh_df = pd.concat(list(db.readsql_iter(workdir.path)))
    gh_df = gh_df.loc[(gh_df['VALID_DATE'] > valid_date) & (gh_df['OwnerType'] == '民間') & gh_df['USESCOPE_DETL'].str.contains('住', na=False)]
    res = pd.merge(res.loc[:, ['COUNTYNAME', 'TOWNNAME', 'CASENM', 'GUSTRE', 'Floor', 'USESCOPE_DETL', 'ID', '承作區域', '證號']], gh_df.loc[:, ['證號', 'level', 'VALID_DATE']], on=['證號'])
    res = res.rename(columns={'COUNTYNAME': '縣市', 'TOWNNAME': '行政區', 'CASENM': '社區', 'GUSTRE': '地址', 'Floor': '樓層資訊', 'USESCOPE_DETL': '使用型態', 'ID': '估價報告編號', 'VALID_DATE': '證號有效期'})
    if proj == 'all':
        res = res.drop_duplicates(subset=['縣市', '行政區', '社區'], ignore_index=True)
        res.groupby(['縣市', '行政區', '社區']).first().to_excel(r'C:\Users\118939\Desktop\全台社區名單彙整.xlsx')

    elif proj == 'part':
        res.groupby(['縣市', '行政區', '社區']).first().to_excel(r'C:\Users\118939\Desktop\單年綠建築名單.xlsx')