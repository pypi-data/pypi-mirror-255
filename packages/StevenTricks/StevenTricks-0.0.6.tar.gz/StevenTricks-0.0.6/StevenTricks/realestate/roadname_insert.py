# -*- coding: utf-8 -*-

import pandas as pd
import StevenTricks.db_sqlite as db
from os.path import join
from StevenTricks import db_path
from StevenTricks.dfi import replace_series

dirname = "Examin"
# Valuer , Examin

tablename = "202203"
# valuer ==> "2021"
# examin ==> "202110"

if dirname == 'Valuer':
    dbname = "ValuerBuy.db"
elif dirname == 'Examin':
    dbname = 'Examin.db'
    
#%%

iter_temp = db.readsql_iter(join(db_path, "CrossWalk.db"), table_list=["adm", "road"])
adm = next(iter_temp)
road = next(iter_temp)

road = pd.merge(road, adm, on=["TOWNCODE"])
road.loc[:, "length"] = road["ROADNAME"].map(lambda x: len(x))
road = road.sort_values(by=["TOWNCODE", "length"], ascending=False).drop(["length"], axis=1)

table = next(db.readsql_iter(join(db_path, dirname, dbname), table_list=[tablename]))
table = table.reindex(columns=["COUNTYNAME", "COUNTYCODE", "TOWNNAME", "TOWNCODE", "GUSTRE", "ROADNAME", "ID"]).dropna(axis=1, how="all")

if "TOWNCODE" not in table :
    try :
        table = pd.merge( table , adm , on = [ _ for _ in table if _ in adm ] , how = "inner")
    except ValueError :
        pass
    
# 連接路名的關鍵是towncode所以檢查有沒有towncode和加入towncode，在這之後的table資料是依定會具有TOWNCODE欄位的
if "TOWNCODE" not in table :
    if "TOWNNAME" in table :
        table.loc[ : , "TOWNCODE"] = replace_series(series = table["TOWNNAME"] , std_dict = dict( road.loc[ : , ["TOWNCODE" , "TOWNNAME"] ].values ) , mode = "exac" )
    else :
        table.loc[ : , "TOWNCODE"] = replace_series( series = table["GUSTRE"] , std_dict = dict( zip( road["TOWNCODE"] , road[ ["COUNTYNAME" , "TOWNNAME" ] ].values.tolist() ) ) , mode = "exac" )
    db.addcols_df( df = road.loc[ : , ["TOWNCODE"] ] , table = tablename )
    sql = r"update '{table}' set TOWNCODE=? where id=?".format(table = tablename )
    db.cursor.executemany( sql , table.loc[ : , ["TOWNCODE" , "ID"] ].values )
    db.conn.commit()
table.loc[ : , 'TOWNCODE'] = table['TOWNCODE'].astype(str)

# 有roadname就是已經處理過的，現在要抓出上一次處理沒有成功插入路名的資料
if "ROADNAME" in table :
    table = table.drop( table.dropna( subset = ["ROADNAME"] , how = "any").index )

# 開始執行依照towncode去插入路名的工作
for towncode in table["TOWNCODE"].astype(str).unique() :
    print(towncode)
    table.loc[ table["TOWNCODE"] == towncode , "ROADNAME"] = replace_series( series = table.loc[ table["TOWNCODE"] == towncode , "GUSTRE"] , std_dict = dict( zip ( road.loc[ road["TOWNCODE"] == towncode , "ROADNAME" ] , road.loc[ road["TOWNCODE"] == towncode , "ROADNAME" ] ) ) , mode = "exac" )

db.addcols_df( df = road.loc[ : , [ "ROADNAME" ] ] , table = tablename )
sql = r"update '{table}' set ROADNAME=? where id=?".format( table = tablename )
db.cursor.executemany( sql , table.loc[ : , ["ROADNAME" , "ID"] ].values )
db.conn.commit()

table = table.drop( table.dropna( subset = [ _ for _ in ["COUNTYCODE" , "TOWNCODE" , "ROADNAME"] if _ in table ] , how = "any" ).index , errors = 'ignore' )

#%%

addrtemp_dict = {}
import sqlite3
conn = sqlite3.connect( join( db_path , "CrossWalk.db") )
cursor = conn.cursor()

for addr , towncode in table.loc[ : , [ "GUSTRE" , "TOWNCODE" ] ].values :
    if towncode in addrtemp_dict :
        if [ _  for _ in addrtemp_dict[ towncode ] if _ in addr ] : continue
        
    i = input("{}\n{}\nenter the road or skip(n or N):".format( addr , towncode ) )
              
    if i not in ["n" , "N" ] and i in addr :
        sql = r"insert into 'road'(TOWNCODE,ROADNAME) values ('{}' , '{}')".format( towncode , i )
        cursor.execute( sql )
        conn.commit()
        if towncode not in addrtemp_dict : 
            addrtemp_dict[towncode] = [ i ]
        else :
            addrtemp_dict[ towncode ].append( i )
        print( [ towncode , i ] , "Commit Successfully !")