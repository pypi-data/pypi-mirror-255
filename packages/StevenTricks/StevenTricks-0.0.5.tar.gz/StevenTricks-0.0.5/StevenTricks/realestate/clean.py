# -*- coding: utf-8 -*-

from StevenTricks.snt import tonumeric_int, changetype_stringtodate
from StevenTricks.dfi import replace_series
from StevenTricks.dictur import flat
from StevenTricks.realestate.packet import colname_dic, DATE_mode, ValueReplace_dict, chnum_dict, Value_dict

from os.path import splitext

import unicodedata
import pandas as pd

# def test(s):
#     s=s.dropna()
#     s=pd.to_datetime(s)
#     print(s)
#     return s
# t1 = pd.DataFrame([[1], [3, '2011/3/1'], [5, '2021/6/6']], columns=['tt', 'te'])
# t1.loc[:, ['te']] = t1.loc[:, ['te']].apply(lambda x: test(x))

def story_clean(text):
    text = tonumeric_int(text)
    if isinstance(text, str) is False:
        return text
    text = text.split(',')
    text = [_ for _ in text if '層' in _ or '全' == _]
    if '全' in text:
        return '全'
    text = [_.replace('層', '').replace('地下層', 'B1').replace('地下', 'B') for _ in text if _ != '全' ]
    text = ['B' + str(chnum_dict.get(_.split('B')[1], _.split('B')[1])) if 'B' in _ else str(chnum_dict.get(_, _) ) for _ in text]
    return ','.join(text)
    

def Agent_input(df):
    df.columns = [str.lower(i) for i in df.columns.tolist()]
    df = df.rename(columns=colname_dic['Agent'])
    templist = [_ for _ in ['Updated_DATE', 'Created_DATE'] if _ in df]
    df.loc[:, templist] = df.loc[:, templist].apply(lambda x: pd.to_datetime(x, errors='coerce'))
    df = df.replace(ValueReplace_dict, regex=True)
    
    if 'BDTYPE_DETL' in df:
        if 'USESCOPE_DETL' in df:
            df.loc[:, 'BDTYPE_DETL'] = df['BDTYPE_DETL'] + ',' + df['USESCOPE_DETL']
        df.loc[:, 'BDTYPE_DETL'] = df['BDTYPE_DETL'].replace(flat(Value_dict['BDTYPE_DETL']), regex=True)
    return df

# def AP_input(df, sheet, filename_ext, adm_std):


def AP_input(df, sheet, filename_ext):
    print('<FileName>{}<SheetName>{}'.format(filename_ext, sheet))
    sheet = sheet.split('_', 1)[0]
    if 'lvr' in filename_ext:
        df = df.drop(0)
    df = df.drop(['Unnamed: 35'], axis=1, errors='ignore')
    df = df.rename(columns=colname_dic['ActualPrice'])
    templist = [_ for _ in ['Case_story', 'GUSTRE', 'PLSTRE'] if _ in df]
    df.loc[:, templist] = df.loc[:, templist].applymap(lambda x: unicodedata.normalize('NFKC', str(x)))
    
    if sheet in ['不動產買賣', '預售屋買賣', '不動產租賃']:
        df.insert(0, 'FileName', splitext(filename_ext)[0])
        df = df.replace(ValueReplace_dict, regex=True)
        # df.loc[:, 'TOWNCODE'] = df.loc[:, 'TOWNNAME'].map(lambda x: adm_std[x] if pd.isnull(x) is False else x)
        # df.loc[df['TOWNNAME'].isnull(), 'TOWNCODE'] = replace_series(series=df.loc[df['TOWNNAME'].isnull(), 'GUSTRE'], std_dict=adm_std, mode='exac')
        # df = df.drop(['TOWNNAME'], axis=1, errors='ignore')
    
    if sheet in DATE_mode['ActualPrice']:
        templist = [_ for _ in ['DATE', 'FNSH_DATE'] if _ in df]
        df = changetype_stringtodate(df=df, datecol=templist, mode=DATE_mode['ActualPrice'][sheet])
    templist = [_ for _ in ['BUILD_FLRPRC', 'REALTY_SUMVAL', 'BUILDMSR', 'STALLMSR', '主建物面積', '附屬建物面積', '陽台面積'] if _ in df]
    df.loc[:, templist] = df.loc[:, templist].apply(lambda x : pd.to_numeric(x, downcast='float', errors='coerce'))
    
    templist = [_ for _ in ['BUILDMSR', 'STALLMSR', '主建物面積', '附屬建物面積', '陽台面積'] if _ in df]
    df.loc[:, templist] = df.loc[:, templist].apply(lambda x: x*.3025)
    templist = [_ for _ in ['BUILD_FLRPRC'] if _ in df]
    df.loc[:, templist] = df.loc[:, templist].apply(lambda x: x/0.3025/10000)
    templist = [_ for _ in ['REALTY_SUMVAL'] if _ in df]
    df.loc[:, templist] = df.loc[:, templist].apply(lambda x: x/10000)
    templist = [_ for _ in ['STORY', 'Case_story'] if _ in df]
    df.loc[:, templist] = df.loc[:, templist].applymap(lambda x: story_clean(x))
    return df


def Valuer_input(df, filename_ext):
    print('<FileName>{}'.format(filename_ext))
    df = df.rename(columns=colname_dic['Valuer'])
    df.loc[:, 'GUSTRE'] = df.loc[:, 'GUSTRE'].map(lambda x: unicodedata.normalize('NFKC', str(x)))
    df.loc[:, 'GAGENO'] = df['GAGENO'].fillna(1)
    df.loc[:, ['CERPTNO', 'GAGENO']] = df[['CERPTNO', 'GAGENO']].astype(str)
    df.loc[:, 'ID'] = df['CERPTNO'].str.strip().str.zfill(15) + df['GAGENO'].str.split('.', expand=True)[0]
    df = df.replace(ValueReplace_dict, regex=True)
    df = changetype_stringtodate(df=df, datecol=['FNSH_DATE'], mode=DATE_mode['Valuer'])
    df.loc[:, 'DateExamin'] = pd.to_datetime(df['DateExamin'].astype(str).str.rsplit('.', expand=True)[0], errors='coerce')
    df.loc[:, 'DATE'] = pd.to_datetime(df['ID'].str.slice(start=5, stop=11) + '01', errors='coerce')
    df.insert(0, 'FileName', splitext(filename_ext)[0])
    return df


def Examin_input(df, filename_ext):
    print('<FileName>{}'.format(filename_ext))
    df = df.rename(columns=colname_dic['Examin'])
    df = df.reset_index().rename(columns={'index': 'Sequence'})
    df = df.replace(ValueReplace_dict, regex=True)
    df.loc[:, 'GUSTRE'] = df.loc[:, 'GUSTRE'].map(lambda x: unicodedata.normalize('NFKC', str(x)))
    df.loc[:, 'DATE'] = pd.to_datetime(df['DATE'].astype(str).str.rsplit('.', expand=True)[0], errors='coerce')
    df.loc[:, 'ID'] = df['CERPTNO'].str.strip().str.zfill(15) + df['GAGENO'].fillna(1).astype(str).str.split('.', expand=True)[0]
    df.loc[:, 'PriceExamin'] = df['PriceExamin']/10000
    df.insert(0, 'FileName', splitext(filename_ext)[0])
    return df


def FC_input(df):
    df = df.rename(columns=colname_dic['FC'])
    df = df.replace(ValueReplace_dict, regex=True)
    df.loc[:, 'DATE'] = (pd.to_numeric(df['DATE'].str.slice(stop=3), errors='coerce') + 1911).astype(str).str.rsplit('.', expand=True)[0] + df['DATE'].str.slice(start=3)
    df.loc[:, 'DATE'] = pd.to_datetime(df['DATE'], errors='coerce')
    return df


def GH_input(df):
    df = df.drop_duplicates()
    df = df.rename(columns=colname_dic['GH'])
    df = df.replace(ValueReplace_dict, regex=True)
    df = df.drop(['年度', '編號.1'], axis=1, errors='ignore')
    df.loc[:, 'BUILDMSR'] = pd.to_numeric(df['BUILDMSR'], downcast='float', errors='coerce')*.3025
    df.loc[:, 'VALID_DATE'] = pd.to_datetime(df['VALID_DATE'], errors='coerce')
    return df
    

if __name__ == '__main__':
    pass
