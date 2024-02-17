# -*- coding: utf-8 -*-

__author__ = r'wsb310@gmail.com'

import time
import typing

from abc import abstractmethod

from texttable import Texttable

from ..extend.base import Utils
from ..extend.asyncio.socket import recv_msg, DEFAULT_UNIX_SOCKET_ENDPOINT
from ..extend.asyncio.command import MainProcessAbstract, SubProcessAbstract


class TimerMS:

    __slots__ = [r'_timer']

    def __init__(self, timer: typing.Optional[float] = None):
        self._timer: float = time.time() if timer is None else timer

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.done()

    def done(self):
        self._timer = (time.time() - self._timer) * 1000

    @property
    def value(self) -> float:
        return self._timer


class Report:

    class _Report:

        def __init__(self):
            self.success: typing.List[float] = []
            self.failure: typing.List[float] = []

        @property
        def total(self) -> int:
            return len(self.success) + len(self.failure)

        @property
        def ratio(self) -> float:
            return len(self.success) / self.total if self.total > 0 else 0

        @property
        def min_success(self) -> float:
            return min(self.success)

        @property
        def max_success(self) -> float:
            return max(self.success)

        @property
        def avg_success(self) -> float:
            return sum(self.success) / len(self.success) if len(self.success) > 0 else 0

    def __init__(self):

        self._reports: typing.Dict = {}

        self._timer: typing.Optional[TimerMS] = None

    def __enter__(self):

        self._timer = TimerMS()

        return self

    def __exit__(self, exc_type, exc_val, exc_tb):

        self._timer.done()

        _time = max(round(self._timer.value / 1000), 1)
        _count = sum([item.total for item in self._reports.values()])

        table = Texttable()

        table.header(
            [
                r'Event Name',
                r'Success Total',
                r'Failure Total',
                r'Success Ratio',
                r'Success AveTime',
                r'Success MinTime',
                r'Success MaxTime',
            ]
        )

        for key, val in self._reports.items():
            table.add_row(
                [
                    key,
                    len(val.success),
                    len(val.failure),
                    r'{:.2%}'.format(val.ratio),
                    r'{:.3f}ms'.format(val.avg_success),
                    r'{:.3f}ms'.format(val.min_success),
                    r'{:.3f}ms'.format(val.max_success),
                ]
            )

        Utils.log.info(f'\nTotal: {_count}, Time: {_time}s, Qps: {round(_count / _time)}\n{table.draw()}\n')

    def _get_report(self, name: str) -> _Report:

        if name not in self._reports:
            self._reports[name] = self._Report()

        return self._reports[name]

    def add(self, name, result, resp_time):

        if result is True:
            self._get_report(name).success.append(resp_time)
        else:
            self._get_report(name).failure.append(resp_time)


class RunnerAbstract(SubProcessAbstract):

    @abstractmethod
    async def _run(self):
        """
        实际测试的业务逻辑
        """

    async def success(self, name: str, resp_time: typing.Union[int, float]):

        await self._socket_client.send_msg(
            [name, True, resp_time]
        )

    async def failure(self, name: str, resp_time: typing.Union[int, float]):

        await self._socket_client.send_msg(
            [name, False, resp_time]
        )


class Launcher(MainProcessAbstract):

    def __init__(
            self, target: typing.Callable, sub_process_num: int, unix_socket_path: str = DEFAULT_UNIX_SOCKET_ENDPOINT,
            *args, **kwargs
    ):

        super().__init__(target, sub_process_num, *args, unix_socket_path=unix_socket_path, **kwargs)

        self._report: Report = Report()

    async def _client_connected_cb(self, reader, writer):

        while True:

            request = await recv_msg(reader)

            if request:
                self._report.add(*request)
            else:
                break

    async def _run(self):

        with self._report:
            await super()._run()
