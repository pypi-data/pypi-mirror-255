
from typing import Callable as _Callable
from time import perf_counter as _perf_counter
from simpleworkspace.types.time import TimeSpan as _TimeSpan

class MemoryCache:
    def __init__(self) -> None:
        self._cache = {}

    def Get(self, key: str, default=None):
        if(key not in self._cache):
            return default
        
        if(self._CacheObject_HasExpired(self._cache[key])):
            if("ValueGenerator" in self._cache[key]):
                self._CacheObject_GenerateValue(self._cache[key])
            else:
                del self._cache[key]
                return default
            
        return self._cache[key]["Value"]
        
    def Set(self, key:str, value=None, valueGenerator:_Callable=None, TTL:_TimeSpan=None):
        """
        :param valueGenerator: when a value generator is used, the callback is used to initialize and reset the value of the cache once expired
        :param TTL: time until cache expires, leave null for permanent
        """

        cacheObj = {
            "Value": value,
            "ValueTime": _perf_counter(),
        }
        if(TTL is not None):
            cacheObj["TTL"] = TTL.InSeconds()
        if(valueGenerator is not None):
            cacheObj["Value"] = valueGenerator()
            cacheObj["ValueGenerator"] = valueGenerator
        
        self._cache[key] = cacheObj


    def Remove(self, key:str):
        if (key in self._cache):
            del self._cache[key]

    def Clear(self):
        self._cache.clear()
    
    def _CacheObject_HasExpired(self, cacheObj:dict):
        if("TTL" not in cacheObj):
            return False
        if(_perf_counter() > cacheObj["TTL"] + cacheObj["ValueTime"]):
            return True
        return False

    def _CacheObject_GenerateValue(self, cacheObj:dict):
        cacheObj["Value"] = cacheObj["ValueGenerator"]()
        cacheObj["ValueTime"] = _perf_counter()