import dataclasses
import json
import uuid
from datetime import timedelta, datetime, UTC
from typing import Callable, Optional, TYPE_CHECKING, Union, Literal

from cryptography.fernet import Fernet
from fastapi import Request
from fastapi.security import APIKeyCookie
from jose import jwt, JWTError
from starlette.authentication import AuthenticationError

from fastapi_identity.authentication.base import AuthenticationBackend
from fastapi_identity.claims import ClaimsPrincipal, ClaimTypes, Claim
from fastapi_identity.utils import asdict

if TYPE_CHECKING:
    from fastapi_identity.http_context import HttpContext


@dataclasses.dataclass
class CookieOptions:
    max_age: Optional[int] = None
    path: str = "/"
    domain: Optional[str] = None
    secure: bool = False
    httponly: bool = False
    samesite: Optional[Literal["lax", "strict", "none"]] = "lax"


class CookieAuthenticationBackend(AuthenticationBackend):
    def __init__(
            self,
            secret: str,
            name: str = ".fastapi.identity.auth",
            expires: timedelta = timedelta(days=14),
            *,
            configure_cookie_options: Callable[[CookieOptions], None] = None,
            valid_audience: str = "@LOCALHOST AUTHORITY",
            claim_prefix: str = "__fastapi.identity.claim.",
            encrypt_cookie_key: Optional[Union[bytes, str]] = None
    ):
        super().__init__(APIKeyCookie(name=name, auto_error=False), secret)
        self.name = name
        self.expires = expires
        self.valid_audience = valid_audience
        self.cookie_options = CookieOptions()
        self.claim_prefix = claim_prefix
        self.fernet = Fernet(encrypt_cookie_key) if encrypt_cookie_key is not None else None
        if configure_cookie_options is not None:
            configure_cookie_options(self.cookie_options)

    async def _authenticate(self, request: Request, token: str) -> ClaimsPrincipal:
        try:
            jwt.decode(token, self._secret, algorithms='HS256', audience=self.valid_audience)
        except JWTError:
            raise AuthenticationError()

        principal = ClaimsPrincipal()

        for cname, cvalue in request.cookies.items():
            if cname.startswith(self.claim_prefix):
                principal.add_claims(Claim.load(json.loads(self.decode_cookie(cvalue))))

        return principal

    async def sign_in(self, context: 'HttpContext', user: ClaimsPrincipal) -> None:
        await self.sign_out(context)
        context.response.headers.append('Cache-Control', 'no-cache')
        expires = datetime.now(UTC) + self.expires
        data = {
            'aud': self.valid_audience,
            'sub': user.find_first_value(ClaimTypes.NameIdentifier)
        }
        token = jwt.encode(data, self._secret)
        context.response.set_cookie(self.name, token, expires=expires, **asdict(self.cookie_options))

        for claim in user.claims:
            context.response.set_cookie(
                key=self._generate_cookie_name(),
                value=self.encode_cookie(json.dumps(claim.dump())),
                expires=expires,
                **asdict(self.cookie_options)
            )

    async def sign_out(self, context: 'HttpContext') -> None:
        context.response.delete_cookie(self.name)
        self._remove_cookie_claims(context)

    def encode_cookie(self, value: Union[bytes, str]) -> str:
        if self.fernet is not None:
            if isinstance(value, str):
                value = value.encode()
            return self.fernet.encrypt(value).decode()
        return value

    def decode_cookie(self, data: Union[bytes, str]) -> str:
        if self.fernet is not None:
            return self.fernet.decrypt(data).decode()
        return data

    def _generate_cookie_name(self) -> str:
        return self.claim_prefix + str(uuid.uuid4())

    def _remove_cookie_claims(self, context: 'HttpContext'):
        for cname, cvalue in context.request.cookies.items():
            if cname.startswith(self.claim_prefix):
                context.response.delete_cookie(key=cname)
