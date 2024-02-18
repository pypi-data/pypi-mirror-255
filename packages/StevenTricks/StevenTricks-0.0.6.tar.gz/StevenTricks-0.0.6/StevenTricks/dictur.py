from random import randint
import re


def indexkey(dic, index):
    n = 0
    for key in dic:
        if n == index:
            return dic[key]
        n += 1
    print('index <{}> is out of index. the dic size is {}'.format(str(index), str(n)))


def findstr(dic, text):
    # text可以用|分隔，來達到多條件搜尋，搜尋結果有可能是兩個以上，就會用list返回，如果找不到就返回空的list
    res = []
    for key in dic:
        if re.search(text, key):
            res.append(key)
    return res


def randomitem(dic):
    key = list(dic.keys())[randint(0, len(dic)-1)]
    return key, dic[key]


def flat(dic):
    # 把字典裡的value，如果是list的話就全部展開，變成key值，如果不是list的話，就只是把value和key顛倒而已
    res = {}
    for key, value in dic.items():
        if isinstance(value, list) is True:
            res.update(dict.fromkeys(value, key))
        else:
            res[value] = key
    return res


def stack(dic):
    # 把有相同value的key值，全部把value當作key值，收攏每一個key值到list，是flat_dict的反向操作
    res = {}
    for key, value in dic.items():
        if value not in res:
            res[value] = []
        res[value].append(key)
    return res


def renamekey(dic, replacedic={}, error='coerce'):
    # replacedic = { oldkey : newkey}
    # error 可以是 coerce就是沒有這個key就給一個None，ignore意思就是沒有這個key就什麼都不做
    for key in replacedic:
        if replacedic[key] not in dic:
            if error == 'coerce':
                dic[replacedic[key]] = None
            elif error == 'ignore':
                pass
            continue
        dic[key] = dic.pop(replacedic[key])
    return dic
