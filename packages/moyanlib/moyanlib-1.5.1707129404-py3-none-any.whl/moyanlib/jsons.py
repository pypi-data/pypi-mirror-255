import importlib as _il
import os as _os
import pathlib as _pl
import pickle as _p
from moyanlib import system as _sy
from functools import lru_cache
import requests as _req

cachePath = _os.path.join(str(_pl.Path.home()), ".moyan")  # 缓存路径
if not _os.path.exists(_os.path.join(cachePath, "lib.json.pkl")):  # 判断缓存是否存在
    parserList = ["orjson", "ujson", "simdjson", "simplejson", "json"]  # 解析器列表
    parser5List = ["pyjson5", "json5"]  # json5解析器列表

    parserInfo = []  # 解析器信息
    for parser in parserList:  # 遍历列表
        # 尝试导入解析器
        try:
            v = _il.import_module(parser)
        except ImportError:
            pass
        else:
            parserInfo.append({"type": True, "name": parser})  # 保存至解析器信息列表
    # 缓存下来
    _os.makedirs(_os.path.join(cachePath), exist_ok=True)
    _p.dump(parserInfo, open(_os.path.join(cachePath, "lib.json.pkl"), "wb"))
else:
    # 加载缓存
    parserInfo = _p.load(open(_os.path.join(cachePath, "lib.json.pkl"), "rb"))


@lru_cache
def _getParser():
    # 获取解析器
    return _il.import_module(parserInfo[0]["name"])


def dump(obj, fp, indent=0, toacill=True):
    # 保存至文件
    return _getParser().dump(obj, fp, indent=indent, ensure_ascii=toacill)


def dumps(obj, indent=0, toacill=True):
    # 保存至str
    return _getParser().dumps(obj, indent=indent, ensure_ascii=toacill)


def load(fp):
    # 从文件加载
    return _getParser().load(fp)


def loads(data):
    # 从字符加载
    return _getParser().loads(data)


def dump_f(obj, path, *args, **xargs):
    # 从文件路径保存
    f = open(path, "w")
    return dump(obj, f, *args, **xargs)


def load_f(path):
    # 从文件路径加载
    f = open(path)
    return load(f)


def load_url(url, method, *args, **xargs):
    # 从url加载
    r = _req.request(method, url, *args, **xargs)
    return loads(r.text)


def cleanCache():
    # 清除缓存
    _sy.remove_file(_os.path.join(cachePath, "lib.json.pkl"))
