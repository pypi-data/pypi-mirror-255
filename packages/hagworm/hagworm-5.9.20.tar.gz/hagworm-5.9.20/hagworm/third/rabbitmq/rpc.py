# -*- coding: utf-8 -*-

__author__ = r'wsb310@gmail.com'

import typing

import asyncio
import inspect
import aio_pika
import async_timeout

from .publish import RabbitMQProducerForExchangePool
from .consume import RabbitMQConsumerForExchange

from ...extend.asyncio.base import Utils


class RpcServerError(Exception): pass


def get_routing_key(server_name: typing.Optional[str]) -> str:
    return f'rpc_server.{server_name}' if server_name else r'rpc_server'


class RpcServer:

    def __init__(
            self, pool_size: int, connection: aio_pika.RobustConnection, exchange_name: str,
            *, server_name: typing.Optional[str] = None, response_timeout: int = 60
    ):

        self._rpc_function: typing.Dict[str, typing.Callable] = {}

        self._queue_name: str = get_routing_key(server_name)
        self._exchange_name: str = exchange_name
        self._response_timeout: int = response_timeout

        self._producer: RabbitMQProducerForExchangePool = RabbitMQProducerForExchangePool(
            pool_size, connection, self._exchange_name
        )

        self._consumer: RabbitMQConsumerForExchange = RabbitMQConsumerForExchange(
            connection, self._queue_name, self._exchange_name
        )

    async def initialize(self):

        self._rpc_function[r'ping'] = lambda: r'pong'

        await self._producer.open(
            exchange_type=aio_pika.ExchangeType.TOPIC
        )

        await self._consumer.open(
            consume_func=self._consume_message,
            consume_no_ack=False,
            queue_config={
                r'arguments': {r'x-message-ttl': int(self._response_timeout * 1000)}
            },
            channel_qos_config={r'prefetch_count': self._producer.size}
        )

    async def release(self):

        await self._producer.close()
        await self._consumer.close()

        self._rpc_function.clear()

    async def _consume_message(self, message: aio_pika.IncomingMessage):

        try:

            _message = Utils.msgpack_decode(message.body)

            Utils.log.info(f'rpc client request: {_message}')

            _func_name = _message.get(r'name')
            _func_args = _message.get(r'args')
            _func_kwargs = _message.get(r'kwargs')

            if _func_name in self._rpc_function:

                try:

                    result = self._rpc_function[_func_name](*_func_args, **_func_kwargs)

                    if inspect.isawaitable(result):
                        result = await result

                    response = {
                        r'name': _func_name,
                        r'data': result,
                    }

                except Exception as err:

                    response = {
                        r'name': _func_name,
                        r'error': str(err),
                    }

            else:

                response = {
                    r'name': _func_name,
                    r'error': r'function not found',
                }

            await self._producer.publish(
                aio_pika.Message(
                    body=Utils.msgpack_encode(response),
                    correlation_id=message.correlation_id
                ),
                routing_key=message.reply_to
            )

        except Exception as err:

            Utils.log.error(str(err))

        finally:

            await message.ack()

    def register(self, name: str, func: typing.Callable):

        self._rpc_function[name] = func

        Utils.log.info(f'rpc server register {name} {func}')


class RpcClient:

    def __init__(
            self, pool_size: int, connection: aio_pika.RobustConnection,
            exchange_name: str, request_timeout: int = 60
    ):

        self._futures: typing.Dict[str, asyncio.Future] = {}

        self._queue_name: str = f'rpc_client.{Utils.uuid1()}'
        self._exchange_name: str = exchange_name
        self._request_timeout: int = request_timeout

        self._producer: RabbitMQProducerForExchangePool = RabbitMQProducerForExchangePool(
            pool_size, connection, self._exchange_name
        )

        self._consumer: RabbitMQConsumerForExchange = RabbitMQConsumerForExchange(
            connection, self._queue_name, self._exchange_name
        )

    async def initialize(self):

        await self._producer.open(
            exchange_type=aio_pika.ExchangeType.TOPIC
        )

        await self._consumer.open(
            consume_func=self._consume_message,
            consume_no_ack=False,
            queue_config={
                r'exclusive': True,
                r'arguments': {r'x-message-ttl': int(self._request_timeout * 1000)}
            },
            channel_qos_config={r'prefetch_count': self._producer.size}
        )

    async def release(self):

        await self._producer.close()
        await self._consumer.close()

    async def _consume_message(self, message: aio_pika.IncomingMessage):

        try:

            response = Utils.msgpack_decode(message.body)

            if message.correlation_id in self._futures:

                self._futures.get(
                    message.correlation_id
                ).set_result(
                    response
                )

        except Exception as err:

            Utils.log.error(str(err))

        finally:

            await message.ack()

    async def call(
            self, name: str, *,
            args: typing.Optional[typing.List] = None,
            kwargs: typing.Optional[typing.Dict] = None,
            server_name: typing.Optional[str] = None
    ):

        correlation_id = Utils.uuid1()

        future = self._futures[correlation_id] = asyncio.Future()

        message = {
            r'name': name,
            r'args': args if args is not None else [],
            r'kwargs': kwargs if kwargs is not None else {},
        }

        try:

            async with async_timeout.timeout(self._request_timeout):

                await self._producer.publish(
                    aio_pika.Message(
                        Utils.msgpack_encode(message),
                        correlation_id=correlation_id,
                        reply_to=self._consumer.queue_name,
                    ),
                    routing_key=get_routing_key(server_name),
                )

                response = await future

        except asyncio.TimeoutError as err:

            Utils.log.error(f'rpc call timeout: {message}')

            raise err

        except Exception as err:

            Utils.log.error(str(err))

            raise err

        finally:

            del self._futures[correlation_id]

        if r'error' in response:
            raise RpcServerError(response[r'error'])

        return response[r'data']
