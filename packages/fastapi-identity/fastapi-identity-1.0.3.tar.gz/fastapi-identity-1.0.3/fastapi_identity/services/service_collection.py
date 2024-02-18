from re import Pattern
from typing import Optional, Callable, Union

from fastapi import FastAPI, Request
from fastapi.responses import PlainTextResponse

from fastapi_identity.authentication import AuthenticationBackend, AuthenticationMiddleware
from fastapi_identity.authentication.cookies import CookieAuthenticationBackend
from fastapi_identity.authorization.exc import AuthorizationError
from fastapi_identity.authorization.authorization_provider import AuthorizationOptions, AuthorizationProvider
from fastapi_identity.exc import ArgumentNoneException
from fastapi_identity.http_context import HttpContext
from fastapi_identity.options import IdentityOptions
from fastapi_identity.depends import (
    get_error_describer,
    get_user_validator,
    get_password_validator,
    get_password_hasher,
    get_lookup_normalizer,
    get_role_validator,
    get_user_confirmation,
    get_user_manager,
    get_role_manager,
    get_claims_factory,
    get_signin_manager,
)
from fastapi_identity.depends import di
from fastapi_identity.services.identity_builder import IdentityBuilder
from fastapi_identity.stores import IUserStore, IRoleStore
from fastapi_identity.types import DependencyCallable
from fastapi_identity.utils import get_device_uuid


class ServiceCollection:
    def __init__(self, app: FastAPI):
        self.app = app
        self._dependencies = {}
        self._middlewares = {}

    def _add_service[TService, TFactory](
            self,
            _type: type[TService],
            _factory: DependencyCallable[TFactory]
    ):
        self._dependencies[_type] = _factory

    def add_identity[TUser, TRole](
            self,
            user: type[TUser],
            role: type[TRole],
            get_user_store: DependencyCallable[IUserStore[TUser]],
            get_role_store: DependencyCallable[IRoleStore[TRole]],
            setup_action: Optional[Callable[[IdentityOptions], None]] = None
    ) -> IdentityBuilder:
        if get_user_store is None:
            raise ArgumentNoneException('get_user_store')
        if get_role_store is None:
            raise ArgumentNoneException('get_role_store')

        self.add_authentication(backend=CookieAuthenticationBackend(get_device_uuid()))

        _options = IdentityOptions()

        if setup_action is not None:
            setup_action(_options)

        self._add_service(di.IdentityOptions, lambda: _options)
        self._add_service(di.IdentityErrorDescriber, get_error_describer)
        self._add_service(di.IUserStore, get_user_store)
        self._add_service(di.IRoleStore, get_role_store)
        self._add_service(di.IUserValidators, get_user_validator)
        self._add_service(di.IPasswordValidators, get_password_validator)
        self._add_service(di.IPasswordHasher, get_password_hasher)
        self._add_service(di.ILookupNormalizer, get_lookup_normalizer)
        self._add_service(di.IRoleValidators, get_role_validator)
        self._add_service(di.IUserConfirmation, get_user_confirmation)
        self._add_service(di.UserManager, get_user_manager)
        self._add_service(di.RoleManager, get_role_manager)
        self._add_service(di.IUserClaimsPrincipalFactory, get_claims_factory)
        self._add_service(di.SignInManager, get_signin_manager)

        return IdentityBuilder(user, role, self._dependencies)

    def add_authentication(
            self,
            backend: AuthenticationBackend,
            allow_anonymous: Optional[list[Union[Pattern, str]]] = None
    ):
        if backend is None:
            raise ArgumentNoneException('backend')

        self._middlewares[AuthenticationMiddleware] = {'backend': backend, 'allow_anonymous': allow_anonymous}
        HttpContext.backend = backend

    def add_authorization(
            self,
            configure: Optional[Callable[[AuthorizationOptions], None]] = None
    ):
        _options = AuthorizationOptions()

        if configure is not None:
            configure(_options)

        AuthorizationProvider.options = _options

        @self.app.exception_handler(AuthorizationError)
        async def authorization_exception_handler(request: Request, exc: AuthorizationError):
            return PlainTextResponse(str(exc), status_code=403)
