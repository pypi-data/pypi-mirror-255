# -*- coding: utf-8 -*-

from time import sleep
import requests as re
import pandas as pd

class webdata_crawl :
    def __init__( self , url , headers , log = pd.Series( ) ) :
        self.log = log
        self.url = url
        self.headers = headers
        
    def response_iter( self , zip_list , page = 0 , timeout = 1 ) :
        # 去迭代每一個zip裡面的page，直到page == total page，就跳下一個zip，直到全台灣的zip的都迭代完了之後才正式結束，以上是每個月該做的事，新的月份開始就重新做
        zip_list.sort()
        if self.log is not None :
            zip_list = zip_list[ zip_list.index( self.log['ZIP'] ) + 1 : ]
            page = self.log['currentpage']
        # 以上處理有沒有讀取到log的情況
        # 以下處理不管有沒有log都要做的事
        for zip_num in zip_list :
            page = 0
            while True :
                page += 1
                res = re.get( self.url.format( z = zip_num , page = page ) , headers = self.headers )
                if res.status_code != re.codes.ok :
                    print('status_code of response({}) is not equal to re.codes.ok({})\nProcess Stop !'.format( str(res.status_code) , str(re.codes.ok) ) )
                    yield res
                json = res.json()
                
                if not json['data'] : 
                    break
                else:
                    json['ZIP'] = zip_num
                    # 目的是把zip_num跟著json一起傳出去
                    yield json
                    if json['pager']['page'] >= json['pager']['pages'] : break
                sleep( timeout )
                
if __name__ =='__main__':
    pass
