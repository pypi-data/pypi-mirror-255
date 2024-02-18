import dataclasses
from datetime import timedelta, datetime, UTC
from typing import Callable, TYPE_CHECKING, Any

from fastapi import Request
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from starlette.authentication import AuthenticationError
from starlette.responses import JSONResponse

from fastapi_identity.authentication.base import AuthenticationBackend
from fastapi_identity.claims import ClaimsPrincipal, ClaimTypes, Claim
from fastapi_identity.utils import asdict

if TYPE_CHECKING:
    from fastapi_identity.http_context import HttpContext


@dataclasses.dataclass
class TokenValidationParameters:
    verify_signature: bool = True
    verify_aud: bool = True
    verify_iat: bool = True
    verify_exp: bool = True
    verify_nbf: bool = True
    verify_iss: bool = True
    verify_sub: bool = True
    verify_jti: bool = True
    verify_at_hash: bool = True
    require_aud: bool = True
    require_iat: bool = False
    require_exp: bool = True
    require_nbf: bool = False
    require_iss: bool = True
    require_sub: bool = False
    require_jti: bool = False
    require_at_hash: bool = False
    leeway: int = 60


@dataclasses.dataclass
class BaseAccessToken:
    iss: str = None
    sub: str = None
    aud: str = None
    exp: datetime = None
    nbf: datetime = None
    iat: datetime = None
    jti: str = None


class BearerAuthenticationBackend(AuthenticationBackend):
    def __init__(
            self,
            secret: str,
            tokenUrl: str,
            expires: timedelta = timedelta(minutes=5),
            *,
            configure_validation_parameters: Callable[[TokenValidationParameters], None] = None,
            token_data_factory: Callable[[ClaimsPrincipal], dict[str, Any]] = None,
            valid_audience: str = "@LOCALHOST AUTHORITY",
            valid_issuer: str = "@LOCALHOST AUTHORITY"
    ):
        super().__init__(OAuth2PasswordBearer(tokenUrl=tokenUrl, auto_error=False), secret)
        self.expires = expires
        self.valid_audience = valid_audience
        self.valid_issuer = valid_issuer
        self.token_validation_parameters = TokenValidationParameters()
        if configure_validation_parameters is not None:
            configure_validation_parameters(self.token_validation_parameters)
        self.token_data_factory = token_data_factory

    async def _authenticate(self, request: Request, token: str) -> ClaimsPrincipal:
        try:
            payload = jwt.decode(
                token,
                self._secret,
                algorithms='HS256',
                options=asdict(self.token_validation_parameters),
                audience=self.valid_audience,
                issuer=self.valid_issuer
            )
        except JWTError:
            raise AuthenticationError()

        principal = ClaimsPrincipal(
            *[Claim.load(claim) for claim in payload.get('claims')],
            *[Claim.load(claim) for claim in payload.get('roles')]
        )
        return principal

    async def sign_in(self, context: 'HttpContext', user: ClaimsPrincipal) -> None:
        data = self.token_data_factory(user) if self.token_data_factory is not None else {}
        expires = datetime.now(UTC) + self.expires
        roles, other_claims = user.dump()
        data.update({
            'exp': expires,
            'aud': self.valid_audience,
            'sub': user.find_first_value(ClaimTypes.NameIdentifier),
            'roles': roles,
            'claims': other_claims
        })
        token = jwt.encode(data, self._secret)
        context.response = JSONResponse({'access_token': token, 'token_type': 'bearer'})

    async def sign_out(self, context: 'HttpContext') -> None:
        pass
