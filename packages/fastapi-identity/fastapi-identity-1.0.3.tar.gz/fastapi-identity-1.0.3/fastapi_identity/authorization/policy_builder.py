from typing import Awaitable, Callable

from fastapi_identity.authorization.handler_context import AuthorizationHandlerContext
from fastapi_identity.exc import ArgumentNoneException
from fastapi_identity.authorization.base import AuthorizationHandler, AuthorizationPolicy


class RolesAuthorizationRequirement(AuthorizationHandler):
    def __init__(self, *allowed_roles: str):
        if not allowed_roles:
            raise ArgumentNoneException('allowed_roles')

        self.allowed_roles = allowed_roles

    async def handle(self, context: AuthorizationHandlerContext):
        if context.user is not None:
            found = any([context.user.is_in_role(r) for r in self.allowed_roles])

            if found:
                context.succeed()


class ClaimsAuthorizationRequirement(AuthorizationHandler):
    def __init__(self, claim_type: str, *allowed_values: str):
        if not allowed_values:
            raise ArgumentNoneException('allowed_values')

        self.claim_type = claim_type
        self.allowed_values = allowed_values

    async def handle(self, context: AuthorizationHandlerContext):
        if context.user is not None:
            if not self.allowed_values:
                found = any([c.type == self.claim_type for c in context.user.claims])
            else:
                found = any([
                    c.type == self.claim_type and
                    c.value in self.allowed_values
                    for c in context.user.claims
                ])

            if found:
                context.succeed()


class NameAuthorizationRequirement(AuthorizationHandler):
    def __init__(self, required_name: str):
        self.required_name = required_name

    async def handle(self, context: AuthorizationHandlerContext):
        if self.required_name == context.user.name:
            context.succeed()


class AssertionRequirement(AuthorizationHandler):
    def __init__(self, handler: Callable[[AuthorizationHandlerContext], Awaitable[bool]]):
        self.handler = handler

    async def handle(self, context: AuthorizationHandlerContext):
        if await self.handler(context):
            context.succeed()


class DenyAnonymousAuthorizationRequirement(AuthorizationHandler):
    async def handle(self, context: AuthorizationHandlerContext):
        if context.is_authenticated:
            context.succeed()


class AuthorizationPolicyBuilder:
    def __init__(self):
        self.requirements: list[AuthorizationHandler] = []

    def add_requirements(self, *requirements: AuthorizationHandler) -> 'AuthorizationPolicyBuilder':
        if not requirements:
            raise ArgumentNoneException('requirements')
        self.requirements.extend(requirements)
        return self

    def require_claim(self, claim_type: str, *allowed_values) -> 'AuthorizationPolicyBuilder':
        if not allowed_values:
            raise ArgumentNoneException('allowed_values')
        self.requirements.append(ClaimsAuthorizationRequirement(claim_type, *allowed_values))
        return self

    def require_role(self, *roles: str) -> 'AuthorizationPolicyBuilder':
        if not roles:
            raise ArgumentNoneException('roles')
        self.requirements.append(RolesAuthorizationRequirement(*roles))
        return self

    def require_assertion(
            self,
            handler: Callable[[AuthorizationHandlerContext], Awaitable[bool]]
    ) -> 'AuthorizationPolicyBuilder':
        if handler is None:
            raise ArgumentNoneException('handler')
        self.requirements.append(AssertionRequirement(handler))
        return self

    def require_authenticated_user(self):
        self.requirements.append(DenyAnonymousAuthorizationRequirement())
        return self

    def build(self) -> AuthorizationPolicy:
        return AuthorizationPolicy(self.requirements)
