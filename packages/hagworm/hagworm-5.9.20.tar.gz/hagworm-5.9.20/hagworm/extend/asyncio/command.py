# -*- coding: utf-8 -*-

__author__ = r'wsb310@gmail.com'

import typing
import asyncio

from abc import abstractmethod

from .base import install_uvloop, Utils
from .socket import UnixSocketServer, UnixSocketClient, DEFAULT_LIMIT, DEFAULT_UNIX_SOCKET_ENDPOINT

from ..interface import RunnableInterface
from ..process import Daemon


class MainProcessAbstract(Daemon):

    def __init__(
            self, target: typing.Callable, sub_process_num: int, *,
            set_affinity: typing.Optional[typing.List[int]] = None, join_timeout: int = 10,
            unix_socket_path: str = DEFAULT_UNIX_SOCKET_ENDPOINT, unix_socket_limit: int = DEFAULT_LIMIT,
            **kwargs
    ):

        super().__init__(
            target, sub_process_num,
            set_affinity=set_affinity, join_timeout=join_timeout,
            unix_socket_path=unix_socket_path,
            **kwargs
        )

        self._socket_server: UnixSocketServer = UnixSocketServer(
            self._client_connected_cb, unix_socket_path, unix_socket_limit
        )

    @abstractmethod
    async def _client_connected_cb(
            self,
            reader: 'asyncio.streams.StreamReader',
            writer: 'asyncio.streams.StreamWriter'
    ):
        """
        连接成功后的回调函数
        """

    async def _run(self):

        self._fill_process()

        while self._check_process():
            await Utils.sleep(1)

    def run(self):

        Utils.print_slogan()

        install_uvloop()

        Utils.run_until_complete(self._socket_server.open())
        Utils.run_until_complete(self._run())
        Utils.run_until_complete(self._socket_server.close())


class SubProcessAbstract(RunnableInterface):

    @classmethod
    def create(cls, process_num: int, unix_socket_path: str):

        cls(process_num, unix_socket_path).run()

    def __init__(self, process_num: int, unix_socket_path: str):

        self._socket_client: UnixSocketClient = UnixSocketClient(unix_socket_path)

        self._process_id: int = Utils.getpid()
        self._process_num: int = process_num

    @abstractmethod
    async def _run(self):
        """
        子进程的运行逻辑
        """

    def run(self):

        Utils.log.success(f'Started worker process [id:{self._process_id} num:{self._process_num}]')

        install_uvloop()

        Utils.run_until_complete(self._socket_client.open())
        Utils.run_until_complete(self._run())
        Utils.run_until_complete(self._socket_client.close())

        Utils.log.success(f'Stopped worker process [id:{self._process_id} num:{self._process_num}]')
