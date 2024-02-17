# -*- coding: utf-8 -*-

__author__ = r'wsb310@gmail.com'

import typing

import asyncio

from threading import Event, Thread as _Thread
from concurrent.futures import ThreadPoolExecutor

from ..interface import RunnableInterface, TaskInterface

from .base import Utils


class Thread(_Thread):
    """带强制停止功能的线程，如非必要请勿使用
    """
    
    def __init__(self, group=None, target=None, name=None, args=(), kwargs=None):

        super().__init__(group, target, name, args, kwargs, daemon=True)

        self._exit_event: Event = Event()

    def stop(self, timeout: int = None):

        self._exit_event.set()

        if timeout is not None:
            self.join(timeout)

    def is_stopped(self) -> bool:

        return self._exit_event.is_set()


class ThreadPool(RunnableInterface):
    """线程池，桥接线程与协程
    """

    def __init__(self, max_workers: typing.Optional[int] = None):

        self._executor = ThreadPoolExecutor(max_workers)

    async def run(self, _callable: typing.Callable, *args, **kwargs):
        """线程转协程，不支持协程函数
        """

        loop = asyncio.events.get_event_loop()

        if kwargs:

            return await loop.run_in_executor(
                self._executor,
                Utils.func_partial(
                    _callable,
                    *args,
                    **kwargs
                )
            )

        else:

            return await loop.run_in_executor(
                self._executor,
                _callable,
                *args,
            )


class ThreadWorker:
    """通过线程转协程实现普通函数非阻塞的装饰器
    """

    def __init__(self, max_workers: typing.Optional[int] = None):

        self._thread_pool = ThreadPool(max_workers)

    def __call__(self, func: typing.Callable):

        @Utils.func_wraps(func)
        def _wrapper(*args, **kwargs):
            return self._thread_pool.run(func, *args, **kwargs)

        return _wrapper


class SubProcess(TaskInterface):
    """子进程管理，通过command方式启动子进程
    """

    @classmethod
    async def create(cls, program, *args, stdin=None, stdout=None, stderr=None, **kwargs):

        inst = cls(program, *args, stdin=stdin, stdout=stdout, stderr=stderr, **kwargs)
        await inst.start()

        return inst

    def __init__(
            self, program: str, *args,
            stdin: int = asyncio.subprocess.DEVNULL,
            stdout: int = asyncio.subprocess.DEVNULL,
            stderr: int= asyncio.subprocess.DEVNULL,
            **kwargs
    ):

        self._program: str = program
        self._args: typing.Tuple = args
        self._kwargs: typing.Dict = kwargs

        self._stdin: int = stdin
        self._stdout: int = stdout
        self._stderr: int = stderr

        self._process: typing.Optional['asyncio.subprocess.Process'] = None
        self._process_id: typing.Optional[int] = None

    @property
    def pid(self) -> int:
        return self._process_id

    @property
    def process(self) -> 'asyncio.subprocess.Process':
        return self._process

    @property
    def stdin(self) -> 'asyncio.streams.StreamWriter':
        return self._process.stdin

    @property
    def stdout(self) -> 'asyncio.streams.StreamReader':
        return self._process.stdout

    @property
    def stderr(self) -> 'asyncio.streams.StreamReader':
        return self._process.stderr

    def create_stdout_task(self) -> asyncio.Task:
        return Utils.create_task(self._log_stdout())

    async def _log_stdout(self):

        stream = self._process.stdout

        while self._process.returncode is None:

            content = await stream.readline()

            if content:
                content = content.decode().strip()
                if content:
                    Utils.log.info(content)
            else:
                break

    def create_stderr_task(self) -> asyncio.Task:

        return Utils.create_task(self._log_stderr())

    async def _log_stderr(self):

        stream = self._process.stderr

        while self._process.returncode is None:

            content = await stream.readline()

            if content:
                content = content.decode().strip()
                if content:
                    Utils.log.error(content)
            else:
                break

    def is_running(self) -> bool:
        return self._process is not None and self._process.returncode is None

    async def start(self) -> bool:

        if self.is_running():
            return False

        self._process = await asyncio.create_subprocess_exec(
            self._program, *self._args,
            stdin=self._stdin,
            stdout=self._stdout,
            stderr=self._stderr,
            **self._kwargs
        )

        self._process_id = self._process.pid

        return True

    async def stop(self) -> bool:

        if not self.is_running():
            return False

        self._process.kill()
        await self._process.wait()

        return True

    def kill(self) -> bool:

        if not self.is_running():
            return False

        self._process.kill()

        return True

    async def wait(self, timeout: typing.Optional[float] = None):

        if not self.is_running():
            return

        try:
            await asyncio.wait_for(self._process.wait(), timeout=timeout)
        except Exception as err:
            Utils.log.error(err)
        finally:
            await self.stop()
