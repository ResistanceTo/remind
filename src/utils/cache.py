import time


class Cache:

    _data = dict()
    _max_time = 60 * 10

    @classmethod
    def set(cls, key, value, max_time=None):
        cls._data[key] = value
        cls._data[f"{key}_time"] = time.time()
        if max_time == None:
            cls._data[f"{key}_max_time"] = cls._max_time
        else:
            cls._data[f"{key}_max_time"] = max_time

    @classmethod
    def get(cls, key):
        if cls._data.get(key) == None:
            return None
        if time.time() - cls._data[f"{key}_time"] > cls._data[f"{key}_max_time"]:
            del cls._data[key]
            del cls._data[f"{key}_time"]
            del cls._data[f"{key}_max_time"]
            return None
        else:
            return cls._data[key]

    @classmethod
    def set_max_time(cls, max_time):
        if isinstance(max_time, (int, float)):
            cls._max_time = max_time
        else:
            raise ValueError


cache = Cache
