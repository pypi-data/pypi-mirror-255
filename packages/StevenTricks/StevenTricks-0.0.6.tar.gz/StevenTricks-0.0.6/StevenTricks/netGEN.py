import requests as re

from traceback import format_exc
from StevenTricks.net import headers
from StevenTricks.dictur import randomitem


def randomheader():
    # 隨機產生header，是一個iter
    while True:
        yield {"User-Agent": randomitem(headers)[1]}


def safereturn(res,packet,jsoncheck=False):
    # 如果狀態碼不正確那也不用檢查json了
    # 不用返回packet是因為packet是dictionary，只要引用這個function，內部修改dictionary外面也會跟著連動，所以不用特地再去賦值
    packet['restatuscode']=res.status_code
    packet['restatuscode']=None
    if res.status_code!=re.codes.ok:
        packet["errormessage"] = '{} != {}'.format(str(res.status_code),str(re.codes.ok))
        return [None]

    if jsoncheck is True:
        try:
            jsontext = res.json()
        except:
            packet["errormessage"]=format_exc()
            return [None]
        return [jsontext]
    else:
        return [None]

