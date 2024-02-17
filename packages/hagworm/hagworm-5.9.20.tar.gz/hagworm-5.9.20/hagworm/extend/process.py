# -*- coding: utf-8 -*-

__author__ = r'wsb310@gmail.com'

import os
import sys
import time
import signal
import typing

from multiprocessing import Process, set_start_method
from multiprocessing.shared_memory import SharedMemory

from .base import Utils
from .interface import ContextManager, RunnableInterface
from .struct import ByteArrayAbstract


def set_spawn_mode():

    set_start_method(r'spawn')


def fork_processes() -> int:

    pid = os.fork()

    if pid == 0:
        Utils.urandom_seed()

    return pid


class Daemon(RunnableInterface):

    def __init__(
            self, target: typing.Callable, sub_process_num: int, *,
            set_affinity: typing.Optional[typing.List[int]] = None, join_timeout: int = 10, **kwargs
    ):

        self._target: typing.Callable = target
        self._kwargs: typing.Dict = kwargs

        self._sub_process: typing.Set = set()
        self._sub_process_num: int = sub_process_num

        self._set_affinity: typing.Optional[typing.List[int]] = set_affinity
        self._join_timeout: int = join_timeout

        signal.signal(signal.SIGINT, self._kill_process)
        signal.signal(signal.SIGTERM, self._kill_process)

        if self._set_affinity:

            if sub_process_num > len(self._set_affinity):
                raise Exception(f'process num {sub_process_num}, affinity {self._set_affinity}')

            cpu_count = os.cpu_count()

            for _core in self._set_affinity:
                if _core >= cpu_count:
                    raise Exception(f'cpu cores num {cpu_count}, cores {self._set_affinity}')

    def _kill_process(self, *_):

        for process in self._sub_process:
            os.kill(process.ident, signal.SIGINT)

        for process in self._sub_process:
            process.join(self._join_timeout)
            process.kill()

    def _fill_process(self):

        for idx in range(self._sub_process_num - len(self._sub_process)):

            process = Process(target=self._target, args=(idx,), kwargs=self._kwargs)
            process.start()

            self._sub_process.add(process)

        if self._set_affinity:

            for _idx, _process in enumerate(self._sub_process):

                _pid = _process.pid
                _cores = self._set_affinity[_idx: _idx + 1]

                os.sched_setaffinity(_pid, _cores)
                sys.stdout.write(f'process {_pid} affinity {os.sched_getaffinity(_pid)}\n')

    def _check_process(self):

        for process in self._sub_process.copy():

            if process.is_alive():
                continue

            self._sub_process.remove(process)
            sys.stderr.write(f'kill process {process.ident}\n')

        return len(self._sub_process) > 0

    def run(self):

        self._fill_process()

        while self._check_process():
            time.sleep(1)


class SharedByteArray(ByteArrayAbstract, ContextManager):

    def __init__(self, name: typing.Optional[str] = None, create: bool = False, size: int = 0):

        ByteArrayAbstract.__init__(self)

        self._shared_memory: SharedMemory = SharedMemory(name, create, size)
        self._create_mode: bool = create

    def _context_release(self):

        self.release()

    def release(self):

        self._shared_memory.close()

        if self._create_mode:
            self._shared_memory.unlink()

    def read(self, size: int) -> memoryview:
        return self._shared_memory.buf[:size]

    def write(self, buffer: memoryview):
        self._shared_memory.buf[:len(buffer)] = buffer


class HeartbeatChecker(ContextManager):

    def __init__(self, name: str = r'default', timeout: int = 60):

        self._name: str = f'heartbeat_{name}'

        self._timeout: int = timeout

        self._byte_array: typing.Optional[SharedByteArray] = None

        # noinspection PyBroadException
        try:
            self._byte_array = SharedByteArray(self._name, True, 8)
        except Exception as _:
            self._byte_array = SharedByteArray(self._name)

    def _context_release(self):

        self.release()

    @property
    def refresh_time(self) -> int:

        if self._byte_array is not None:
            return self._byte_array.read_unsigned_int()
        else:
            return 0

    def release(self):

        if self._byte_array is not None:
            self._byte_array.release()
            self._byte_array = None

    def check(self) -> bool:

        return (Utils.timestamp() - self.refresh_time) < self._timeout

    def refresh(self):

        if self._byte_array is not None:
            self._byte_array.write_unsigned_int(Utils.timestamp())
