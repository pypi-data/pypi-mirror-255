import dataclasses
from abc import abstractmethod
from datetime import timedelta
from typing import Callable, cast, TYPE_CHECKING

from fastapi import Request
from fastapi.security.base import SecurityBase
from starlette.authentication import AuthenticationError

from fastapi_identity.claims import ClaimsPrincipal

if TYPE_CHECKING:
    from fastapi_identity.http_context import HttpContext


@dataclasses.dataclass
class TokenAuthenticationOptions:
    audience: str = "@LOCALHOST AUTHORITY"
    issuer: str = "@LOCALHOST AUTHORITY"
    expires: timedelta = timedelta(minutes=15)


class AuthenticationBackend:
    def __init__(
            self,
            scheme: SecurityBase,
            secret: str
    ):
        self.scheme = cast(Callable, scheme)
        self._secret = secret

    async def authenticate(self, request: Request) -> ClaimsPrincipal:
        token: str = await self.scheme(request)
        if not token:
            raise AuthenticationError()
        return await self._authenticate(request, token)

    @abstractmethod
    async def _authenticate(self, request: Request, token: str) -> ClaimsPrincipal:
        pass

    @abstractmethod
    async def sign_in(self, context: 'HttpContext', user: ClaimsPrincipal) -> None:
        pass

    @abstractmethod
    async def sign_out(self, context: 'HttpContext') -> None:
        pass
