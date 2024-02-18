# -*- coding: utf-8 -*-
"""
Created on Tue Apr 26 16:33:20 2022

@author: 118939
"""


import re
import sys
import locale
import pandas as pd


def findbylist(lis, text):
    # 可以給出一連串文字，放在list裏面，只要list裡面有其中一個文字是在text裡面的話，那就會返回搜尋結果，是一個list
    # 返回的字串以lis裡面匹配的為主
    return re.findall('|'.join([re.escape(_) for _ in lis]), text)


def isinstance_dfiter(df):
    # to tell the df if it is iterable or not
    try:
        iter(df)
        if isinstance(df, pd.DataFrame) is True:
            return False
        elif isinstance(df, pd.DataFrame) is False:
            return True
    except:
        return False
    

def tonumeric_int(char):
    # 用來判斷是否為數字，盡量返回整數，如果不是浮點數也不是整數就返回原來的字符
    try:
        res = float(char)
    except:
        return None
    # 因為float可以返回的種類最多，如果連float都無法返回那一定不是數值類型，就返回None
    # 下面以返回res為主，通常不是返回int，最少也會返回float
    try:
        if res == int(char):
            return int(char)
        else:
            return res
    except:
        return res


def dtypes_df(df):
    df = df.convert_dtypes()
    # 把dataframe的dtypes屬性轉換成純文字的series，可以選擇是否在轉換過程中，統一更名成sql模式的屬性名稱，或是不更名
    return df.dtypes.map(lambda x: x.name)


def TenPercentile_to_int(char, errors="raise", local="en_US.UTF-8"):
    # 可以把帶有逗號的文字用千分位的模式轉換成數字的功能，所以要先檢查輸入的char是否為數字，如果是的話就直接用tonumeric_int轉成數字送出去就好，如果不是的話才要進行下面的功能，進行千分位轉換，如果千分位也無法轉換，那這個就不是數字
    char = tonumeric_int(char)
    if isinstance(char, str) is False:
        return char
    locale.setlocale(locale.LC_ALL, local)
    
    try:
        return locale.atof(char)
    except ValueError:
        if errors == "raise":
            raise ValueError
        elif errors == "ignore":
            return char
        elif errors == "coerce":
            return None
    except:
        print("=====NEW ERROR=====\n{}\n=====NEW ERROR=====\n{}".format(sys.exc_info(), char))
        raise ValueError


def changetype_stringtodate(df=pd.DataFrame(), datecol=[], mode=1):
    # 分解有國字年月日的情況，例如93年4月12日
    def mode1(series):
        result = series.str.split("年|月|日", expand=True).rename(columns={0: "year", 1: "month", 2: "day"})
        if '年' not in result or '月' not in result or '日' not in result:
            return series
        result.loc[:, "year"] = (pd.to_numeric(result.loc[:, "year"], downcast="integer", errors='coerce') + 1911).astype(str)
        result = pd.to_datetime(result.loc[:, ["year", "month", "day"]], errors="coerce")
        return result

    # 例如9/82，就是民國82年9月的意思，把它變成1993-8-1，日期預設是1
    def mode2(series):
        series = series.str.split("-", expand=True).rename(columns={0: "month", 1: "year"}).reindex(columns=['year', 'month'])
        series = (pd.to_numeric(series.loc[:, "year"], downcast="float", errors="coerce") + 1911).astype(str).str.split(".", expand=True)[0] + "-" + series["month"]
        series = pd.to_datetime(series, errors="coerce")
        return series

    if mode == 1:
        df.loc[:, datecol] = df.loc[:, datecol].apply(lambda x: mode1(series=x))
    
    elif mode == 2:
        df.loc[:, datecol] = df.loc[:, datecol].apply(lambda x: mode2(series=x))
    # 例如82/4/12變成1993/4/12
    elif mode == 3:
        df.loc[:, datecol] = df.loc[:, datecol].apply(lambda x: x.str.zfill(9))
        df.loc[:, datecol] = df.loc[:, datecol].apply(lambda x: (pd.to_numeric(x.str.slice(stop=3), errors='coerce') + 1911).fillna("").astype(str).str.rsplit(r".", expand=True)[0] + x.str.slice(start=3))
        df.loc[:, datecol] = df.loc[:, datecol].apply(lambda x: pd.to_datetime(x, errors="coerce"))
    return df

def strtodate(x):
    # 0820412轉成1993/04/12
    if pd.isna(x) is True:
        return

    if 7>=len(x) >= 6:
        x = x.zfill(7)
    else:
        return

    d = x[-2:]
    m = x[-4:-2]
    y = str(int(x[:-4])+1911)

    res = pd.to_datetime("-".join([y,m,d]), errors="coerce")

    if pd.isna(res) is True:
        return
    else:
        return res.strftime("%Y/%m/%d")



def ChineseStr_bool( char ) :
    if re.sub("[^\u4e00-\u9fa5]", "" , char) == "" :
        return False
    else:
        return True


def numfromright( char ) :
# typ表示要返回文字的部分還是數字的部分，而和值的類型無關
    new = ""
    start_sign = "號"
    preserve_sign = "-之—"
    # stop_sign = "、,~ &?()/;+._'ˋ:∕。"
    # 從 "號" 開始收集往右的非漢字(包含數字和特殊符號),然後遇到漢字就停下來
    for _ in str( char )[ : : -1 ] :
        if new == "" :
            if _ in start_sign :
                new = _
        elif new != "" :
            if _ in preserve_sign :
                new = _ + new
            else :
                try :
                    new = str(int(_)) + new
                except :
                    break
    if new == "" or new in start_sign : return char
    # temp = new.maketrans( point_sign , "."*len( point_sign ) , start_sign )
    # new = new.translate( temp )
    # new = new.split(".")
    # if len(new) == 1 :
        # new = new[0]
    # elif len(new) > 1 :
        # new = "{}.{}".format( new[0] , "".join( new[ 1 : ] ) )
        
    # try :
    #     return float(new)
    # except:
    #     print(new)
    return new


adapter = {
    "unit" : {
        "零" : 1 ,
        "十" : 10,
        "百" : 100,
        "千" : 1000,
        "萬" : 10000,
        "億" : 100000000,
        "兆" : 1000000000000
        },
    "value" : {
        "一" : 1 ,
        "二" : 2 ,
        "三" : 3 ,
        "四" : 4 ,
        "五" : 5 ,
        "六" : 6 ,
        "七" : 7 ,
        "八" : 8 ,
        "九" : 9 ,
        }
    }