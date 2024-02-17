import os as _os
import time as _time
from . import jsons as _json


class Cache:
    def __init__(self, cache_dir="cache"):
        self.cache_dir = cache_dir
        _os.makedirs(cache_dir, exist_ok=True)

    def get(self, key):
        # 获取缓存
        path = self._get_path(key)

        if _os.path.exists(path):
            with open(path, "r") as f:
                data = _json.load(f)
                if self._is_expired(data):
                    return None
                else:
                    return data["v"]
        else:
            return None

    def set(self, key, value, ttl=None):
        # 设置缓冲
        path = self._get_path(key)
        data = {"v": value, "c": _time.time(), "t": ttl}
        with open(path, "w") as f:
            _json.dump(data, f)

    def get_all(self):
        # 获取所有缓存
        all_data = {}
        for filename in _os.listdir(self.cache_dir):
            path = _os.path.join(self.cache_dir, filename)
            if _os.path.isfile(path) and filename.endswith(".json"):
                with open(path, "r") as f:
                    data = _json.load(f)
                    if not self._is_expired(data):
                        all_data[filename[:-5]] = data["v"]
        return all_data

    def delete(self, key):
        # 删除指定缓存
        path = self._get_path(key)
        if _os.path.exists(path):
            _os.remove(path)

    def delete_all(self):
        # 删除所有缓存
        for filename in _os.listdir(self.cache_dir):
            path = _os.path.join(self.cache_dir, filename)
            if _os.path.isfile(path) and filename.endswith(".json"):
                _os.remove(path)

    def _get_path(self, key):
        filename = "{}.json".format(key)
        path = _os.path.join(self.cache_dir, filename)
        return path

    def _is_expired(self, data):
        if data["t"] and _time.time() - data["c"] > data["t"]:
            return True
        elif not data["t"] and _time.time() - data["c"] > 60:
            return True
        else:
            return False
