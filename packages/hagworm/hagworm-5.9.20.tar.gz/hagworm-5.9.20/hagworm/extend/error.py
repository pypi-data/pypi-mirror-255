# -*- coding: utf-8 -*-

__author__ = r'wsb310@gmail.com'

from contextlib import contextmanager

from .base import Utils


# 基础异常
class BaseError(Exception):
    pass


class Ignore(BaseError):
    """可忽略的异常

    用于with语句块跳出，或者需要跳出多层逻辑的情况

    """

    def __init__(self, *args, layers=1):

        super().__init__(*args)

        self._layers = layers

        info = str(self)

        if info:
            Utils.log.warning(info)

    def throw(self):

        if self._layers > 0:
            self._layers -= 1

        return self._layers != 0


@contextmanager
def catch_warning():
    """异常捕获，打印warning级日志

    通过with语句捕获异常，代码更清晰，还可以使用Ignore异常安全的跳出with代码块

    """

    try:
        yield
    except Ignore as err:
        if err.throw():
            raise err
    except Exception as err:
        Utils.log.warning(str(err))


@contextmanager
def catch_error():
    """异常捕获，打印error级日志

    通过with语句捕获异常，代码更清晰，还可以使用Ignore异常安全的跳出with代码块

    """

    try:
        yield
    except Ignore as err:
        if err.throw():
            raise err
    except Exception as err:
        Utils.log.exception(str(err))


# 数据库只读限制异常
class MySQLReadOnlyError(BaseError):
    pass


# NTP校准异常
class NTPCalibrateError(BaseError):
    pass


# Router异常
class RouterError(BaseError):
    pass
