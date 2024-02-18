from abc import ABC, abstractmethod
from typing import Optional, Callable, Union

from fastapi import Depends

from fastapi_identity.authorization.policy_builder import AuthorizationPolicyBuilder
from fastapi_identity.authorization.base import AuthorizationPolicy
from fastapi_identity.authorization.exc import AuthorizationError
from fastapi_identity.authorization.handler_context import AuthorizationHandlerContext
from fastapi_identity.exc import InvalidOperationException, ArgumentNoneException


class IAuthorizationProvider(ABC):
    @abstractmethod
    def get_policy(self, name: str) -> Optional[AuthorizationPolicy]:
        pass


class AuthorizationOptions:
    def __init__(self):
        self._policy_map: dict[str, AuthorizationPolicy] = {}

    def add_policy(self, name: str, configure_policy: Callable[[AuthorizationPolicyBuilder], None]):
        if not name:
            raise ArgumentNoneException('name')
        if configure_policy is None:
            raise ArgumentNoneException('configure_policy')

        builder = AuthorizationPolicyBuilder()
        configure_policy(builder)
        self._policy_map[name] = builder.build()


class AuthorizationProvider(IAuthorizationProvider):
    options: AuthorizationOptions

    def get_policy(self, name: str) -> Optional[AuthorizationPolicy]:
        if not name:
            raise ArgumentNoneException('name')

        return getattr(self.options, '_policy_map').get(name)



