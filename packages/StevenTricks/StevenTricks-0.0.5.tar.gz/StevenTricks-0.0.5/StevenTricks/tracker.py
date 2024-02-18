from os.path import exists, isfile, basename, dirname, isdir, splitext
from os import stat
from datetime import datetime, date
import pandas as pd


class PathSweeper:
    def __init__(self, path):
        self.path = path
        self.file_dir = None
        self.file = None
        self.file_exists = False
        self.file_dirname = None
        self.file_name = None
        self.file_ext = None
        self.file_bldg = None
        self.file_mod = None
        self.file_atime = None
        self.file_ctime = None
        self.file_mtime = None

        if exists(path) is True:
            if isfile(path) is True:
                temp_stat = stat(path)
                self.file_exists = True
                self.file = basename(path)
                self.file_dir = dirname(path)
                self.file_dirname = basename(self.file_dir)
                self.file_name, self.file_ext = splitext(self.file)
                self.file_atime = datetime.fromtimestamp(temp_stat.st_atime)
                self.file_ctime = datetime.fromtimestamp(temp_stat.st_ctime)
                self.file_mtime = datetime.fromtimestamp(temp_stat.st_mtime)
            elif isdir(path) is True:
                self.file_dir = path

    def report(self):
        # report in series type, because it could be convenient to concat with other series
        return pd.Series(self.__dict__)


def logmaker(write_dt, data_dt, log=pd.Series(dtype='object'),  period=None, index=None):
    # log就是額外想要加入的資訊，格式固定是series
    # write_dt就是寫入當下的時間點
    # data_dt就是資料的時間
    # period就是資料的更新週期，目前支援日、月、年
    # index就是項目的名字
    if period == "day":
        period = data_dt
    elif period == "month":
        period = str(data_dt).rsplit("-", 1)[0]
    elif period == "year":
        period = str(data_dt.year)
    return pd.concat([pd.Series({"write_dt": write_dt, "data_dt": data_dt, "period": period, "index": index}, dtype='object'),
                      log], axis=1).dropna(how="any", axis=1)


if __name__ == '__main__':
    pass