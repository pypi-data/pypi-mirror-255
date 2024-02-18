# -*- coding: utf-8 -*-
# import sys
# sys.path

from StevenTricks import dbsqlite as db
from StevenTricks.fileop import PathWalk_df, xlstoxlsx, independentfilename
from StevenTricks.dfi import dfrows_iter
from StevenTricks.realestate.packet import Workdir, APfilename_dict
from StevenTricks.tracker import logmaker

from os.path import join, basename, splitext
from os import replace
from datetime import datetime, date
from time import sleep

import pandas as pd
import requests as re

if __name__ == '__main__':

    Workdir = Workdir()

    if Workdir.proj_dict['dir'] in ['Agent']:
        from StevenTricks.realestate.Ubee import webdata_crawl
        from StevenTricks.realestate.clean import Agent_input

        adm = next(Workdir.crosswalk_iter())
        log_series = Workdir.log_series()

        adm = adm.loc[:, ['ZIP', 'COUNTYCODE']]
        crawl = webdata_crawl(url=Workdir.proj_dict['url'], headers=Workdir.proj_dict['headers'], log=log_series)

        for webdata in crawl.response_iter(adm['ZIP'].unique().tolist(), 3):
            if isinstance(webdata, dict) is False:
                break
            df = pd.DataFrame(webdata['data'])
            df = Agent_input(df)
            df = pd.merge(df, adm, on=['ZIP'], how='left')
            log_series = pd.Series({'writetime': datetime.now(), 'writedate': date.today(), 'freq': 'month', 'totalpage': webdata['pager']['pages'], 'currentpage': webdata['pager']['page'], 'ZIP': webdata['ZIP'], 'type': Workdir.proj_dict['type']})
            for df_chunk in dfrows_iter(df, ['Created_DATE', 'COUNTYCODE'], db.sqltype_dict):
                db.tosqladapter_df(df_chunk[1], join(Workdir.path, Workdir.proj_dict['type'], df_chunk[0][0]+'.db'), df_chunk[0][1], 'price', ['Updated_DATE', 'AgentPrice', 'BUILD_FLRPRC'], ['title'], ['title', 'Updated_DATE'])
            db.tosql_df(log_series.to_frame().T, Workdir.logpath, Workdir.proj_dict['dir'], ['type', 'period'], True)
            print(log_series)

    elif Workdir.proj_dict['dir'] in ['ForeClosure']:
        from StevenTricks.realestate.FC import webdata_crawl
        from StevenTricks.realestate.clean import FC_input

        adm = next(Workdir.crosswalk_iter())

        if Workdir.proj_dict['type'] in ['WebData']:
            crawl = webdata_crawl(Workdir.proj_dict['url'], Workdir.proj_dict['headers'], Workdir.proj_dict['payload'], Workdir.proj_dict['arg'])
            adm = adm.loc[:, ['COUNTYNAME', 'COUNTYCODE', 'TOWNNAME', 'TOWNCODE']]

            for webdata in crawl.response_iter():
                if isinstance(webdata, dict) is False:
                    break
                df = pd.DataFrame(webdata['data'])
                df = FC_input(df)

                if 'COUNTYNAME' in df and 'TOWNNAME' in df:
                    df = pd.merge(df, adm, on=['COUNTYNAME', 'TOWNNAME'], how='left')
                    for df_chunk in dfrows_iter(df, ['DATE', 'COUNTYCODE']):
                        # 因為已經有saledate1這個欄位可以表示他的即將開拍日期，所以就不用把DATE放進nodrop欄位
                        db.tosql_df(df_chunk[1], join(Workdir.path, df_chunk[0][0] + '.db'), df_chunk[0][1], ['ID'])
                else:
                    for df_chunk in dfrows_iter(df, ['DATE', 'crtid']):
                        # 這個釋放動產的法拍，因為沒有COUNTYNAME和TOWNNAME所以用法院代號來區分
                        db.tosql_df(df_chunk[1], join(Workdir.path, '動產', df_chunk[0][0] + '.db'), df_chunk[0][1], ['ID'])
            db.conn.close()

        elif Workdir.proj_dict['type'] in ['pdf']:
            pdfdir_df = PathWalk_df(join(Workdir.path, 'pdf'))
            # 到負責裝有pdf檔案的資料夾裡面讀取現有的資料
            source_df = pd.concat(list(db.readsql_iter(Workdir.path)))
            # 把全部不動產的法拍資料一口氣讀進去
            source_df.loc[:, 'crm'] = source_df['crm'] + '.pdf'
            # 因為比較的對象有副檔名,這裡也要先把副檔名加進去
            source_df = source_df.loc[~source_df['crm'].isin(pdfdir_df['file'])]
            # 跟現有的pdf檔名做比對，比對完排除已經存在的檔名
            source_df = source_df.drop_duplicates(subset=['crm'])
            # 剩下的資料有些資料來源是來自同一個pdf檔名，所以要把剩下重複的檔名做去除重複的動作
            for url_pdf, filename in source_df[['filenm', 'crm']].values:
                url_pdf = Workdir.proj_dict['url'] + url_pdf
                response = re.get(url_pdf)
                with open(join(Workdir.path, 'pdf', filename), 'wb') as pdf:
                    for chunk in response.iter_content(chunk_size=1024):
                        pdf.write(chunk)
                print(filename)
                sleep(0.1)
        elif Workdir.proj_dict['func'] in ['NLP']:
            pass
            # with Pool() as pool:
            #     for res in pool.imap_unordered(text_parse, args_list):
            #         res = pd.DataFrame(res)
            #         print(res)

    elif Workdir.proj_dict['dir'] in ['ActualPrice']:
        # 不管是購買的還是下載免費的，都只能給副檔名是'.xls'的excel表
        from StevenTricks.realestate.clean import AP_input
        # adm = next(Workdir.crosswalk_iter())
        source_df = PathWalk_df(Workdir.source_path, fileinclude=['.xls'], level=1)
        for sourcepath in source_df['path']:
            print(sourcepath)
            # 對每一個.xlsm檔案做迭代，下面對整個excel表內的資料作統一整理
            filename_ext = basename(sourcepath)
            for vocab, county in APfilename_dict.items():
                if 'list_' + vocab in filename_ext or vocab + '_lvr' in filename_ext:
                    break
            #         利用for的方式找出vocab和county停在哪裡，就知道這個檔案是位於哪個區域
            # adm_std = dict(adm.loc[adm['COUNTYCODE'] == county, ['TOWNNAME', 'TOWNCODE']].values)
            # 取得該檔案所位於的county，並將adm鎖定在特定區域，取得adm_std
            df_dict = pd.read_excel(io=sourcepath, sheet_name=None)
            # df_dict = {_: AP_input(df_dict[_], _, filename_ext, adm_std) for _ in df_dict if
            #            _.split('_', 1)[0] not in ['歷次移轉明細'] and df_dict[_].empty is False}
            df_dict = {_: AP_input(df_dict[_], _, filename_ext) for _ in df_dict if _.split('_', 1)[0] not in ['歷次移轉明細'] and df_dict[_].empty is False}
            # 用pd.read_excel讀取檔案並對內容作資料清理，且排除'歷次移轉明細'，因為這個sheet不需要納入資料庫，如果資料本身是空的也排除
            df_dict = {_: df_dict[_] for _ in df_dict if df_dict[_] is not None}
            # 以上排除資料清理完是None的資料
            dfmain_dict = {_: df_dict.pop(_) for _ in [_ for _ in df_dict for main in ['不動產買賣', '預售屋買賣', '不動產租賃'] if main in _]}
            # 把主要sheet( '不動產買賣' , '預售屋買賣' , '不動產租賃' )分類在dfmain_dict，其餘附表分類在df_dict
            # 下方開始做個別的資料分類插入資料庫，先由主要資料表dfmain_dict開始插入，每插入一個主要資料表做迭代所有的附表，附表會先跟主要資料表做merge以確保該附表資料存在於主資料上
            pk = 'ID'
            for sheetmain in dfmain_dict:
                # 開始處理每一個主資料表
                Sheetmain = sheetmain.split('_', 1)[0]
                for dfmain_chunk in dfrows_iter(dfmain_dict[sheetmain], ['DATE'], db.sqltype_dict, ['DATE']):
                    db.tosql_df(dfmain_chunk[1], join(Workdir.path, Sheetmain, dfmain_chunk[0][0] + '.db'),  county, [pk])
                for sheet in df_dict:
                    # 開始處理每一個副資料表
                    sheettable = '{}_{}'.format(county, sheet.split('_', 1)[0])
                    df = pd.merge(df_dict[sheet], dfmain_dict[sheetmain].loc[:, [pk, 'DATE']], on=[pk], how='inner')
                    # 把主資料表和副資料表用ID連接在一起，為每個副資料表添加date，這樣才知道副資料表要放在哪個db裡面
                    df_dict[sheet] = df_dict[sheet].drop(df_dict[sheet].loc[df_dict[sheet][pk].isin(df[pk].unique())].index, axis=0)
                    # 把merge到的資料從原始資料drop掉，這樣下次merge的數量就會減少，也會減少dram空間占用
                    for df_chunk in dfrows_iter(df, ['DATE'], db.sqltype_dict):
                        # 因為都是針對已經存在的主資料表去merge，所以正常來講不用新增db也不會有db不存在的情況
                        db.tosql_df(df_chunk[1], join(Workdir.path, Sheetmain, df_chunk[0][0] + '.db'), sheettable, [pk], fktable=county, fk=[pk])
            replace(sourcepath, independentfilename(join(Workdir.used_path, filename_ext)))
            db.conn.close()

    elif Workdir.proj_dict['dir'] in ['Examin']:
        from StevenTricks.realestate.clean import Examin_input
        source_df = PathWalk_df(Workdir.source_path, level=0)
        for sourcepath in source_df['path']:
            filename_ext = basename(sourcepath)
            df_dict = pd.read_excel(io=sourcepath, sheet_name=None)
            df_dict = {key: Examin_input(df=df_dict[key], filename_ext=filename_ext) for key in df_dict if key.split('_', 1)[0] not in ['工作表1']}
            for sheet in df_dict:
                db.tosql_df(df_dict[sheet], join(Workdir.path, 'Examin.db'), sheet, ['ID'])
            replace(sourcepath, join(Workdir.used_path, filename_ext))
        db.conn.close()

    elif Workdir.proj_dict['dir'] in ['Valuer']:
        from StevenTricks.realestate.clean import Valuer_input

        if Workdir.proj_dict['type'] in ['all']:
            source_df = PathWalk_df(Workdir.source_path, fileexclude=['buy', 'full'])
            dbname = 'Valuer.db'

        elif Workdir.proj_dict['type'] in ['buy']:
            source_df = PathWalk_df(Workdir.source_path, fileinclude=['buy'])
            dbname = 'ValuerBuy.db'

        elif Workdir.proj_dict['type'] in ['full']:
            source_df = PathWalk_df(Workdir.source_path, fileinclude=['full'])
            dbname = 'ValuerFull.db'

        for sourcepath in source_df['path']:
            filename_ext = basename(sourcepath)
            if splitext(sourcepath)[1] == '.xls':
                sourcepath = xlstoxlsx(sourcepath)
                filename_ext = basename(sourcepath)
            # 找出路徑和附檔名，如果有xls就轉成excel的副檔名xlsx
            df_dict = pd.read_excel(sourcepath, sheet_name=None)
            # 把全部的sheet讀進dict

            # a = Valuer_input( df_dict['Sheet1'] , filename_ext )
            for sheet, df in df_dict.items():
                # 迭代每一個sheet，都做完事情之後，一個excel檔案才算是處理完成
                df = Valuer_input(df, filename_ext)
                for df_chunk in dfrows_iter(df, ['DATE'], db.sqltype_dict, ['DATE']):
                    db.tosql_df(df_chunk[1], join(Workdir.path, dbname), df_chunk[0][0], ['ID'])
            replace(sourcepath, join(Workdir.used_path, filename_ext))
        db.conn.close()

    elif Workdir.proj_dict['dir'] in ['GreenHouse']:
        from StevenTricks.realestate.clean import GH_input
        source_df = PathWalk_df(Workdir.source_path, level=0)

        adm = next(Workdir.crosswalk_iter())
        adm = adm.loc[:, ['COUNTYNAME', 'COUNTYCODE']].drop_duplicates(ignore_index=True)

        for sourcepath in source_df['path']:
            df = pd.read_excel(sourcepath, sheet_name='標章')
            df = GH_input(df)
            df = pd.merge(df, adm, on=['COUNTYNAME'], how='left').drop(labels=('COUNTYNAME'), axis=1)
            for df_chunk in dfrows_iter(df, ['COUNTYCODE'], db.sqltype_dict):
                db.tosql_df(df_chunk[1], join(Workdir.path, 'gh.db'), df_chunk[0][0], ['證號'])
                # 因為其他欄位，編號或書號會有None的情況，只有證號不會有空值，又具有唯一性
            replace(sourcepath, join(Workdir.used_path, basename(sourcepath)))
        db.conn.close()