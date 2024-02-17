# -*- coding: utf-8 -*-

__author__ = r'wsb310@gmail.com'

from hagworm.frame.gunicorn import DEFAULT_WORKER_STR, SIMPLE_LOG_CONFIG
from hagworm.extend.metaclass import Singleton
from hagworm.extend.process import HeartbeatChecker

from setting import Config

# 进程数
workers = Config.ProcessNum

# 工人类
worker_class = DEFAULT_WORKER_STR

# 日志配置
logconfig_dict = SIMPLE_LOG_CONFIG

# 绑定地址
bind = f':{Config.Port}'


# 启动辅助
class LaunchHelper(Singleton):

    def __init__(self):

        self._heartbeat_checker = None

    def on_starting(self, server):

        self._heartbeat_checker = HeartbeatChecker(Config.ServerName)

    def on_exit(self, server):

        self._heartbeat_checker.release()


def on_starting(server):

    LaunchHelper().on_starting(server)


def on_exit(server):

    LaunchHelper().on_exit(server)
