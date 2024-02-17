# -*- coding: utf-8 -*-

__author__ = r'wsb310@gmail.com'

import types
import typing
import weakref
import inspect
import asyncio
import functools

import async_timeout

from abc import ABCMeta, abstractmethod
from contextlib import asynccontextmanager
from contextvars import Context, ContextVar, Token

from .. import base
from ..error import catch_error
from ..cache import StackCache


def install_uvloop():
    """尝试安装uvloop
    """

    try:
        import uvloop
    except ModuleNotFoundError:
        Utils.log.warning(f'uvloop is not supported (T＿T)')
    else:
        uvloop.install()
        Utils.log.info(f'uvloop {uvloop.__version__} installed')


class Utils(base.Utils):
    """异步基础工具类

    集成常用的异步工具函数

    """

    sleep = staticmethod(asyncio.sleep)

    @staticmethod
    def is_coroutine_function(func: typing.Callable) -> bool:

        if isinstance(func, functools.partial):
            return asyncio.iscoroutinefunction(func.func)
        else:
            return asyncio.iscoroutinefunction(func)

    @staticmethod
    async def awaitable_wrapper(obj: typing.Any) -> typing.Any:
        """自适应awaitable对象
        """

        if inspect.isawaitable(obj):
            return await obj
        else:
            return obj

    @staticmethod
    @types.coroutine
    def wait_frame(count: int = 10):
        """暂停指定帧数
        """

        for _ in range(max(1, count)):
            yield

    @staticmethod
    def get_event_loop() -> asyncio.AbstractEventLoop:
        return asyncio.get_event_loop()

    @staticmethod
    def loop_time() -> float:
        """获取当前loop内部时钟
        """

        loop = asyncio.get_event_loop()

        return loop.time()

    @classmethod
    def call_soon(
            cls, callback: typing.Callable, *args,
            loop: asyncio.AbstractEventLoop = None, context: Context = None
    ) -> asyncio.Handle:
        """延时调用(能隔离上下文)
        """

        if loop is None:
            loop = asyncio.get_event_loop()

        if context is None:
            context = Context()

        return loop.call_soon(
            async_adapter(callback),
            *args,
            context=context
        )

    @classmethod
    def call_soon_threadsafe(
            cls, callback: typing.Callable, *args,
            loop: asyncio.AbstractEventLoop = None, context: Context = None
    ) -> asyncio.Handle:
        """延时调用(线程安全，能隔离上下文)
        """

        if loop is None:
            loop = asyncio.get_event_loop()

        if context is None:
            context = Context()

        return loop.call_soon_threadsafe(
            async_adapter(callback),
            *args,
            context=context
        )

    @classmethod
    def call_later(
            cls, delay: float, callback: typing.Callable, *args,
            loop: asyncio.AbstractEventLoop = None, context: Context = None
    ) -> asyncio.Handle:
        """延时指定秒数调用(能隔离上下文)
        """

        if loop is None:
            loop = asyncio.get_event_loop()

        if context is None:
            context = Context()

        return loop.call_later(
            delay,
            async_adapter(callback),
            *args,
            context=context
        )

    @classmethod
    def call_at(
            cls, when: float, callback: typing.Callable, *args,
            loop: asyncio.AbstractEventLoop = None, context: Context = None
    ) -> asyncio.Handle:
        """指定时间调用(能隔离上下文)
        """

        if loop is None:
            loop = asyncio.get_event_loop()

        if context is None:
            context = Context()

        return loop.call_at(
            when,
            async_adapter(callback),
            *args,
            context=context
        )

    @staticmethod
    def create_task(obj: typing.Union[typing.Generator, typing.Awaitable]):
        """将协程对象包装成task对象(兼容Future接口)
        """

        if inspect.isgenerator(obj) or inspect.isawaitable(obj):
            return asyncio.create_task(obj)
        else:
            return None

    @staticmethod
    def run_until_complete(future: typing.Union[typing.Coroutine, typing.Generator]):
        """运行事件循环直到future结束
        """

        loop = asyncio.get_event_loop()

        return loop.run_until_complete(future)

    @staticmethod
    @asynccontextmanager
    async def async_timeout(timeout: float):
        """异步超时等待

        async with timeout(1.5) as res:
            pass
        print(res.expired)

        """

        with catch_error():
            async with async_timeout.timeout(timeout) as res:
                yield res


def async_adapter(func: typing.Callable) -> typing.Callable:
    """异步函数适配装饰器

    使异步函数可以在同步函数中调用，即非阻塞式的启动异步函数，同时会影响上下文资源的生命周期

    """

    if not Utils.is_coroutine_function(func):
        return func

    @base.Utils.func_wraps(func)
    def _wrapper(*args, **kwargs):

        return Utils.create_task(
            func(*args, **kwargs)
        )

    return _wrapper


class WeakContextVar:
    """弱引用版的上下文资源共享器
    """

    def __init__(self, name: str):
        self._context_var: ContextVar = ContextVar(name, default=None)

    def get(self) -> typing.Any:

        ref = self._context_var.get()

        return None if ref is None else ref()

    def set(self, value: typing.Any) -> Token:
        return self._context_var.set(weakref.ref(value))


class FutureWithTimeout(asyncio.Future):
    """带超时功能的Future
    """

    def __init__(self, delay: float, default: typing.Any = None):

        super().__init__()

        self._timeout_handle = Utils.call_later(
            delay,
            self.set_result,
            default
        )

        self.add_done_callback(self._clear_timeout)

    def _clear_timeout(self, *_):

        if self._timeout_handle is not None:
            self._timeout_handle.cancel()
            self._timeout_handle = None


class FutureWithCoroutine(asyncio.Future):
    """Future实例可以被多个协程await，本类实现Future和Coroutine的桥接
    """

    def __init__(self, coroutine: typing.Coroutine):

        super().__init__()

        self._lock = asyncio.Lock()
        self._coroutine: typing.Coroutine = coroutine

    def __await__(self) -> typing.Any:
        return (yield from self._run_coroutine().__await__())

    async def _run_coroutine(self):

        async with self._lock:

            if not self.done():

                try:
                    self.set_result(
                        await self._coroutine
                    )
                except Exception as err:
                    super().cancel()
                    raise err

        return Utils.deepcopy(self.result())

    def cancel(self, *args, **kwargs):

        super().cancel()

        self._coroutine.close()


class AsyncCirculatory:
    """异步循环器

    提供一个循环体内的代码重复执行管理逻辑，可控制超时时间、执行间隔(LoopFrame)和最大执行次数

    async for index in AsyncCirculatory():
        pass

    其中index为执行次数，从1开始

    """

    def __init__(
            self, timeout: typing.Union[int, float] = 0,
            interval: typing.Union[int, float] = 0xff,
            max_times: int = 0
    ):

        self._expire_time: typing.Union[int, float] = 0

        if timeout > 0:
            self._expire_time = Utils.loop_time() + timeout

        self._interval: typing.Union[int, float] = interval
        self._max_times: int = max_times

        self._current: int = 0

    def __aiter__(self):
        return self

    async def __anext__(self):

        if self._current > 0:

            if (self._max_times > 0) and (self._max_times <= self._current):
                raise StopAsyncIteration()

            if (self._expire_time > 0) and (self._expire_time <= Utils.loop_time()):
                raise StopAsyncIteration()

            await self._sleep()

        self._current += 1

        return self._current

    async def _sleep(self):
        await Utils.wait_frame(self._interval)


class AsyncCirculatoryForSecond(AsyncCirculatory):

    def __init__(
            self, timeout: typing.Union[int, float] = 0,
            interval: typing.Union[int, float] = 0xff,
            max_times: int = 0
    ):
        super().__init__(timeout, interval, max_times)

    async def _sleep(self):
        await Utils.sleep(self._interval)


class FuncWrapper(base.FuncWrapper):
    """非阻塞异步函数包装器

    将多个同步或异步函数包装成一个可调用对象

    """

    def __call__(self, *args, **kwargs):

        for func in self._callables:
            Utils.call_soon(func, *args, **kwargs)


class AsyncConstructor(metaclass=ABCMeta):
    """实现了__async_init__异步构造函数
    """

    def __await__(self):

        yield from self.__async_init__().__await__()

        return self

    @abstractmethod
    async def __async_init__(self):
        """
        异步构造函数
        """


class AsyncFuncWrapper(base.FuncWrapper):
    """阻塞式异步函数包装器

    将多个同步或异步函数包装成一个可调用对象

    """

    async def __call__(self, *args, **kwargs):

        for func in self._callables:

            with catch_error():
                await Utils.awaitable_wrapper(
                    func(*args, **kwargs)
                )


class ShareFuture:
    """共享Future装饰器

    同一时刻并发调用函数时，使用该装饰器的函数签名一致地调用，会共享计算结果

    """

    def __init__(self):
        self._future: typing.Dict[str, FutureWithCoroutine] = {}

    def __call__(self, func: typing.Callable) -> typing.Callable:

        @base.Utils.func_wraps(func)
        async def _wrapper(*args, **kwargs):

            nonlocal self, func

            return await self._make_future(
                func, *args, **kwargs
            )

        return _wrapper

    def _make_future(self, func: typing.Callable, *args, **kwargs) -> FutureWithCoroutine:

        func_sign = Utils.params_sign(func, *args, **kwargs)
        future = self._future.get(func_sign)

        if not future:

            future = self._future[func_sign] = FutureWithCoroutine(func(*args, **kwargs))

            future.add_done_callback(
                Utils.func_partial(self._clear_future, func_sign)
            )

        return future

    def _clear_future(self, func_sign: str, _: typing.Any):

        if func_sign in self._future:
            del self._future[func_sign]


class FuncCache(ShareFuture):
    """函数缓存

    使用堆栈缓存实现的函数缓存，在有效期内函数签名一致就会命中缓存

    """

    def __init__(self, maxsize: int = 0xffff, ttl: float = 10):

        super().__init__()

        self._cache = StackCache(maxsize, ttl)

    def __call__(self, func: typing.Callable) -> typing.Callable:

        @base.Utils.func_wraps(func)
        async def _wrapper(*args, **kwargs):

            nonlocal self, func

            return await self._make_future(
                self._do_func_with_cache, func, *args, **kwargs
            )

        return _wrapper

    async def _do_func_with_cache(self, func: typing.Callable, *args, **kwargs) -> typing.Any:

        func_sign = Utils.params_sign(func, *args, **kwargs)

        result = self._cache.get(func_sign)

        if result is None:

            result = await func(*args, **kwargs)

            if result is not None:
                self._cache.set(func_sign, result)

        return result
