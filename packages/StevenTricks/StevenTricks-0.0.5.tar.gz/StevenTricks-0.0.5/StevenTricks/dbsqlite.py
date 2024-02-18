# -*- coding: utf-8 -*-
from StevenTricks.snt import dtypes_df
from StevenTricks.fileop import PathWalk_df
from StevenTricks.dfi import replace_series

from os.path import join, basename, isfile, dirname, isdir, pardir, abspath
from os import makedirs

import pandas as pd
import numpy as np
import sqlite3
# 所有傳入的文件一律要自行加.db

sqltype_dict = {
    "text": ["object", "string"],
    "timestamp": ["M8", 'datetime64[ns]', 'pytz.FixedOffset(480)'],
    # 用timestamp儲存才會在dataframe讀取的時候自動被轉換為日期格式，datetime也可以儲存但是讀取的時候只會是object格式
    "numeric": ["float32", "Float32", "float64", "Float64", "int64", "Int64", 'bool', 'boolean'],
}


def dbchange(path):
    # 這裡的path一定要給完整路徑
    if isdir(abspath(join(path, pardir))) is False:
        print("Maked new dir ! =======================\n{}\n=======================================".format(abspath(join(path, pardir))))
        makedirs(abspath(join(path, pardir)), exist_ok=True)
    
    db_info = {
        "info": pd.DataFrame(),
        "dbname": '',
        "table_list": [],
        "tableadapter_list": [],
        "index_list": [],
        "view_list": [],
        }
    
    if isdir(path) is True:
        db_info["dbpath"] = path
        db_info["dbdir"] = path
        
    else:
        global conn, cursor
        conn = sqlite3.connect(path)
        cursor = conn.cursor()
        
        db_info["dbpath"] = path
        db_info["dbdir"] = dirname(path)

        db_info["info"] = pd.read_sql("select * from sqlite_master", conn)
        db_info["dbname"] = basename(path)
        
        info = db_info["info"]
        
        db_info["table_list"] = info[(info["type"] == "table") & ~(info['name'].str.contains('_', regex=True, na=False))]["name"]
        db_info["tableadapter_list"] = info[(info["type"] == "table") & (info['name'].str.contains('_', regex=True, na=False))]["name"]
        db_info["index_list"] = info[info["type"] == "index"]["name"]
        db_info["view_list"] = info[info["type"] == "view"]["name"]
        
    db_info["db_list"] = PathWalk_df(db_info["dbdir"], fileinclude=[".db"], level=0)['path']
    return db_info


def tableinfo_dict(table):
    table_info = {
        "info": pd.DataFrame(),
        "dtype_dic": {},
        "columns": [],
        "col_date": [],
        "pk": None,
        }
    
    info = pd.read_sql("PRAGMA table_info('{}') ".format(table), conn)
    table_info["info"] = info
    table_info["dtype_dic"] = dict(table_info["info"].loc[:, ["name", "type"]].values)
    table_info["columns"] = info['name']
    table_info["col_date"] = info.loc[info["type"].isin(["TIMESTAMP", "DATE", "timestamp", "date"]), "name"].tolist()
    if info.loc[info["pk"] > 0, "name"].empty is False:
        table_info["pk"] = info.loc[info["pk"] > 0, "name"].tolist()
    return table_info


def addcols_df(df, table):
    df = df.dropna(axis=1, how="all").convert_dtypes()
    tableinfo = tableinfo_dict(table)
    df = df.loc[:, [_ for _ in df if _ not in tableinfo['columns'].values]]
    if df.empty is True:
        return
    dtype_series = dtypes_df(df)
    dtype_series = replace_series(dtype_series, sqltype_dict, True, "fuzz")
    for col in df:
        sql = "alter table '{t}' add '{n}' {d}".format(t=table, n=col, d=dtype_series[col])
        try:
            cursor.execute(sql)
        except:
            print(sql)
            cursor.execute(sql)


def addtable_df(df, table, pk=[], autotime=False, notnullkey=[], uniquekey=[], fktable="", fk=[]):
    # 如果沒有指定pk就會自動用auto_pk，就是直接給一連串的連續數值
    df = df.dropna(axis=1, how="all")
    dtype_series = dtypes_df(df)
    dtype_series = replace_series(dtype_series, sqltype_dict, True, "fuzz")
    # print(dtype_series)
    dtype_dic = {colname: " '{colname}' {dtype} ".format(colname=colname, dtype=dtype) for colname, dtype in dtype_series.items()}
    
    constraint_dic = {
        " not null ": notnullkey,
        " unique ": uniquekey,
        }
    
    if [_ for _ in pk if _ in df] != pk or not pk:
        # 填入的pk如果沒有完全在df裏面就直接用auto_pk
        dtype_dic["Auto_pk"] = "Auto_pk integer primary key autoincrement"
        pk = ""
    else:
        pk = r",PRIMARY KEY({})".format(",".join(pk))
    
    if autotime is True :
        autotime = ',start_dt timestamp default (datetime(current_timestamp,\'localtime\'))'
        # ',Write_dt timestamp default current_timestamp not null'
    elif autotime is False:
        autotime = ''
        
    if [_ for _ in fk if _ in df] != fk or not fk or fktable == "":
        fk = ''
    else :
        fk = r",CONSTRAINT fk_{fktable} FOREIGN KEY ({fk}) REFERENCES '{fktable}'({fk})".format(fk=",".join(fk), fktable=fktable)
        
    for constraint, key_list in constraint_dic.items():
        for key in key_list:
            if key in pk:
                continue
            if key not in df:
                continue
            dtype_dic[key] += constraint
    sql = "create table if not exists '{tablename}'({colinfo}{autotime}{pk}{fk}) ".format(tablename=table, colinfo=",".join(dtype_dic.values()), autotime=autotime, pk=pk, fk=fk)
    try:
        cursor.execute(sql)
    except:
        print(sql)
        cursor.execute(sql)


def tosql_df(df, dbpath, table, pk=[], autotime=False, notnullkey=[], uniquekey=[], fktable="", fk=[]):
    # autotime就是在table裡面增加一個欄位，那個欄位會在資料新增的時候自動新增資料寫入的時間，通常是用在log紀錄寫入的瞬間自動新增一個時間欄位，精準到秒
    # dbpath一定要指定到檔名，且包含副檔名.db
    # only for the insert df into table without any condition
    # table 就是要自己指定database裡面的table的名稱
    # 如果要保留就是使用update(只更新有變動的部分)，如果不保留就是用replace into，這樣就會把有變動的部分放進去，其餘清空
    df = df.dropna(axis=1, how="all")
    db_info = dbchange(dbpath)
    if table not in db_info['table_list'].tolist() and table not in db_info['tableadapter_list'].tolist():
        # 如果這個table不存在就導入addtable去新增一個table
        addtable_df(df, table, pk, autotime, notnullkey, uniquekey, fktable, fk)
    else:
        # 如果這個table存在，就檢查column需不需要新增
        addcols_df(df, table)
    table_info = tableinfo_dict(table)
    
    df = df.astype(str).replace({"<NA>": np.nan})
    sql = "insert or ignore into '{table}'('{cols}')  values({values})".format(table=table, cols="','".join(df.columns), values=",".join(["datetime(?)" if _ in table_info["col_date"] else "?" for _ in df.columns]))
    try:
        cursor.executemany(sql, df.values)
    except:
        print(sql)
        cursor.executemany(sql, df.values)
    conn.commit()
    
    if "Auto_pk" not in table_info["pk"]:
        sql = "update '{table}' set {value} where {pkvalue}".format(table=table, value=",".join(["'{c}'=datetime(?)".format(c=c) if c in table_info["col_date"] else "'{c}'=?".format(c=c) for c in df.columns if c not in table_info["pk"]]), pkvalue=" and ".join(['{}=datetime(?)'.format(_) if _ in table_info["col_date"] else '{}=?'.format(_) for _ in table_info["pk"]]))
        try:
            cursor.executemany(sql, [a + b for a, b in zip(df.drop(table_info["pk"], axis=1).values.tolist(), df[table_info["pk"]].values.tolist())])
        except:
            print(sql)
            cursor.executemany(sql, [a + b for a, b in zip(df.drop(table_info["pk"], axis=1).values.tolist(), df[table_info["pk"]].values.tolist())])
        conn.commit()


def tosqladapter_df(df, dbpath, table, adaptertable, adapter_col, pk=[], adapter_pk=[], autotime=False, notnullkey=[], uniquekey=[]):
    # tablename is specify a col to seperate df into pieces
    # adapter_col and adapter_pk is only for the adapter table
    # pk is for original df and adapter_pk is mostly "auto_pk" , because only a few situation that adapter table has not duplicate column
    adapter_df = df.loc[:, [_ for _ in adapter_col + pk if _ in df]]
    tosql_df(adapter_df, dbpath, "{t}_{p}".format(t=table, p=adaptertable), adapter_pk, autotime, notnullkey, uniquekey, table, pk)
    
    df = df.sort_values(pk, ascending=True)
    if pk:
        df = df.drop_duplicates(subset=pk, keep="last")
    df = df.drop(adapter_col, axis=1)
    tosql_df(df, dbpath, table, pk, autotime, notnullkey, uniquekey)


def readsql_iter(dbpath, db_list=[], table_list=[], table_exclude=[], adapter=True, db_col=False, table_col=False, ind_col=None, chunksize=None):
    # dbpath可以是資料夾也可以是檔名，檔名一定要包含副檔名.db
    # table_list 就是只找某幾個table
    # db_list一定要是 "檔名.db"
    db_info = dbchange(dbpath)
    if isdir(dbpath) is True:
        if not db_list:
            db_list = db_info["db_list"].tolist()
            # 因為db_inifo裡面的資訊全部都是用Series，所以這裡要轉乘list才能直接用if去判斷
        elif db_list:
            db_list = [join(dbpath, str(_)) for _ in db_list]
    elif isfile(dbpath) is True:
        db_list = [dbpath]
    if not db_list:
        print('db_list is empty , pls check the dbpath.')
    for db in db_list:
        db_info = dbchange(db)
        if not table_list:
            Table_list = db_info['table_list'].tolist()
            # 因為db_inifo裡面的資訊全部都是用Series，所以這裡要轉乘list才能直接用if去判斷
        else:
            Table_list = [str(_) for _ in table_list if str(_) in db_info['table_list'].values]
            # 這裡用str(_)下去比對，是為了確保就算給的是數字(2021、2022)也能比對到
            # pd.Series 不支援用 X in db_info['table_list'] 的方式去比對裡面的value，所以如果要用in去比對的話，要先把後面加.values，才能用in去比對，但是用for loop 去迭代是可以把全部的value迭代出來
        if not Table_list:
            print('Table_list in \n{}\n is empty , pls check the table_list.'.format(db))
        for table in Table_list:
            if table_exclude and [_ for _ in table_exclude if _ in table]:
                continue
            table_info = tableinfo_dict(table=table)
            
            tabledf = pd.read_sql("select * from '{table}'".format(table=table), conn, parse_dates=table_info["col_date"], index_col=ind_col, chunksize=None)
            if adapter is True:
                tableadapter_list = db_info["tableadapter_list"][db_info["tableadapter_list"].str.contains("{}_".format(table), regex=True, na=False)]
                for tableadapter in tableadapter_list:
                    tableadapter_info = tableinfo_dict(tableadapter)
                    tableadapter_df = pd.read_sql("select * from '{}'".format(tableadapter), conn, parse_dates=tableadapter_info["col_date"], chunksize=None)
                    tableadapter_df = tableadapter_df.drop([_ for _ in tableadapter_df if _ in tabledf and _ not in tableadapter_info["pk"]], axis=1)
                    merge_cols = [_ for _ in tableadapter_info["pk"] if _ in tabledf]
                    tabledf.loc[:, merge_cols] = tabledf.loc[:, merge_cols].astype(str)
                    tableadapter_df.loc[:, merge_cols] = tableadapter_df.loc[:, merge_cols].astype(str)
                    tabledf = pd.merge(tabledf, tableadapter_df, on=merge_cols, how="outer")
                    
            if db_col is True:
                tabledf["DB_name"] = db
            if table_col is True:
                tabledf["Table_name"] = table
            
            if chunksize is not None:
                while tabledf.empty is False:
                    yield tabledf[:chunksize]
                    tabledf = tabledf[chunksize:]
            else:
                yield tabledf