# -*- coding: utf-8 -*-

__author__ = r'wsb310@gmail.com'

import time
import typing

import httpx

from ...extend.base import Utils
from ...extend.interface import TaskInterface
from ...extend.asyncio.future import Thread


DEFAULT_GROUP_NAME = r'DEFAULT_GROUP'
DEFAULT_PROTOCOL = r'http'
DEFAULT_REQUEST_TIMEOUT = 5
DEFAULT_PULLING_TIMEOUT = 60
DEFAULT_WEIGHT = 1

WORD_SEPARATOR = u'\x02'
LINE_SEPARATOR = u'\x01'


class _NacosInterface(TaskInterface):

    def __init__(self, servers: str, request_timeout: float):

        self._task: Thread = Thread(target=self._do_task)
        self._servers: typing.List[str] = Utils.split_str(servers, r',')

        self._http_client: httpx.Client = httpx.Client(timeout=request_timeout)

    def _do_task(self):
        """
        执行后台任务
        """

    def start(self):
        self._task.start()

    def stop(self):
        self._task.stop()
        self._http_client.close()

    def is_running(self) -> bool:
        return self._task.is_alive()


class NacosConfig(_NacosInterface):

    def __init__(
            self, listener: typing.Callable, servers: str, data_id: str, *,
            protocol: typing.Optional[str] = None, endpoint: typing.Optional[str] = None,
            group: typing.Optional[str] = None, namespace: typing.Optional[str] = None,
            request_timeout: float = DEFAULT_REQUEST_TIMEOUT, pulling_timeout: float = DEFAULT_PULLING_TIMEOUT
    ):

        super().__init__(servers, request_timeout)

        self._listener: typing.Callable = listener

        self._protocol: str = protocol if protocol is not None else DEFAULT_PROTOCOL
        self._endpoint: str = endpoint if endpoint is not None else r''
        self._namespace: str = namespace if namespace is not None else r''

        self._data_id: str = data_id
        self._group: str = group if group is not None else DEFAULT_GROUP_NAME

        self._content: typing.Optional[str] = None
        self._content_has: typing.Optional[str] = None

        self._request_timeout: float = request_timeout
        self._pulling_timeout: float = pulling_timeout

        self._flush()

    def _flush(self):

        self._content, self._content_hash = self.get_config()
        self._listener(self._content)

        Utils.log.info(f'nacos flush config: {self._content_hash}')

    def _do_task(self):

        while not self._task.is_stopped():

            payload = {
                r'Listening-Configs': WORD_SEPARATOR.join(
                    [
                        self._data_id,
                        self._group,
                        self._content_hash,
                        self._namespace,
                    ]
                ) + LINE_SEPARATOR,
            }

            headers = {
                r'Long-Pulling-Timeout': str(self._pulling_timeout * 1000),
            }

            for server in self._servers:

                url = f'{self._protocol}://{server}{self._endpoint}/nacos/v1/cs/configs/listener'

                try:

                    resp = self._http_client.post(
                        url, data=payload,
                        headers=headers, timeout=self._request_timeout + self._pulling_timeout
                    )

                    if resp.status_code == 200:
                        if resp.text:
                            Utils.log.info(f'nacos config pulling: {resp.text.strip()}')
                            self._flush()
                    else:
                        raise Exception(r'nacos config pulling error')

                except Exception as err:
                    Utils.log.error(str(err))
                    time.sleep(self._request_timeout)
                else:
                    break

            else:

                Utils.log.error(f'nacos config pulling failed: servers unusable')

    def get_config(self) -> typing.Tuple[str, str]:

        content = content_hash = None

        params = {
            r'dataId': self._data_id,
            r'group': self._group,
        }

        if self._namespace:
            params[r'tenant'] = self._namespace

        for server in self._servers:

            url = f'{self._protocol}://{server}{self._endpoint}/nacos/v1/cs/configs'

            try:

                resp = self._http_client.get(url, params=params)

                if resp.status_code == 200:
                    content = resp.text
                    content_hash = Utils.md5(content)
                else:
                    raise Exception(r'nacos get config error')

            except Exception as err:
                Utils.log.error(str(err))
            else:
                break

        else:

            Utils.log.error(f'nacos get config failed: servers unusable')

        return content, content_hash


class NacosInstanceRegister(_NacosInterface):

    def __init__(
            self, servers: str, service_name: str, service_ip: str, service_port: int, heartbeat_interval: int, *,
            protocol: typing.Optional[str] = None, endpoint: typing.Optional[str] = None,
            group: typing.Optional[str] = None, namespace: typing.Optional[str] = None,
            cluster: typing.Optional[str] = None, weight: typing.Optional[int] = None,
            request_timeout: float = DEFAULT_REQUEST_TIMEOUT
    ):

        super().__init__(servers, request_timeout)

        self._service_name: str = service_name
        self._service_ip: str = service_ip
        self._service_port: int = service_port

        self._protocol: str = protocol if protocol is not None else DEFAULT_PROTOCOL
        self._endpoint: str = endpoint if endpoint is not None else r''
        self._namespace: str = namespace if namespace is not None else r''

        self._group: str = group if group is not None else DEFAULT_GROUP_NAME
        self._cluster: str = cluster
        self._weight: int = weight if weight is not None else DEFAULT_WEIGHT

        self._heartbeat_interval: int = heartbeat_interval

    def _do_task(self):

        while not self._task.is_stopped():

            payload = {
                r'serviceName': self._service_name,
                r'namespaceId': self._namespace,
                r'groupName': self._group,
                r'beat': Utils.json_encode(
                    {
                        r'serviceName': self._service_name,
                        r'ip': self._service_ip,
                        r'port': str(self._service_port),
                        r'weight': self._weight,
                        r'ephemeral': True,
                    }
                ),
            }

            for server in self._servers:

                url = f'{self._protocol}://{server}{self._endpoint}/nacos/v1/ns/instance/beat'

                try:

                    resp = self._http_client.put(url, data=payload)

                    if resp.status_code != 200:
                        raise Exception(r'nacos instance beat error')

                except Exception as err:
                    Utils.log.error(str(err))
                else:
                    break

            else:

                Utils.log.error(f'nacos instance beat failed: servers unusable')

            time.sleep(self._heartbeat_interval)

    def start(self):

        payload = {
            r'serviceName': self._service_name,
            r'ip': self._service_ip,
            r'port': self._service_port,
            r'namespaceId': self._namespace,
            r'weight': self._weight,
            r'enabled': True,
            r'healthy': True,
            r'groupName': self._group,
            r'ephemeral': True,
        }

        if self._cluster:
            payload[r'clusterName'] = self._cluster

        for server in self._servers:

            url = f'{self._protocol}://{server}{self._endpoint}/nacos/v1/ns/instance'

            try:

                resp = self._http_client.post(url, data=payload)

                if resp.status_code == 200:
                    self._task.start()
                    Utils.log.info(f'nacos instance register: {payload}')
                else:
                    raise Exception(r'nacos instance register error')

            except Exception as err:
                Utils.log.error(str(err))
            else:
                break

        else:

            Utils.log.error(f'nacos instance register failed: servers unusable')


class NacosInstanceQuery(_NacosInterface):

    def __init__(
            self, listener: typing.Callable, servers: str, service_name: str, listener_interval: int, *,
            protocol: typing.Optional[str] = None, endpoint: typing.Optional[str] = None,
            group: typing.Optional[str] = None, namespace: typing.Optional[str] = None,
            cluster: typing.Optional[str] = None,
            request_timeout: float = DEFAULT_REQUEST_TIMEOUT
    ):

        super().__init__(servers, request_timeout)

        self._listener: typing.Callable = listener

        self._service_name: str = service_name

        self._protocol: str = protocol if protocol is not None else DEFAULT_PROTOCOL
        self._endpoint: str = endpoint if endpoint is not None else r''
        self._namespace: str = namespace if namespace is not None else r''

        self._group: str = group if group is not None else DEFAULT_GROUP_NAME
        self._cluster: typing.Optional[str] = cluster

        self._content: typing.Optional[typing.List[typing.Dict]] = None
        self._content_hash: typing.Optional[str] = None

        self._listener_interval: int = listener_interval

        self._content, self._content_hash = self._send_query()

    def _do_task(self):

        while not self._task.is_stopped():

            content, content_hash = self._send_query()

            if content_hash != self._content_hash:
                Utils.log.info(f'nacos instance query: {content}')
                self._content, self._content_hash = content, content_hash
                self._listener(self._content)

            time.sleep(self._listener_interval)

    def _send_query(self) -> typing.Tuple[typing.List[typing.Dict], str]:

        content = content_hash = None

        params = {
            r'serviceName': self._service_name,
            r'namespaceId': self._namespace,
            r'groupName': self._group,
            r'healthyOnly': True,
        }

        if self._cluster:
            params[r'clusterName'] = self._cluster

        for server in self._servers:

            url = f'{self._protocol}://{server}{self._endpoint}/nacos/v1/ns/instance/list'

            try:

                resp = self._http_client.get(url, params=params)

                if resp.status_code == 200:
                    content = resp.json()[r'hosts']
                    content_hash = Utils.md5(Utils.json_encode(content))
                else:
                    raise Exception(r'nacos instance query error')

            except Exception as err:
                Utils.log.error(str(err))
            else:
                break

        else:

            Utils.log.error(f'nacos instance query failed: servers unusable')

        return content, content_hash

    def get_host(self) -> typing.Dict:

        if self._content:
            return Utils.rand_hit(self._content, lambda x: int(x[r'weight'] * 100))

    def get_hosts(self) -> typing.List[typing.Dict]:
        return self._content
