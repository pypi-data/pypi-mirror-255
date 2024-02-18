# -*- coding: utf-8 -*-

from StevenTricks.snt import numfromright
from StevenTricks.dfi import numinterval_series, flat_dict
import StevenTricks.db_sqlite as db

from StevenTricks import reasondict
from StevenTricks import db_path

from os.path import join
from os import makedirs
from datetime import timedelta
import calendar
import pandas as pd
import sqlite3
import re

reasondict = flat_dict(dic=reasondict)


def percent_series(series, point=2):
    percent = round((series / series.sum())*100, point)
    return pd.concat([percent, series], ignore_index=True, axis=1)


def reason(text):
    for key in reasondict:
        if key in str(text):
            return reasondict[key]
    print('原因的文字辨識要再加上: ', text)
    return '買價高於區域行情'


project = 'Valuer'
# Valuer, Examin
month = "2022-04-01"
# yyyy-mm-01


if project == 'Valuer':
    table = month.split('-')[0]
elif project == 'Examin':
    table = month.rsplit('-', 1)[0].replace('-', '')
# 2021, 202111

packet = {
    'table': table,
    'sourcedir': join(db_path, project),
    'month': month,
    'year': month.split('-')[0],
    'reportdir': join(db_path, project, "report", month.rsplit("-", 1)[0].replace("-", ""))
    }

packet.update({
    'reportpath': join(packet['reportdir'], "{}_{}.xlsx".format(project, packet['month'])),
    'analysispath': join(packet['reportdir'], "{}_{}_analysis.xlsx".format(project, packet['month'])),
                })

makedirs(packet['reportdir'], exist_ok=True)

temp_iter = db.readsql_iter(join(db_path, "CrossWalk.db"), table_list=["adm", "deptgroup"])
adm = next(temp_iter)
adm = adm.loc[:, ["COUNTYNAME", "TOWNNAME", "TOWNCODE", "COUNTYCODE"]]
ao = next(temp_iter)
ao = ao.loc[:, ["AODEPTCODE", "AODEPT"]]
ao['AODEPTCODE'] = ao.loc[:, 'AODEPTCODE'].str.zfill(3)
del temp_iter, table

# In[]
if project == "Valuer":
    valuer = next(db.readsql_iter(join(packet['sourcedir'], 'ValuerBuy.db'), table_list=[packet['year']]))
    valuer = valuer.loc[valuer['DATE'].between(month, '{}-{}'.format(month.rsplit('-', 1)[0], str(calendar.monthrange(int(month.split('-')[0]), int(month.split('-')[1]))[1])))]
    valuer = valuer.loc[~valuer["DateExamin"].isna()].reset_index(drop=True)

elif project == "Examin":
    examin = next(db.readsql_iter(join(packet['sourcedir'], 'Examin.db'), table_list=[packet['table']]))
    # 取得審查給的資料
    year_list = list(range(examin["DATE"].min().year - 5, examin["DATE"].max().year + 1, 1))
    # 把潛在需要用到的實價登錄年份都取出來
    valuer = pd.concat(list(db.readsql_iter(join(db_path, "Valuer", "Valuer.db"), table_list=year_list)))
    # 取得歷年的全部鑑估資料
    valuer = valuer.drop([_ for _ in valuer if _ in examin and _ != "ID"], axis=1)
    # 因為資料以審查的為準，所以找出鑑估資料和審查資料重複的欄位，且把他刪掉，只留下ID欄位，因為ID會在後面被用來整合
    valuer.loc[:, 'ID'] = valuer['ID'].astype(str).str.zfill(16)
    # ID欄位就算進入sqlite之前是string格式，讀取出來之後也會變成int格式，開頭的0會被省略掉，所以要自己補上
    valuer = pd.merge(examin, valuer, on=["ID"])
    # 以ID做整合，融合兩個df，已經不需要用到審查的資料了

valuer.loc[:, 'AODEPTCODE'] = valuer['ID'].str.slice(start=2, stop=5)
valuer = pd.merge(valuer, ao, on=["AODEPTCODE"], how="left")
valuer.loc[: , "Number"] = valuer["GUSTRE"].map(lambda x: numfromright(x))
# 從地址裡面找出門牌號碼
valuer.loc[: , ["LOW_STORY" , "HIGH_STORY" , "STORY"] ] = valuer["Floor"].str.split("~|/" , expand = True , n = 2).rename(columns = { 0: "LOW_STORY" , 1: "HIGH_STORY" , 2: "STORY" })
# 把樓層做拆分
valuer.loc[ (valuer["LOW_STORY"] == valuer["HIGH_STORY"]) , "Case_story" ] = valuer["HIGH_STORY"]
valuer.loc[ (pd.to_numeric(valuer["LOW_STORY"] , errors = "coerce") <= 1) & (valuer["HIGH_STORY"] == valuer["STORY"]) , "Case_story" ] = "全"
valuer.loc[ valuer["Case_story"].isna() , "Case_story" ] = valuer["LOW_STORY"] + "," + valuer["HIGH_STORY"]
# 找出真正的交易樓層Case_story
valuer = pd.merge(valuer , adm , on = [ _ for _ in adm if _ in valuer ] , how = "left")
valuer.loc[: , "TotalPin"] = valuer["BUILDMSR"] + valuer["STALLMSR"]
del adm , ao
# In[]
towncode_list = valuer["TOWNCODE"].unique().tolist()
countycode_list = valuer["COUNTYCODE"].unique().tolist()
year_list = ['{}.db'.format(str(_)) for _ in list(range(valuer["DATE"].min().year - 5, valuer["DATE"].max().year + 1, 1))]
ActualPrice = pd.concat([_.loc[_["TransactionSign"].str.contains("房地", regex=True, na=False)] for _ in db.readsql_iter(join(db_path, "ActualPrice", "不動產買賣"), table_list=countycode_list, db_list=year_list)])
ActualPrice = ActualPrice.drop(['ADDRESS_X', 'ADDRESS_Y', '有無備註欄'], axis=1, errors="ignore")
ActualPrice = ActualPrice.loc[ActualPrice["TOWNCODE"].isin(towncode_list)]
ActualPrice = ActualPrice.set_index("ID", drop=True)
ActualPrice["STORY"] = ActualPrice["STORY"].astype(str).str.rsplit(".", expand=True, n=1)[0]

# In[]
conn = sqlite3.connect(join(db_path, "CrossWalk.db"))
cursor = conn.cursor()
res = pd.DataFrame()
for i in valuer.index:
    print("\r{} ==> {}%".format(i, round(i/valuer.shape[0], 3)*100), end="")

    AP_temp = ActualPrice.loc[ActualPrice["TOWNCODE"] == valuer["TOWNCODE"][i]]
    if AP_temp.empty is True:
        valuer.loc[i, "Note"] = "TOWNCODE: 核貸書 {}".format(valuer["TOWNCODE"][i])
        continue

    if pd.isna(valuer["ROADNAME"][i]) is False:
        AP_temp = AP_temp.loc[AP_temp["GUSTRE"].str.contains(valuer["ROADNAME"][i], regex=True, na=False)]
        if AP_temp.empty is True:
            valuer.loc[i, "Note"] = "RoadName:{}".format(valuer["ROADNAME"][i])
            continue

    AP_temp = AP_temp.loc[AP_temp["GUSTRE"].str.contains(re.escape(valuer["Number"][i]), regex=True, na=False)]
    if AP_temp.empty is True:
        valuer.loc[i, "Note"] = "Number:{}".format(valuer["Number"][i])
        continue

    AP_temp = AP_temp.loc[AP_temp["STORY"].isin([ valuer["STORY"][i]])]
    if AP_temp.empty is True:
        valuer.loc[i, "Note"] = "STORY: {}".format(valuer["STORY"][i])
        continue

    AP_temp = AP_temp.loc[AP_temp["Case_story"].str.contains(valuer["Case_story"][i], regex=True, na=False)]
    if AP_temp.empty is True:
        valuer.loc[i, "Note"] = "Case_story: {}".format(valuer["Case_story"][i])
        continue

    AP_temp = AP_temp.loc[(AP_temp["DATE"] >= valuer["DATE"][i] - timedelta(weeks=52)) & (AP_temp["DATE"] <= valuer["DATE"][i] + timedelta(weeks=24))]
    if AP_temp.empty is True:
        valuer.loc[i, "Note"] = "DATE"
        continue

    AP_temp = AP_temp.loc[ ((AP_temp["BUILDMSR"] >= valuer["BUILDMSR"][i] - 0.5) & (AP_temp["BUILDMSR"] <= valuer["BUILDMSR"][i] + 0.5)) | ((AP_temp["BUILDMSR"] >= valuer["TotalPin"][i] - 0.5) & (AP_temp["BUILDMSR"] <= valuer["TotalPin"][i] + 0.5))]
    if AP_temp.empty is True:
        valuer.loc[i, "Note"] = "Pin:{}".format(valuer["BUILDMSR"][i])
        continue

    # if pd.isnull(valuer["FNSH_DATE"][i]) != True:
    #     ActualPrice_copy1.loc[(ActualPrice_copy1["FNSH_DATE"].dt.year == valuer["FNSH_DATE"][i].year) & (ActualPrice_copy1["FNSH_DATE"].dt.month == valuer["FNSH_DATE"][i].month),"建築完成日比對結果"] = r"ok"
    # elif pd.isnull(valuer["FNSH_DATE"][i]) == True:
    #     ActualPrice_copy1.loc[:,"建築完成日比對結果"] = None

    AP_temp.loc[:, "temp"] = (AP_temp["REALTY_SUMVAL"] - valuer["PriceExamin"][i]).abs()
    AP_temp = AP_temp.sort_values(by="temp").drop("temp", axis=1)

    temp = AP_temp.iloc[0]

    valuer.loc[i, "候選編號"] = ",".join(AP_temp[1:].index)

    res = pd.concat([res, AP_temp])
    valuer.loc[i, "實價登錄價格"] = temp["REALTY_SUMVAL"]
    valuer.loc[i, "實價登錄編號"] = temp.name
    valuer.loc[i, "超過10%原因"] = "".join(valuer.loc[i, ["IMPRINT_RSN_DETL", "SPCGAGE_DETL", "承作區域", "FIX_TYPE"]].dropna()) + str(temp["備註"])
    # zz = ActualPrice[10:100]

# In[]
valuer.loc[:, "超過10%原因"] = valuer["超過10%原因"].map(lambda x: reason(x))
valuer.loc[:, "估價/實價登錄"] = (valuer["PriceValuer"] / valuer["實價登錄價格"] - 1) * 100
valuer.loc[:, "核貸書/實價登錄"] = valuer["PriceExamin"] / valuer["實價登錄價格"]
valuer = valuer.round({"核貸書/實價登錄": 2, "PriceExamin": 0, "實價登錄價格": 0, "估價/實價登錄": 2})
if 'Sequence' in valuer:
    valuer = valuer.sort_values(by="Sequence")

# In[]

resdic = {}
resdic["實價登錄有無"] = (~valuer["實價登錄價格"].isna()).value_counts()
resdic["縣市分佈"] = valuer["COUNTYNAME"].value_counts()
resdic["估價超過10%原因"] = valuer.loc[valuer["估價/實價登錄"] > 10 , "超過10%原因"].value_counts()
resdic["估價小於10%原因"] = valuer.loc[valuer["估價/實價登錄"] < -10 , "超過10%原因"].value_counts()
resdic["價差20%以上明細"] = valuer.loc[valuer["估價/實價登錄"] > 20, ["ID", 'AODEPT', "PriceValuer", "PriceExamin", "實價登錄價格", "估價/實價登錄", "超過10%原因"]]

# 只針對有比對出實價登錄的資料
valuer_temp = valuer.loc[~valuer["實價登錄價格"].isna()]

valuer_temp.loc[:, '核貸和實價登錄誤差'] = numinterval_series(valuer_temp["核貸書/實價登錄"], [0.999, 1.001], ["低於", "相符", "高於"])
resdic["核貸和實價登錄誤差"] = valuer_temp['核貸和實價登錄誤差'].value_counts()
resdic["分行核貸書誤差"] = valuer_temp.loc[valuer_temp['核貸和實價登錄誤差'] != "相符", "AODEPT"].value_counts()
valuer_temp.loc[:, '估價和實價登錄誤差'] = numinterval_series(valuer_temp["估價/實價登錄"], [-30, -20, -10, -5, -1, 1, 5, 10, 20, 30])
resdic["估價和實價登錄誤差"] = valuer_temp['估價和實價登錄誤差'].value_counts().sort_index(ascending=False)

for series in resdic:
    if series == "價差20%以上明細":
        continue
    resdic[series] = percent_series(resdic[series], point=2)

# In[]

with pd.ExcelWriter(packet['reportpath']) as writer:
    valuer.to_excel(writer, sheet_name="回查成果")
    res.to_excel(writer, sheet_name="實價登錄")

with pd.ExcelWriter(packet['analysispath']) as writer:
    for sheet in resdic:
        resdic[sheet].to_excel(writer, sheet_name=sheet)