# -*- coding: utf-8 -*-

__author__ = r'wsb310@gmail.com'

import typing
import signal
import socket
import asyncio

import grpc
import msgpack

from abc import abstractmethod
from pydantic import BaseModel

from ...extend.asyncio.base import Utils


UNARY_UNARY_MODE = grpc.unary_unary_rpc_method_handler
UNARY_STREAM_MODE = grpc.unary_stream_rpc_method_handler
STREAM_UNARY_MODE = grpc.stream_unary_rpc_method_handler
STREAM_STREAM_MODE = grpc.stream_stream_rpc_method_handler

GRPC_MODE_TYPE = typing.Union[
    typing.Type[UNARY_UNARY_MODE],
    typing.Type[UNARY_STREAM_MODE],
    typing.Type[STREAM_UNARY_MODE],
    typing.Type[STREAM_STREAM_MODE]
]


class StreamHandler:

    def __init__(self, request: typing.AsyncIterator, context: grpc.aio.ServicerContext):

        self._request: typing.AsyncIterator = request
        self._context: grpc.aio.ServicerContext = context

        self._stream_task: asyncio.Task = asyncio.create_task(self._do_stream_task())

    def _on_context_done(self, _: grpc.aio.ServicerContext):

        Utils.log.info(f'grpc close stream {self.peer()}')

        Utils.call_soon(self.on_disconnect)

    async def _do_stream_task(self):

        Utils.log.info(f'grpc open stream {self.peer()}')

        await self.on_connect()
        self._context.add_done_callback(self._on_context_done)

        async for _msg in self._request:

            try:
                if _msg is grpc.aio.EOF:
                    break
                else:
                    await self.on_message(_msg)
            except Exception as err:
                Utils.log.error(str(err))
                break

    def peer(self) -> str:
        return self._context.peer()

    def done(self) -> bool:
        return self._stream_task.done()

    async def join(self):
        await self._stream_task

    async def cancel(self):

        if not self._stream_task.done():
            self._stream_task.cancel()

        if not self._context.done():
            await self._context.abort(grpc.StatusCode.CANCELLED)

    async def read(self) -> typing.Any:

        data = await self._context.read()

        if data != grpc.aio.EOF:
            return data
        else:
            raise ConnectionAbortedError()

    async def send(self, msg: typing.Any):

        if not self._context.done():
            await self._context.write(msg)
        else:
            Utils.log.warning(f'grpc stream send canceled: {msg}')

    @abstractmethod
    async def on_message(self, msg: typing.Any):
        """
        接收消息回调
        """

    @abstractmethod
    async def on_connect(self):
        """
        与客户端通信连接成功后回调
        """

    @abstractmethod
    async def on_disconnect(self):
        """
        与客户端通信失去连接后回调
        """


class Router:

    def __init__(self, service: str):

        self._service: str = service
        self._handlers: typing.Dict[str, typing.Tuple[typing.Callable, GRPC_MODE_TYPE]] = {}

    @property
    def service(self) -> str:
        return self._service

    @property
    def handlers(self) -> typing.List[typing.Tuple[typing.Callable, GRPC_MODE_TYPE]]:
        return list(self._handlers.values())

    def register(self, func: typing.Callable, mode: GRPC_MODE_TYPE) -> typing.Callable:

        if func.__name__ in self._handlers:
            raise ValueError(f'{func.__name__} has exists')

        self._handlers[func.__name__] = (func, mode,)

        return func

    def unary_unary(
            self, func: typing.Callable = None, *, model: typing.Type[BaseModel] = None
    ) -> typing.Callable:

        if func is None:
            return Utils.func_partial(self.unary_unary, model=model)

        @Utils.func_wraps(func)
        async def _func(request, context):
            if model is None:
                return await func(request, context)
            else:
                return await func(model(**request), context)

        return self.register(_func, UNARY_UNARY_MODE)

    def unary_stream(
            self, func: typing.Callable = None, *, model: typing.Type[BaseModel] = None
    ) -> typing.Callable:

        if func is None:
            return Utils.func_partial(self.unary_stream, model=model)

        @Utils.func_wraps(func)
        async def _func(request, context):
            if model is None:
                return await func(request, context)
            else:
                return await func(model(**request), context)

        return self.register(_func, UNARY_STREAM_MODE)

    def stream_unary(self, func: typing.Callable) -> typing.Callable:
        return self.register(func, STREAM_UNARY_MODE)

    def stream_stream(self, func: typing.Callable) -> typing.Callable:
        return self.register(func, STREAM_STREAM_MODE)


class GRPCServer:

    def __init__(
            self,
            interceptors: typing.Optional[typing.Sequence[typing.Any]] = None,
            options: typing.Optional[grpc.aio.ChannelArgumentType] = None,
            maximum_concurrent_rpcs: typing.Optional[int] = None,
            compression: typing.Optional[grpc.Compression] = None,
            request_deserializer: typing.Callable = msgpack.loads,
            response_serializer: typing.Callable = msgpack.dumps
    ):

        self._server: grpc.aio.Server = grpc.aio.server(
            interceptors=interceptors,
            options=options,
            maximum_concurrent_rpcs=maximum_concurrent_rpcs,
            compression=compression
        )

        self._request_deserializer: typing.Callable = request_deserializer
        self._response_serializer: typing.Callable = response_serializer

        signal.signal(signal.SIGINT, self._exit)
        signal.signal(signal.SIGTERM, self._exit)

    def _exit(self, *_):
        Utils.call_soon(self.stop)

    @property
    def server(self) -> grpc.aio.Server:

        return self._server

    def register(self, service: str, handlers: typing.List[typing.Callable], *, mode: GRPC_MODE_TYPE = UNARY_UNARY_MODE):

        generic_handlers = []

        for handler in handlers:
            generic_handlers.append(
                grpc.method_handlers_generic_handler(
                    service,
                    {
                        handler.__name__: mode(
                            handler,
                            request_deserializer=self._request_deserializer,
                            response_serializer=self._response_serializer,
                        )
                    }
                )
            )

        self._server.add_generic_rpc_handlers(generic_handlers)

    def bind_router(self, router: Router):

        generic_handlers = []

        for _func, _mode in router.handlers:
            generic_handlers.append(
                grpc.method_handlers_generic_handler(
                    router.service,
                    {
                        _func.__name__: _mode(
                            _func,
                            request_deserializer=self._request_deserializer,
                            response_serializer=self._response_serializer,
                        )
                    }
                )
            )

        self._server.add_generic_rpc_handlers(generic_handlers)

    async def start(
            self,
            address: typing.Union[str, typing.Tuple[str, int]],
            family: int = socket.AF_INET,
            server_credentials: typing.Optional[grpc.ServerCredentials] = None
    ):

        if family == socket.AF_INET:
            _socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            _address = f'{address[0]}:{address[1]}'
        elif family == socket.AF_INET6:
            _socket = socket.socket(socket.AF_INET6, socket.SOCK_STREAM)
            _address = f'[{address[0]}]:{address[1]}'
        elif family == socket.AF_UNIX:
            _socket = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
            _address = f'unix:{address}'
        else:
            raise ValueError(r'family invalid')

        _socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, True)
        _socket.bind(address)

        if server_credentials is None:
            self._server.add_insecure_port(_address)
        else:
            self._server.add_secure_port(_address, server_credentials)

        await self._server.start()

        Utils.log.success(f'grpc server [pid:{Utils.getpid()}] startup complete: {address}')

    async def stop(self, grace: typing.Optional[float] = None):
        await self._server.stop(grace)

    async def wait(self, timeout: typing.Optional[float] = None):
        return await self._server.wait_for_termination(timeout)
