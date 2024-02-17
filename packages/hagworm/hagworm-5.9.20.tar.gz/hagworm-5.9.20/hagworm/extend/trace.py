# -*- coding: utf-8 -*-

__author__ = r'wsb310@gmail.com'

import typing

import uuid
import time
import functools

from asyncio import iscoroutinefunction
from contextvars import ContextVar
from loguru import logger


TRACE_ID_CONTEXT: ContextVar[typing.Optional[str]] = ContextVar(r'trace_id', default=None)
TRACE_NO_CONTEXT: ContextVar[typing.Optional[int]] = ContextVar(r'trace_no', default=None)


def get_trace_id() -> str:

    return TRACE_ID_CONTEXT.get()


def refresh_trace_id(trace_id: typing.Optional[str] = None, trace_no: typing.Optional[str] = None) -> str:

    if trace_id is None:
        trace_id = str(uuid.uuid1())

    TRACE_ID_CONTEXT.set(trace_id)
    TRACE_NO_CONTEXT.set(trace_no)

    return trace_id


def inc_trace_no() -> int:

    trace_no = TRACE_NO_CONTEXT.get()
    trace_no = 0 if trace_no is None else trace_no + 1

    TRACE_NO_CONTEXT.set(trace_no)

    return trace_no


def trace_wrapper(func: typing.Callable) -> typing.Callable:

    if iscoroutinefunction(func):
        @functools.wraps(func)
        async def _wrapper(*args, **kwargs):
            refresh_trace_id()
            return await func(*args, **kwargs)
    else:
        @functools.wraps(func)
        def _wrapper(*args, **kwargs):
            refresh_trace_id()
            return func(*args, **kwargs)

    return _wrapper


def tracing(func: typing.Callable) -> typing.Callable:

    @functools.wraps(func)
    def _wrapper(*args, **kwargs):

        _time = time.time() * 1000

        try:
            return func(*args, **kwargs)
        finally:
            trace_time = r'{:.3f}'.format(time.time() * 1000 - _time)
            logger.bind(
                trace_id=get_trace_id(), trace_no=inc_trace_no(),
                trace_time=trace_time
            ).info(
                f'tracing <{func.__qualname__}> {trace_time}ms\n'
                f'args: {args}, kwargs: {kwargs}'
            )

    return _wrapper


def async_tracing(func: typing.Callable) -> typing.Callable:

    @functools.wraps(func)
    async def _wrapper(*args, **kwargs):

        _time = time.time() * 1000

        try:
            return await func(*args, **kwargs)
        finally:
            trace_time = r'{:.3f}'.format(time.time() * 1000 - _time)
            logger.bind(
                trace_id=get_trace_id(), trace_no=inc_trace_no(),
                trace_time=trace_time
            ).info(
                f'tracing <{func.__qualname__}> {trace_time}ms\n'
                f'args: {args}, kwargs: {kwargs}'
            )

    return _wrapper

