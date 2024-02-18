# -*- coding: utf-8 -*-
"""
Created on Tue Apr 26 15:53:48 2022

@author: 118939
"""

import pandas as pd
from os import makedirs, walk, remove
from os.path import exists, pardir, abspath, isfile, samefile, join, splitext, dirname, basename
# from sys import platform
import pickle


def filename(path):
    return basename(splitext(path)[0])


def picklesave(data, path):
    # path要精確到檔名
    makedirs(abspath(dirname(path)), exist_ok=True)
    with open(path, 'wb') as f:
        pickle.dump(data, f)


def pickleload(path):
    # path要精確到檔名
    with open(path, 'rb') as f:
        data = pickle.load(f)
        return data


def warehouseinit(path):
    # 會產生兩個資料夾，source和cleaned，都放在warehouse底下
    source, cleaned = join(path, 'source'), join(path, 'cleaned')
    makedirs(source, exist_ok=True), makedirs(cleaned, exist_ok=True)


def xlstoxlsx(path):
    newpath = splitext(path)[0] + '.xlsx'
    with pd.ExcelWriter(newpath) as writer:
        for df in pd.read_html(path, header=0):
            df.to_excel(writer, index=False)
    remove(path)
    return newpath


def independentfilename(root, mark="_duplicated", count=1):
    if exists(root) is True:
        ext = splitext(root)[1]
        root = splitext(root)[0]
        if mark in root:
            rootsplit = root.split(mark)
            root = rootsplit.pop(0)
            if rootsplit:
                count = int(rootsplit.pop(0)) + 1

        root += mark + str(count) + ext
        if exists(root) is True:
            root = independentfilename(root)
    return root

# independentfilename(r'/Users/stevenhsu/Library/Mobile Documents/com~apple~CloudDocs/warehouse/ActualPrice/used/a_lvr_land_a.xls')


def pathlevel(left, right):
    if isfile(right) is True:
        right = abspath(join(right, pardir))
    if len(left) > len(right):
        return
    level = 0
    while not samefile(left, right):
        right = abspath(join(right, pardir))
        level += 1
    return level


def PathWalk_df(path, dirinclude=[], direxclude=[], fileexclude=[], fileinclude=[], level=None):
    res = []
    for _path, dire, file in walk(path):
        if not dire and not file:
            res.append([None, path])
        for f in file:
            res.append([f, join(_path, f)])
        
    res = pd.DataFrame(res, columns=["file", "path"])
    res.loc[:, 'level'] = res['path'].map(lambda x: pathlevel(path, x))
    if level is not None:
        res = res.loc[res['level'] <= level]
    
    res = res.loc[res["path"].str.contains("\\|\\".join(dirinclude), na=False)]
    if direxclude:
        res = res.loc[~(res["path"].str.contains("\\|\\".join(direxclude), na=True))]
    res = res.loc[res.loc[:, "file"].str.contains("|".join(fileinclude), na=False)]
    if fileexclude:
        res = res.loc[~(res.loc[:, "file"].str.contains("|".join(fileexclude), na=True))]
    return res.reset_index(drop=True)

# PathWalk_df(r'/Users/stevenhsu/Library/Mobile Documents/com~apple~CloudDocs/warehouse/stock/source', fileinclude=['.pkl'], fileexclude=['log'])


def logfromfolder(path, fileinclude, fileexclude, direxclude, dirinclude, log, fillval, avoid=[]):
    # avoid 是list形式，就是如果要填寫的地方已經存在avoid裡面的值，就避開，不要覆蓋到
    # fileinclude and fileexclude should be []
    # 標準檔名是col_yyyy-mm-dd.pkl所以用_可以拆分出col和date
    # fillval就是在如果找到檔案的情況下要在log填入什麼值，因為有找到檔案，所以是填入succeed
    # 因為是從檔名分解出col和ind，所以檔名決定log的col複雜度
    pathdf = PathWalk_df(path=path, fileinclude=fileinclude, fileexclude=fileexclude, direxclude=direxclude, dirinclude=dirinclude)
    for name in pathdf['file']:
        col = name.split('_')[0]
        ind = name.split('_')[1].split('.')[0]

        if col in log and ind in log.index:
            # 如果值有存在的話就考慮有沒有在avoid裏面
            if log.loc[ind, col] in avoid:
                # 在avoid裏面就直接跳過
                continue
            else:
                log.loc[ind, col] = fillval
                # 不在avoid裏面就直接覆蓋
        else:
            # 值不存在的話就直接新增
            log.loc[ind, col] = fillval
    return log
