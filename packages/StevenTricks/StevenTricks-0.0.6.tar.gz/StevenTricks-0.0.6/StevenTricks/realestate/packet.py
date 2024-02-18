# -*- coding: utf-8 -*-
"""
Created on Mon Jan 17 15: 58: 55 2022

@author: 118939
"""

from StevenTricks.realestate.conf import db_path
from StevenTricks import dbsqlite as db
from os.path import join, isfile
from os import makedirs
from datetime import date

import logging

ProjectDict = {
    'Agent': {
        'crawl': {
            'crosswalk': ['adm'],
            'sell': {
                'url': 'https://service2.ubee.io/api/houses/sell?zip={z}&p={page}&n=1000&sort=updated_at%2Cdesc',
                'headers': {
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                                  'Chrome/99.0.4844.84 Safari/537.36 '
                    },
                },
            'rent': {
                'url': 'https://service2.ubee.io/api/houses/rent?zip={z}&p={page}&n=1000&sort=updated_at%2Cdesc',
                'headers': {
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                                  'Chrome/100.0.4896.60 Safari/537.36 '
                    },
                },
            },
        },
    'ForeClosure': {
        'crawl': {
            'crosswalk': ['adm'],
            'WebData': {
                'url': 'https://aomp109.judicial.gov.tw/judbp/wkw/WHD1A02/QUERY.htm',
                'headers': {
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                                  'Chrome/99.0.4844.82 Safari/537.36 '
                    },
                'payload': {
                    'gov': '',
                    'crtnm': '全部',
                    'court': '',
                    'COUNTY': '',
                    'town': '',
                    'proptype': '{arg1}',
                    'saletype': '{arg2}',
                    'keyword': '',
                    'saledate1': '',
                    'saledate2': '',
                    'minprice1': '',
                    'minprice2': '',
                    'saleno': '',
                    'crmyy': '',
                    'crmid': '',
                    'crmno': '',
                    'dpt': '',
                    'comm_yn': '',
                    'stopitem': '',
                    'sec': '',
                    'rrange': '',
                    'area1': '',
                    'area2': '',
                    'debtor': '',
                    'checkyn': '',
                    'emptyyn': '',
                    'ttitle': '',
                    'sorted_column': 'A.CRMYY, A.CRMID, A.CRMNO, A.SALENO, A.ROWID',
                    'sorted_type': 'ASC',
                    '_ORDER_BY': '',
                    'pageNum': '{arg3}',
                    'pageSize': '9999',
                        },
                'arg': {
                    'proptype': ['C51', 'C52', 'C54', 'C51C52', 'C103'],
                    'saletype': ['1', '4', '5']
                    }
                # key值須按照payload順序，由上到下
                },
            'pdf': {
                'url': r'https://aomp109.judicial.gov.tw/judbp/wkw/WHD1A02/DO_VIEWPDF.htm?filenm=',
                },
            },
        'NLP': {
            'cycledir': 'y',
            },
        },
    'ActualPrice': {
        'import': {
            'crosswalk': ['adm'],
            'cycledir': 'y',
            },
        },
    'Examin': {
        'import': {
            'cycledir': 'y',
            },
        },
    'Valuer': {
        'import': {
            'cycledir': 'y',
            'all': {
                },
            'buy': {
                },
            'full': {
                },
            },
        },
    'GreenHouse': {
        'import': {
            'crosswalk': ['adm', 'deptgroup'],
            'cycledir': 'y',
        }
    },
}


def dict_extractor(dic):
    # 從dic裡面分解出非dic和dic的資料
    res1, res2 = {}, {}
    while dic:
        tup = dic.popitem()
        if isinstance(tup[1], dict) is True:
            res1[tup[0]] = tup[1]
        else:
            res2[tup[0]] = tup[1]
    return res1, res2


def dict_enumkey(dic, start):
    return {n: k for n, k in enumerate({k: i for k, i in dic.items() if isinstance(i, dict) is True}, start)}


func_list = ['dir', 'func', 'type']


class Workdir:
    # log_series=pd.Series(dtype='object')
    logpath = join(db_path, 'log.db')
    proj_dict = dict.fromkeys(func_list, None)
    source_path = None
    # source_df = None
    used_path = None
    # dbname = None
    # source_path和used_path是根據self.path而來，self.path就是飲用db_path

    def __init__(self):
        num_dict = {}
        temp_dict = ProjectDict.copy()
        start = 1
        for key in func_list:
            num_dict = dict_enumkey(temp_dict, start)

            if len(num_dict) == 1:
                proj_int = start
            else:
                proj_int = int(input('\nSelect the {}\n{}\nEnter the number :'.format(key, '\n'.join(['{n}.{k}'.format(n=n, k=k) for n, k in num_dict.items()]))))

            if proj_int not in num_dict:
                # 只要輸入數字以外的數字就可以跳出循環，或是已經沒有選項可以選了
                print('{} not in the {}\nBreak the loop.'.format(str(proj_int), ','.join(num_dict.keys())))
                break
            else:
                # 有選到某個func的情況，先填入func的名稱
                self.proj_dict[key] = num_dict.get(proj_int)
                # 這時候才會進入篩選temp_dict，第一次進入篩選，一定是全部都是dict不會有dict以外的值，所以可以直接篩選
                temp_dict = temp_dict.get(num_dict.get(proj_int))
                # 篩選過後做分類，把dict分出來
                dictuple = dict_extractor(temp_dict)
                # [0]固定放dict，所以放給temp準備再進行第二輪的迴圈
                temp_dict = dictuple[0]
                # [1]固定放非dict
                self.proj_dict.update(dictuple[1])

                if not temp_dict:
                    # 如果篩選完發現已經沒有dict了，那就直接跳出loop
                    print('Picking is finished.')
                    break
        if temp_dict:
            # 如果實際的值小於func_list，那有可能再全部篩選前就提早結束，這時候temp_dict可能還會殘留一些值沒有取出，如果tmep_dict還有資料的話就全部把他放給proj_dict
            self.proj_dict.update(temp_dict)
        self.path = join(db_path, self.proj_dict['dir'])

        if self.proj_dict.get('cycledir') == 'y':
            self.source_path, self.used_path = join(self.path, 'source'), join(self.path, 'used')
            makedirs(self.source_path, exist_ok=True), makedirs(self.used_path, exist_ok=True)

    def crosswalk_iter(self):
        return db.readsql_iter(join(db_path, 'CrossWalk.db'), table_list=self.proj_dict.get('crosswalk', []))

    def log_series(self):
        if isfile(self.logpath) is False:
            print('Log.db is not existing.')
            return
        try:
            # 這裡的try是為了試出看有沒有這個log.db存在,如果不存在next()就會出錯自動跳下一步
            log_series = next(db.readsql_iter(self.logpath, table_list=[self.proj_dict['dir']]))
            # 如果log.db存在，且table也存在，那這裡會返回df否則引發錯誤中斷，log_series依然保持series格式
            log_series = log_series[(log_series['period'] == str(date.today()).rsplit('-', 1)[0]) & (log_series['type'] == self.proj_dict['type'])]
            # 這裡不論有沒有找到符合條件的紀錄log_series都會被轉換成df，但這裡不會出錯，有找到就是df沒找到也是df
            log_series = log_series.iloc[0]
            # 這裡會把上面的df轉換成series，如果上一行指令有成功找到紀錄，那這裡就不會引發紀錄，而是返回series，如果上一行指令沒有找到紀錄，那就會引發錯誤直接中斷
            # 這裡指定是0是因為db有設置pk的關係，所以正常情況下pk的資料不會重複，只會有一個，所以指定0就醫定只會有一個
            return log_series
        except StopIteration:
            print('Not the project need for log database !')
        except IndexError:
            print('There is log.db but the project type does not have the record in db')
        except:
            logging.error('Error of loading log path !', exc_info=True)


chnum_dict = {'': None, ' ': None, '二十': 20, '八': 8, '十九': 19, '十四': 14, '十': 10, '十三': 13, '四': 4, '五': 5, '二': 2, '九': 9, '七': 7, '三': 3, '二十三': 23, '二十四': 24, '十二': 12, '十五': 15, '二十九': 29, '二十二': 22, '一': 1, '十一': 11, '六': 6, '十八': 18, '十七': 17, '三十二': 32, '二十七': 27, '二十一': 21, '二十五': 25, '二十六': 26, '十六': 16, '二十八': 28, '三十': 30, '三十一': 31, '三十三': 33, '三十四': 34, '三十五': 35, '三十六': 36, '三十七': 37, '三十八': 38, '三十九': 39, '四十': 40, '四十一': 41, '四十二': 42, '四十三': 43, '四十四': 44, '四十五': 45, '四十六': 46, '四十七': 47, '四十八': 48, '四十九': 49, '五十': 50, '五十一': 51, '五十二': 52, '五十三': 53, '五十四': 54, '五十五': 55, '五十六': 56, '五十七': 57}

# 順序會影響判斷的結果
reasondict = {
    '合併戶': ['合併'],
    '關係人交易': ['親友', '親屬', '親', '家人', '二等', '關係', '鄰居'],
    '預售屋交易': ['預售'],
    '短期買賣': ['短', '急'],
    '偏遠區': ['C'],
    '買價低於區域行情': ['毛', '協', '債權', '債', '紅色', '紅', '警戳', '不良', '不佳', '瑕疵', '非', '壁刀', '沖', '陽', '平', '成本', '公設'],
    '增建及裝潢': ['增建', '登記', '頂', '蓋', '改建', '改良', '夾', '實品', '電', '露', '外推', '修正', '修', '回復', '裝潢', '家具', '傢', '俱', '贈送', '室內'],
    }


colname_dic = {
    'ActualPrice': {
        '土地位置/建物門牌': 'GUSTRE',
        '土地位置建物門牌': 'GUSTRE',
        '交易年月日': 'DATE',
        '租賃年月日': 'DATE',
        '總樓層數': 'STORY',
        '總層數': 'STORY',
        '移轉層次': 'Case_story',
        '建物分層': 'Case_story',
        '租賃層次': 'Case_story',
        '建物型態': 'BDTYPE_DETL',
        '屋齡': 'BuildingAge',
        '總價(元)': 'REALTY_SUMVAL',
        '總價元': 'REALTY_SUMVAL',
        '總額(元)': 'REALTY_SUMVAL',
        '總額元': 'REALTY_SUMVAL',
        '單價(元/平方公尺)': 'BUILD_FLRPRC',
        '單價元平方公尺': 'BUILD_FLRPRC',
        '車位總價(元)': 'STALLSUMVAL',
        '車位總價元': 'STALLSUMVAL',
        '車位價格': 'STALLSUMVAL',
        '車位總額元': 'STALLSUMVAL',
        '車位總額(元)': 'STALLSUMVAL',
        '建物移轉面積平方公尺': 'BUILDMSR',
        '建物移轉面積(平方公尺)': 'BUILDMSR',
        '建物移轉總面積(平方公尺)': 'BUILDMSR',
        '建物移轉總面積平方公尺': 'BUILDMSR',
        '建物總面積(平方公尺)': 'BUILDMSR',
        '建物總面積平方公尺': 'BUILDMSR',
        '主要用途': 'USESCOPE_DETL',
        '主要建材': 'MBM_DETL',
        '建築完成日期': 'FNSH_DATE',
        '建築完成年月': 'FNSH_DATE',
        '建案名稱': 'CASENM',
        '編號': 'ID',
        '車位類別': 'ParkingMode',
        '車位移轉總面積(平方公尺)': 'STALLMSR',
        '車位移轉總面積平方公尺': 'STALLMSR',
        '車位面積(平方公尺)': 'STALLMSR',
        '車位面積平方公尺': 'STALLMSR',
        '車位所在樓層': 'ParkingFloor',
        '鄉鎮市區': 'TOWNNAME',
        '土地移轉總面積(平方公尺)': 'LANDMSR',
        '土地移轉總面積平方公尺': 'LANDMSR',
        '土地移轉面積(平方公尺)': 'LANDMSR',
        '土地面積': 'LANDMSR',
        '土地面積平方公尺': 'LANDMSR',
        '土地面積(平方公尺)': 'LANDMSR',
        '建物現況格局-房': 'PART_RMCNT',
        '建物現況格局-廳': 'PART_HALLCNT',
        '建物現況格局-衛': 'PART_BHRMCNT',
        '建物現況格局-隔間': 'PART_COUNT',
        '有無管理組織': 'SecurityGuard',
        '有無備註欄(y/n)': '有無備註欄',
        '有無備註欄(Y/N)': '有無備註欄',
        '主建物面積': 'GUBUMSR',
        '陽台面積': 'MezzanineArea',
        '交易標的橫坐標': 'ADDRESS_X',
        '交易標的縱坐標': 'ADDRESS_Y',
        '都市土地使用分區': 'USE_SORT_DETL',
        '使用分區或編定': 'USE_SORT_DETL',
        '土地位置': 'PLSTRE',
        '地號': 'PLSTRENO',
        '權利人持分分母': 'HoldingDenominator',
        '權利人持分分子': 'HoldingNumerator',
        '移轉情形': 'TransactionType',
        '電梯': 'Elevator',
        '交易標的': 'TransactionSign',
        },
    'Examin': {
        '買賣日期': 'DATE',
        '買賣價': 'PriceExamin',
        '郵遞區號': 'ZIP',
        '地址': 'GUSTRE',
        '鄉鎮市區': 'TOWNNAME',
        '縣市': 'COUNTYNAME',
        '實價登錄金額': 'REALTY_SUMVAL',
        '實價登錄價格': 'REALTY_SUMVAL',
        '擔保品序號': 'GAGENO',
        '估價報告編號': 'CERPTNO',
        '績效行代號': 'AODEPTCODE'
        },
    'Valuer': {
        '社區案名': 'CASENM',
        '地址': 'GUSTRE',
        '完成年月': 'FNSH_DATE',
        '地坪': 'LANDMSR',
        '建坪': 'BUILDMSR',
        '屋簷雨遮': 'canopypin',
        '車位總坪數': 'STALLMSR',
        '建坪價(萬/坪)': 'BUILD_FLRPRC',
        '車位總價(萬)': 'STALLSUMVAL',
        '總價(萬)': 'PriceValuer',
        '修正原因': 'FIX_TYPE',
        '樓別/樓高': 'Floor',
        '用途': 'USESCOPE_DETL',
        '類別': 'BDTYPE_DETL',
        '加印原因': 'IMPRINT_RSN_DETL',
        '特殊擔保品': 'SPCGAGE_DETL',
        '核貸書買賣金額(萬)': 'PriceExamin',
        '核貸書購買日期': 'DateExamin',
        '修正前單價(萬)': 'BUILD_FIXPRC',
        '修正前總價(萬)': 'BUILD_FIXPRC2',
        '序號': 'GAGENO',
        '估價報告件號': 'CERPTNO',
        },
    'Agent': {
        'caseid': 'ID',
        'id': 'ID',
        'zip': 'ZIP',
        'address': 'GUSTRE',
        'bathroom': 'PART_BHRMCNT',
        'bedroom': 'PART_RMCNT',
        'livingroom': 'PART_HALLCNT',
        'land_area': 'LANDMSR',
        'mainarea': 'GUBUMSR',
        'main_building_area': 'GUBUMSR',
        'building_area': 'BUILDMSR',
        'regarea': 'BUILDMSR',
        'public_building_area': 'PublicMeasure',
        'room': 'PART_RMCNT',
        'casetypename': 'BDTYPE_DETL',
        'building_type': 'BDTYPE_DETL',
        'buildage': 'BuildingAge',
        'building_age': 'BuildingAge',
        'start_floor': 'LOW_STORY',
        'casefromfloor': 'LOW_STORY',
        'end_floor': 'HIGH_STORY',
        'casetofloor': 'HIGH_STORY',
        'total_floor': 'STORY',
        'unit_price': 'BUILD_FLRPRC',
        'price': 'AgentPrice',
        'mezzaninearea': 'MezzanineArea',
        'buildingname': 'CASENM',
        'community': 'CASENM',
        'parkingmode': 'ParkingMode',
        'longitude': 'ADDRESS_X',
        'latitude': 'ADDRESS_Y',
        'updated_at': 'Updated_DATE',
        'created_at': 'Created_DATE',
        'parking_info': 'ParkingMode',
        },
    'FC': {
        'rowid': 'ID',
        'crmyy': 'DATE_year',
        'saledate': 'DATE',
        'hsimun': 'COUNTYNAME',
        'ctmd': 'TOWNNAME',
        'budadd': 'GUSTRE',
        'sec': 'PLSTRENAME',
        'subsec': 'PLSTRESECTION',
        'landno': 'PLSTRENO',
        'crtnm': 'COURTNAME',
        'zip': 'ZIP'
        },
    'GH': {
        '年度.1': 'PAYEAR',
        '分區': 'region',
        '額件案別': 'OwnerType',
        '案件類別': 'OwnerType',
        '建築物名稱': 'CASENM',
        '建物地址': 'GUSTRE',
        '地面層總樓地板面積ｍ2': 'BUILDMSR',
        '分級評估': 'level',
        '縣市別': 'COUNTYNAME',
        '用途類建築別': 'USESCOPE_DETL',
        '證書效期': 'VALID_DATE',
        '續用/變更證號': '續用變更證號',
        }
    }


APfilename_dict = {
    'a': '63000',
    'b': '66000',
    'c': '10017',
    'd': '67000',
    'e': '64000',
    'f': '65000',
    'g': '10002',
    'h': '68000',
    'i': '10020',
    'j': '10004',
    'k': '10005',
    'm': '10008',
    'n': '10007',
    'o': '10018',
    'p': '10009',
    'q': '10010',
    't': '10013',
    'u': '10015',
    'v': '10014',
    'w': '9020',
    'x': '10016',
    'z': '9007',
    }


DATE_mode = {
    'ActualPrice': {
        '不動產買賣': 1,
        '不動產租賃': 1,
        '預售屋買賣': 1,
        '建物': 2,
        },
    'Valuer': 3,
    'Examin': 4,
    }

# 取代的順序會由上到下，例如上面已經做過'臺'>'台'，那dict下方的關鍵字就要從臺中縣改成台中縣，不然會找不到
ValueReplace_dict = {
    'COUNTYNAME': {
        '高雄市\(原高雄縣\)': '高雄市',
        '臺': '台',
        '巿': '市',
        },
    'TOWNNAME': {
        '臺': '台',
        '巿': '市',
        'fa72埔鄉': '鹽埔鄉',
        '金fa4b鄉': '金峰鄉',
        '金\x1bfa4b鄉': '金峰鄉',
        },
    'GUSTRE': {
        '臺南縣': '台南市',
        '臺北縣': '新北市',
        '臺中縣': '台中市',
        '高雄縣': '高雄市',
        '臺': '台',
        '巿': '市',
        },
    'COURTNAME': {
        '臺': '台',
        '－': '_',
        ' ': '',
        },
    'PAYEAR': {
        '年度': '',
        }
    }


Value_dict = {
    'COUNTYNAME': {
         '63000': ['台北市', '1'],
         '66000': ['台中市', '4'],
         '10017': ['基隆市', '9'],
         '67000': ['台南市', '6'],
         '64000': ['高雄市', '3'],
         '65000': ['新北市', '2'],
         '10002': ['宜蘭縣', '10'],
         '68000': ['桃園市', '5'],
         '10020': ['嘉義市', '14'],
         '10004': ['新竹縣', '8'],
         '10005': ['苗栗縣', '11'],
         '10008': ['南投縣', '13'],
         '10007': ['彰化縣', '12'],
         '10018': ['新竹市', '7'],
         '10009': ['雲林縣'],
         '10010': ['嘉義縣', '15'],
         '10013': ['屏東縣', '20'],
         '10015': ['花蓮縣', '21'],
         '10014': ['台東縣', '20'],
         '10016': ['澎湖縣', '17'],
         '9020': ['金門縣', '18'],
        },
    'BDTYPE_DETL': {
        '獨棟公寓': '獨棟公寓',
        '雙拼公寓': '雙拼公寓',
        '連棟公寓': ['連棟公寓', '公寓'],
        '集合式公寓': '集合式公寓',
        '電梯公寓': '電梯公寓',
        '連棟大樓': ['連棟大樓', '電梯大樓'],
        '雙拼大樓': '雙拼大樓',
        '集合式大樓': ['集合式大樓', '住宅大樓', '辦公商業大樓', '套房', '華廈', '廠辦'],
        '獨棟透天': ['獨棟透天', '倉庫', '工廠', '透天厝'],
        '雙拼透天': '雙拼透天',
        },
    'USESCOPE_DETL': {
        '住家用': ['國民住宅', '住家用', '整層住家', '住宅', '套房', '別墅'],
        '商業用': ['商業用', '辦公用', '辦公室', '辦公', '店舖', '店面'],
        '工業用': ['工業用', '廠房'],
        '住商用': ['住商用', '住辦'],
        '其他': '其他'
        },
    'MBM_DETL': {
        '鋼骨': ['鋼骨', '鋼骨混凝土造', '鋼骨造', '鋼骨構造', '鋼骨鋼筋混凝土', '鋼骨鋼筋混凝土造', '鋼骨鋼筋混凝土構造', '鋼骨鋼筋混凝土\(SRC\)', '鋼骨\(SC\)或鋼骨混凝土'],
        '鋼筋混凝土造': ['鋼筋混凝土', '鋼筋混凝土造', 'RC結構造', '鋼筋混凝土結構造', '鋼筋混凝土加強磚造'],
        '加強磚造': ['加強磚造' '加強磚構造', '加強磚造或其他建材'],
        '磚造': '磚造',
        '木造': '木造',
        '土石造': ['土石造', '土造', '土磚石混合造'],
        '其它': '其它',
        'RC加強磚造': 'RC加強磚造'
        },
    'ParkingMode': {
        '公設輪抽': ['電腦選號'],
        '一樓平面': ['一樓平面', '庭院']
        }
    }