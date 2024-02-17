# -*- coding: utf-8 -*-

__author__ = r'wsb310@gmail.com'

import os
import time
import typing
import logging
import fastapi

from enum import Enum

from starlette.types import ASGIApp, Receive, Scope, Send
from starlette.status import HTTP_422_UNPROCESSABLE_ENTITY
from starlette.exceptions import HTTPException
from starlette.routing import is_async_callable
from starlette.concurrency import run_in_threadpool

from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import RequestValidationError
from fastapi.openapi.docs import get_swagger_ui_html

from ... import hagworm_label

from ...extend.trace import get_trace_id, refresh_trace_id
from ...extend.asyncio.base import Utils, install_uvloop
from ...extend.logging import DEFAULT_LOG_FILE_NAME, DEFAULT_LOG_FILE_ROTATOR, init_logger

from .response import Response, ErrorResponse


get_swagger_ui_html.__kwdefaults__.update(
    {
        r'swagger_js_url': r'https://cdn.bootcdn.net/ajax/libs/swagger-ui/5.6.2/swagger-ui-bundle.min.js',
        r'swagger_css_url': r'https://cdn.bootcdn.net/ajax/libs/swagger-ui/5.6.2/swagger-ui.min.css',
    }
)


DEFAULT_HEADERS = [(r'Server', hagworm_label)]


def create_fastapi(
        log_level: str = r'info', log_handler: typing.Optional[logging.Handler] = None,
        log_file_path: typing.Optional[str] = None, log_file_name: str =DEFAULT_LOG_FILE_NAME,
        log_file_rotation: typing.Callable = DEFAULT_LOG_FILE_ROTATOR, log_file_retention: int = 0xff,
        log_extra: typing.Optional[typing.Dict] = None, log_enqueue: bool = False,
        debug: bool = False, routes: typing.Optional[typing.List] = None,
        **setting: typing.Any
):

    init_logger(
        log_level.upper(),
        handler=log_handler,
        file_path=log_file_path,
        file_name=log_file_name,
        file_rotation=log_file_rotation,
        file_retention=log_file_retention,
        extra=log_extra,
        enqueue=log_enqueue,
        debug=debug
    )

    Utils.print_slogan()

    install_uvloop()

    _fastapi = fastapi.FastAPI(debug=debug, routes=routes, **setting)

    _fastapi.add_exception_handler(HTTPException, http_exception_handler)
    _fastapi.add_exception_handler(RequestValidationError, request_validation_exception_handler)

    return _fastapi


class APIRoute(fastapi.routing.APIRoute):

    def __init__(self, *args, **kwargs):

        super().__init__(*args, **kwargs)

        self.app = self.request_response()

    async def prepare(self, request: fastapi.Request):

        pass

    def request_response(self) -> ASGIApp:

        func = self.get_route_handler()

        is_coroutine = is_async_callable(func)

        async def app(scope: Scope, receive: Receive, send: Send) -> None:

            request = Request(scope, receive, send, self)

            try:

                trace_id = refresh_trace_id(request.get_header(r'x-request-id', None))

                request_time = time.time() * 1000

                await self.prepare(request)

                if is_coroutine:
                    response = await func(request)
                else:
                    response = await run_in_threadpool(func, request)

                response.headers.update(
                    {
                        r'x-trace-id': trace_id,
                        r'x-server-time-ms': r'{:.0f}'.format(request_time),
                        r'x-request-ttl-ms': r'{:.3f}'.format(time.time() * 1000 - request_time),
                        r'x-request-payload': request.get_header(r'x-request-payload', r''),
                    }
                )

                await response(scope, receive, send)

            except ErrorResponse as err:

                Utils.log.warning(f'ErrorResponse: {request.path}\n{err}\n{request.debug_info}')

                await err(scope, receive, send)

        return app


class APIRouter(fastapi.APIRouter):
    """目录可选末尾的斜杠访问
    """

    def __init__(
            self, *,
            prefix: str = r'',
            default_response_class: typing.Type[Response] = Response,
            route_class: typing.Type[APIRoute] = APIRoute,
            **kwargs
    ):

        super().__init__(
            prefix=prefix,
            default_response_class=default_response_class,
            route_class=route_class,
            **kwargs
        )

    def _get_path_alias(self, path: str) -> typing.List[str]:

        _path = path.rstrip(r'/')

        if not self.prefix and not _path:
            return [path]

        _path_split = os.path.splitext(_path)

        if _path_split[1]:
            return [_path]

        return [_path, _path + r'/']

    def api_route(self, path: str, *args, **kwargs) -> typing.Callable:

        def _decorator(func):

            for index, _path in enumerate(self._get_path_alias(path)):

                self.add_api_route(_path, func, *args, **kwargs)

                # 兼容的URL将不会出现在docs中
                if index == 0:
                    kwargs[r'include_in_schema'] = False

            return func

        return _decorator


class Request(fastapi.Request):

    def __init__(self, scope: Scope, receive: Receive, send: Send, api_route: APIRoute):

        super().__init__(scope, receive, send)

        self._api_route: APIRoute = api_route

    @property
    def debug_info(self) -> typing.Dict[str, str]:

        return {
            'trace_id': get_trace_id(),
            'type': self.scope.get(r'type'),
            'http_version': self.scope.get(r'http_version'),
            'server': self.scope.get(r'server'),
            'client': self.scope.get(r'client'),
            'scheme': self.scope.get(r'scheme'),
            'method': self.scope.get(r'method'),
            'root_path': self.scope.get(r'root_path'),
            'path': self.scope.get(r'path'),
            'query_string': self.scope.get(r'query_string'),
            'headers': self.scope.get(r'headers'),
        }

    @property
    def route(self) -> APIRoute:

        return self._api_route

    @property
    def path(self) -> str:

        return self._api_route.path

    @property
    def tags(self) -> typing.List[typing.Union[str, Enum]]:

        return self._api_route.tags

    @property
    def referer(self) -> str:

        return self.headers.get(r'Referer')

    @property
    def client_ip(self) -> str:

        if self.x_forwarded_for:
            return self.x_forwarded_for[0]
        else:
            return self.client_host

    @property
    def client_host(self) -> str:

        return self.headers.get(r'X-Real-IP', self.client.host)

    @property
    def x_forwarded_for(self) -> typing.List[str]:

        return Utils.split_str(self.headers.get(r'X-Forwarded-For', r''), r',')

    @property
    def content_type(self) -> str:

        return self.headers.get(r'Content-Type')

    @property
    def content_length(self) -> int:

        result = self.headers.get(r'Content-Length', r'')

        return int(result) if result.isdigit() else 0

    def get_header(self, name: str, default: typing.Optional[str] = None) -> str:

        return self.headers.get(name, default)


async def http_exception_handler(
        _: Request, exc: HTTPException
) -> ErrorResponse:

    headers = getattr(exc, r'headers', None)

    if headers:
        return ErrorResponse(
            -1,
            content={r'detail': exc.detail},
            status_code=exc.status_code,
            headers=headers
        )
    else:
        return ErrorResponse(
            -1,
            content={r'detail': exc.detail},
            status_code=exc.status_code
        )


async def request_validation_exception_handler(
        _: Request, exc: RequestValidationError
) -> ErrorResponse:

    return ErrorResponse(
        -1,
        content={r'detail': jsonable_encoder(exc.errors())},
        status_code=HTTP_422_UNPROCESSABLE_ENTITY,
    )
