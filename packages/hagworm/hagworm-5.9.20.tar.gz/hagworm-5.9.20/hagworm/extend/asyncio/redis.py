# -*- coding: utf-8 -*-

__author__ = r'wsb310@gmail.com'

from abc import abstractmethod, ABC
from typing import Any, Union, Literal, Optional, Iterable, Tuple

from coredis import typing, Redis, RedisCluster
from coredis.recipes.locks import LuaLock as _LuaLock
from coredis.pool import ConnectionPool as _ConnectionPool, ClusterConnectionPool as _ClusterConnectionPool

from .base import Utils

from ..error import catch_error, catch_warning
from ..interface import AsyncContextManager
from .transaction import Transaction


class ConnectionPool(_ConnectionPool):

    @property
    def current_connections(self) -> int:
        return self._created_connections


class ClusterConnectionPool(_ClusterConnectionPool):

    @property
    def current_connections(self) -> int:
        return sum(self._created_connections_per_node.values())


class LuaLock(AsyncContextManager, _LuaLock):

    def __init__(
            self, client: Any, name: str,
            timeout: Optional[float] = None, sleep: float = 0.1,
            blocking: bool = True, blocking_timeout: Optional[float] = None
    ):
        _LuaLock.__init__(self, client, name, timeout, sleep, blocking, blocking_timeout)

    async def _context_release(self):
        with catch_warning():
            await self.release()

    async def acquire(self) -> bool:
        if self.local.get() is None:
            return await super().acquire()
        else:
            return await super().extend(self.timeout)

    async def release(self):
        if self.local.get() is not None:
            await super().release()


class _PoolMixin(ABC):

    connection_pool: Union[ConnectionPool, ClusterConnectionPool]

    def __init__(self, min_connections=0):

        self._name: str = Utils.uuid1()[:8]
        self._key_prefix: Optional[str] = None
        self._min_connections: int = min_connections if min_connections else 0

    @abstractmethod
    async def _init_connection(self):
        raise NotImplementedError()

    @abstractmethod
    async def get(self, *args, **kwargs):
        raise NotImplementedError()

    @abstractmethod
    async def getset(self, *args, **kwargs):
        raise NotImplementedError()

    @abstractmethod
    async def set(self, *args, **kwargs):
        raise NotImplementedError()

    @abstractmethod
    async def setex(self, *args, **kwargs):
        raise NotImplementedError()

    def set_key_prefix(self, value: str):

        self._key_prefix = value

    def get_safe_key(self, key, *args, **kwargs) -> str:

        if self._key_prefix:
            _key = f'{self._key_prefix}:{key}'
        else:
            _key = key

        if args or kwargs:
            _key = f'{_key}:{Utils.params_sign(*args, **kwargs)}'

        return _key

    async def close(self):

        self.connection_pool.disconnect()

    def allocate_lock(
            self, name: str,
            timeout: Optional[float] = None, sleep: float = 0.1,
            blocking: bool = True, blocking_timeout: Optional[float] = None
    ) -> LuaLock:

        return LuaLock(self, name, timeout, sleep, blocking, blocking_timeout)

    async def get_obj(self, name: str) -> Any:

        result = await self.get(name)

        return Utils.pickle_loads(result) if result else result

    async def getset_obj(self, name: str, value: Any) -> Any:

        _value = Utils.pickle_dumps(value)

        result = await self.getset(name, _value)

        return Utils.pickle_loads(result) if result else result

    async def set_obj(self, name: str, value: Any, seconds: Optional[float] = None):

        _value = Utils.pickle_dumps(value)

        if seconds is None:
            return await self.set(name, _value)
        else:
            return await self.setex(name, _value, seconds)


class RedisPool(Redis, _PoolMixin):
    """StrictRedis连接管理
    """

    connection_pool: ConnectionPool

    def __init__(
            self,
            host:str, port:int, db: int = 0,
            username: Optional[str] = None, password: Optional[str] = None,
            min_connections: int = 0, max_connections: int =32,
            max_idle_time: float = 43200, idle_check_interval: float = 1,
            protocol_version: Literal[2, 3] = 2,
            **kwargs
    ):

        Redis.__init__(
            self,
            host, port, db,
            username=username, password=password, max_connections=max_connections,
            max_idle_time=max_idle_time, idle_check_interval=idle_check_interval,
            protocol_version=protocol_version, connection_pool_cls=ConnectionPool,
            **kwargs
        )

        _PoolMixin.__init__(self, min(min_connections, max_connections))

    async def _init_connection(self):

        connections = []

        with catch_error():
            for _ in range(self._min_connections):
                connection = await self.connection_pool.get_connection()
                connections.append(connection)

        with catch_error():
            for connection in connections:
                self.connection_pool.release(connection)

    async def initialize(self):

        await self._init_connection()

        config = self.connection_pool.connection_kwargs

        Utils.log.info(
            f"Redis Pool ({self._name}) [{config[r'host']}:{config[r'port']}] initialized: "
            f"{self.connection_pool.current_connections}/{self.connection_pool.max_connections}"
        )

        return self


class RedisClusterPool(RedisCluster, _PoolMixin):
    """StrictRedisCluster连接管理
    """

    connection_pool: ClusterConnectionPool

    def __init__(
            self,
            host: str, port: int, startup_nodes: Optional[Iterable[typing.Node]] = None,
            username: Optional[str] = None, password: Optional[str] = None,
            min_connections: int = 0, max_connections: int = 32,
            max_idle_time: float = 43200, idle_check_interval: float = 1,
            protocol_version: Literal[2, 3] = 2,
            **kwargs
    ):

        RedisCluster.__init__(
            self,
            host, port, startup_nodes=startup_nodes,
            username=username, password=password, max_connections=max_connections,
            max_idle_time=max_idle_time, idle_check_interval=idle_check_interval,
            protocol_version=protocol_version, connection_pool_cls=ClusterConnectionPool,
            **kwargs
        )

        _PoolMixin.__init__(self, min(min_connections, max_connections))

    async def _init_connection(self):

        connections = []

        with catch_error():
            for _ in range(self._min_connections):
                connection = await self.connection_pool.get_connection_by_key(Utils.uuid1())
                connections.append(connection)

        with catch_error():
            for connection in connections:
                self.connection_pool.release(connection)

    async def initialize(self):

        await self.connection_pool.initialize()

        await self._init_connection()

        nodes = self.connection_pool.nodes.nodes

        Utils.log.info(
            f"Redis Cluster Pool ({self._name}) {list(nodes.keys())} initialized: "
            f"{self.connection_pool.current_connections}/{self.connection_pool.max_connections}"
        )

        return self


class RedisDelegate:
    """Redis功能组件
    """

    def __init__(self):

        self._redis_pool: Optional[RedisPool, RedisClusterPool] = None

    @property
    def redis_pool(self) -> Union[RedisPool, RedisClusterPool]:

        return self._redis_pool

    async def init_redis_single(
            self,
            host:str, port:int, db: int = 0,
            username: Optional[str] = None, password: Optional[str] = None, *,
            min_connections: int = 0, max_connections: int =32,
            max_idle_time: float = 43200, idle_check_interval: float = 1,
            protocol_version: Literal[2, 3] = 2,
            **kwargs
    ):

        self._redis_pool = await RedisPool(
            host, port, db, username, password,
            min_connections, max_connections,
            max_idle_time, idle_check_interval,
            protocol_version,
            **kwargs
        ).initialize()

        return self._redis_pool

    async def init_redis_cluster(
            self,
            host: str, port: int, startup_nodes: Optional[Iterable[typing.Node]] = None,
            username: Optional[str] = None, password: Optional[str] = None, *,
            min_connections: int = 0, max_connections: int = 32,
            max_idle_time: float = 43200, idle_check_interval: float = 1,
            protocol_version: Literal[2, 3] = 2,
            **kwargs
    ):

        self._redis_pool = await RedisClusterPool(
            host, port, startup_nodes, username, password,
            min_connections, max_connections,
            max_idle_time, idle_check_interval,
            protocol_version,
            **kwargs
        ).initialize()

        return self._redis_pool

    def set_redis_key_prefix(self, value: str):

        self._redis_pool.set_key_prefix(value)

    async def close_redis_pool(self):

        await self._redis_pool.close()

    def get_redis_client(self) -> Union[RedisPool, RedisClusterPool]:

        return self._redis_pool


class ShareCache(AsyncContextManager):
    """共享缓存，使用with进行上下文管理

    基于分布式锁实现的一个缓存共享逻辑，保证在分布式环境下，同一时刻业务逻辑只执行一次，其运行结果会通过缓存被共享

    """

    def __init__(
            self, redis_client: Union[RedisPool, RedisClusterPool], share_key: str,
            lock_timeout: float = 60, lock_blocking_timeout: float = 60
    ):

        self._redis_client: Union[RedisPool, RedisClusterPool] = redis_client
        self._share_key: str = redis_client.get_safe_key(share_key)

        self._lock: LuaLock = self._redis_client.allocate_lock(
            redis_client.get_safe_key(f'share_cache:{share_key}'),
            timeout=lock_timeout, blocking=True, blocking_timeout=lock_blocking_timeout
        )

        self.result = None

    async def _context_release(self):

        await self.release()

    async def get(self) -> Any:

        result = await self._redis_client.get_obj(self._share_key)

        if result is None:

            if await self._lock.acquire():
                result = await self._redis_client.get_obj(self._share_key)

        return result

    async def set(self, value: Any, expire: Optional[float] = None):

        return await self._redis_client.set_obj(self._share_key, value, expire)

    async def release(self):

        if self._lock:
            await self._lock.release()

        self._redis_client = self._lock = None


class PeriodCounter:

    MIN_EXPIRE = 60

    def __init__(self, redis_client: Union[RedisPool, RedisClusterPool], key_prefix: str, time_slice: int):

        self._redis_client: Union[RedisPool, RedisClusterPool] = redis_client

        self._key_prefix = key_prefix
        self._time_slice = time_slice

    def _get_key(self) -> str:

        time_period = Utils.math.floor(Utils.timestamp() / self._time_slice)

        return self._redis_client.get_safe_key(f'{self._key_prefix}:{time_period}')

    async def _execute(self, key: str, val: int) -> int:

        async with await self._redis_client.pipeline(transaction=False) as pipeline:

            await pipeline.incrby(key, val)
            await pipeline.expire(key, max(self._time_slice, self.MIN_EXPIRE))

            res, _ = await pipeline.execute()

            return res

    async def incr(self, val: int = 1):

        return await self._execute(self._get_key(), val)

    async def incr_with_trx(self, val: int = 1) -> Tuple[int, Transaction]:

        _key = self._get_key()

        res = await self._execute(_key, val)

        if res is not None:
            trx = Transaction()
            trx.add_rollback_callback(self._execute, _key, -val)
        else:
            trx = None

        return res, trx

    async def decr(self, val: int = 1) -> int:

        return await self._execute(self._get_key(), -val)

    async def decr_with_trx(self, val: int = 1) -> Tuple[int, Transaction]:

        _key = self._get_key()

        res = await self._execute(_key, -val)

        if res is not None:
            trx = Transaction()
            trx.add_rollback_callback(self._execute, _key, val)
        else:
            trx = None

        return res, trx
