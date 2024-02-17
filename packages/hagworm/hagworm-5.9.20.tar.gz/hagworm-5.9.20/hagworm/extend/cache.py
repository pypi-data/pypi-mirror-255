# -*- coding: utf-8 -*-

__author__ = r'wsb310@gmail.com'

import typing

from cachetools import TTLCache

from .base import Utils
from .transaction import Transaction


class StackCache:
    """堆栈缓存

    使用运行内存作为高速缓存，可有效提高并发的处理能力

    """

    def __init__(self, maxsize: float = 0xff, ttl: float = 60):

        self._cache: TTLCache = TTLCache(maxsize, ttl)

    def has(self, key: str) -> bool:

        return key in self._cache

    def get(self, key: str, default: typing.Any = None) -> typing.Any:

        return self._cache.get(key, default)

    def set(self, key: str, val: typing.Any):

        self._cache[key] = val

    def incr(self, key: str, val: float = 1) -> float:

        res = self.get(key, 0) + val

        self.set(key, res)

        return res

    def decr(self, key: str, val: float = 1) -> float:

        res = self.get(key, 0) - val

        self.set(key, res)

        return res

    def delete(self, key: str):

        del self._cache[key]

    def size(self) -> int:

        return len(self._cache)

    def clear(self):

        return self._cache.clear()


class PeriodCounter:

    def __init__(self, time_slice: float = 60, key_prefix: str = r'', maxsize: float = 0xffff):

        self._time_slice: float = time_slice
        self._key_prefix: str = key_prefix

        # 缓存对象初始化，key最小过期时间60秒
        self._cache: StackCache = StackCache(maxsize, time_slice)

    def _get_key(self, key: typing.Optional[str] = None) -> str:

        time_period = Utils.math.floor(Utils.timestamp() / self._time_slice)

        if key is None:
            return f'{self._key_prefix}_{time_period}'
        else:
            return f'{self._key_prefix}_{key}_{time_period}'

    def get(self, key: typing.Optional[str] = None) -> typing.Any:

        _key = self._get_key(key)

        return self._cache.get(_key, 0)

    def incr(self, val: float, key: typing.Optional[str] = None) -> float:

        _key = self._get_key(key)

        return self._cache.incr(_key, val)

    def incr_with_trx(self, val: float, key: typing.Optional[str] = None) -> typing.Tuple[float, Transaction]:

        _key = self._get_key(key)

        trx = Transaction()
        trx.add_rollback_callback(self._cache.decr, _key, val)

        return self._cache.incr(_key, val), trx

    def decr(self, val: float, key: typing.Optional[str] = None) -> float:

        _key = self._get_key(key)

        return self._cache.decr(_key, val)

    def decr_with_trx(self, val: float, key: typing.Optional[str] = None) -> typing.Tuple[float, Transaction]:

        _key = self._get_key(key)

        trx = Transaction()
        trx.add_rollback_callback(self._cache.incr, _key, val)

        return self._cache.decr(_key, val), trx
