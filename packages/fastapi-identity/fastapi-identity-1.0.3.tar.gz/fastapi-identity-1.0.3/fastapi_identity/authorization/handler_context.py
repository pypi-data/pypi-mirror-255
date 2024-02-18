from typing import Optional

from fastapi.requests import Request

from fastapi_identity.claims import ClaimsPrincipal


class AuthorizationHandlerContext:
    def __init__(self, request: Request):
        self._request = request
        self._fail_called = False
        self._succeeded_called = False

    @property
    def user(self) -> Optional[ClaimsPrincipal]:
        return self._request.user

    @property
    def is_authenticated(self) -> bool:
        return self._request.auth

    @property
    def has_succeeded(self) -> bool:
        return not self._fail_called and self._succeeded_called

    def fail(self):
        self._fail_called = True

    def succeed(self):
        self._succeeded_called = True
