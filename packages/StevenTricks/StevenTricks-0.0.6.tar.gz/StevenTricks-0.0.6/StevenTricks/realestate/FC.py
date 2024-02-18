# -*- coding: utf-8 -*-
from sys import path
from os.path import dirname
# path.append( dirname( __file__ ) )
# path.append( "D:\GitHub" )
from itertools import product
from time import sleep
import requests as re


class webdata_crawl:
    def __init__(self, url, headers, payload, arg):
        self.url = url
        self.headers = headers
        self.payload = payload
        self.arg = arg
        
    def response_iter(self, timeout=1):
        # 因為有了payload和arg所以需要把request做成一個迭代器
        arg = product(*self.arg.values())
        for Arg in arg:
            print(Arg)
            page = 1
            while True:
                print(page)
                payload = self.payload.copy()
                payload['proptype'] = payload['proptype'].format(arg1=Arg[0])
                payload['saletype'] = payload['saletype'].format(arg2=Arg[1])
                payload['pageNum'] = payload['pageNum'].format(arg3=str(page))
                res = re.post(self.url, headers=self.headers, data=payload)
                if res.status_code != re.codes.ok:
                    print('status_code of response({}) is not equal to re.codes.ok({})\nProcess Stop !'.format(str(res.status_code), str(re.codes.ok)))
                    yield res
                res = res.json()
                if not res["data"]:
                    break
                yield res
                page += 1
                sleep(timeout)
        

# In[]

if __name__ == '__main__':
    pass
