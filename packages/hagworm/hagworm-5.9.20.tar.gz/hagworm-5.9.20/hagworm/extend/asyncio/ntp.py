# -*- coding: utf-8 -*-

__author__ = r'wsb310@gmail.com'

import time
import typing

import asyncio

from abc import abstractmethod

from ntplib import NTPClient

from .base import Utils
from .task import IntervalTask, MultiTasks

from ..error import NTPCalibrateError
from ..interface import TaskInterface


class _Interface(TaskInterface):
    """NTP客户端接口定义
    """

    @abstractmethod
    def start(self):
        raise NotImplementedError()

    @abstractmethod
    def stop(self):
        raise NotImplementedError()

    @abstractmethod
    def is_running(self) -> bool:
        raise NotImplementedError()

    @abstractmethod
    def calibrate_offset(self):
        raise NotImplementedError()

    @property
    @abstractmethod
    def offset(self) -> float:
        raise NotImplementedError()

    @property
    @abstractmethod
    def timestamp(self) -> float:
        raise NotImplementedError()


class AsyncNTPClient(_Interface):
    """异步NTP客户端类
    """

    @classmethod
    async def create(cls, host: str) -> 'AsyncNTPClient':

        client = cls(host)

        await client.calibrate_offset()

        client.start()

        return client

    def __init__(
            self, host: str, *,
            version: int = 2, port: str = r'ntp',
            timeout: int = 5, interval: int = 3600, sampling: int = 5
    ):

        self._settings = {
            r'host': host,
            r'version': version,
            r'port': port,
            r'timeout': timeout,
        }

        self._client: NTPClient = NTPClient()
        self._offset: float = 0

        self._sync_task: IntervalTask = IntervalTask.create(interval, self.calibrate_offset)

        self._sampling: int = sampling

    def start(self):
        return self._sync_task.start()

    def stop(self):
        return self._sync_task.stop()

    def is_running(self) -> bool:
        return self._sync_task.is_running()

    async def calibrate_offset(self):
        return await asyncio.to_thread(self._calibrate_offset)

    def _calibrate_offset(self):

        samples = []
        host_name = self._settings[r'host']

        # 多次采样取中位数，减少抖动影响
        for _ in range(self._sampling):
            try:
                resp = self._client.request(**self._settings)
                samples.append(resp.offset)
            except Exception as err:
                Utils.log.warning(f'NTP server {host_name} request error: {err}')

        if samples:
            self._offset = float(sum(samples) / len(samples))
            Utils.log.debug(f'NTP server {host_name} offset median {self._offset} samples: {samples}')
        else:
            raise NTPCalibrateError(f'NTP server {host_name} not available, timestamp uncalibrated')

    @property
    def offset(self) -> float:
        return self._offset

    @property
    def timestamp(self) -> float:

        return time.time() + self._offset


class AsyncNTPClientPool(_Interface):
    """异步NTP客户端池，多节点实现高可用
    """

    @classmethod
    async def create(cls, hosts: typing.List[str]) -> 'AsyncNTPClientPool':

        client_pool = cls()

        for host in hosts:
            client_pool.append(host)

        await client_pool.calibrate_offset()

        client_pool.start()

        return client_pool

    def __init__(self):

        self._clients: typing.List[AsyncNTPClient] = []
        self._running: bool = False

    def append(self, host, *, version=2, port='ntp', timeout=5, interval=3600, sampling=5):

        client = AsyncNTPClient(host, version=version, port=port, timeout=timeout, interval=interval, sampling=sampling)

        self._clients.append(client)

        if self._running:
            client.start()

    def start(self):

        for client in self._clients:
            client.start()

        self._running = True

    def stop(self):

        for client in self._clients:
            client.stop()

        self._running = False

    def is_running(self) -> bool:
        return self._running

    async def calibrate_offset(self):

        tasks = MultiTasks()

        for client in self._clients:
            tasks.append(client.calibrate_offset())

        await tasks

    @property
    def offset(self) -> float:

        samples = []

        for client in self._clients:
            samples.append(client.offset)

        return float(sum(samples) / len(samples))

    @property
    def timestamp(self) -> float:

        return time.time() + self.offset
