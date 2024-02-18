import re
from http.client import HTTPConnection
from typing import Optional, Callable, List, Union, Pattern

from starlette.authentication import AuthenticationError
from starlette.datastructures import URL
from starlette.requests import Request
from starlette.responses import Response, PlainTextResponse
from starlette.types import ASGIApp, Scope, Receive, Send

from fastapi_identity.authentication import AuthenticationBackend


class AuthenticationMiddleware:
    def __init__(
            self,
            app: ASGIApp,
            backend: AuthenticationBackend,
            allow_anonymous: Optional[List[Union[Pattern, str]]] = None,
            skip_error: bool = True,
            on_error: Optional[Callable[[HTTPConnection, AuthenticationError], Response]] = None
    ):
        self.app = app
        self.backend = backend
        self.skip_error = skip_error
        self.on_error = (on_error if on_error is not None else self.default_on_error)
        self.allow_anonymous = allow_anonymous or []
        for _item in self.allow_anonymous:
            if isinstance(_item, str):
                self.allow_anonymous.append(re.compile(_item))
            else:
                self.allow_anonymous.append(_item)

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] not in ["http", "websocket"]:
            await self.app(scope, receive, send)
            return

        request = Request(scope)
        try:
            principal = await self.backend.authenticate(request)
            scope['user'] = principal
            scope['auth'] = True
        except AuthenticationError as exc:
            if self.skip_error or self.__url_is_exempt(request.url):
                scope['user'] = None
                scope['auth'] = False
            else:
                response = self.on_error(request, exc)
                if scope["type"] == "websocket":
                    await send({"type": "websocket.close", "code": 1000})
                else:
                    await response(scope, receive, send)
                return

        await self.app(scope, receive, send)

    def __url_is_exempt(self, url: URL) -> bool:
        if not self.allow_anonymous:
            return False
        for exempt_url in self.allow_anonymous:
            if exempt_url.match(url.path):
                return True
        return False

    @staticmethod
    def default_on_error(request: Request, exc: Exception) -> Response:
        return PlainTextResponse(str(exc), status_code=401)
