from typing import Union, Optional

from fastapi import Depends

from fastapi_identity.authorization.handler_context import AuthorizationHandlerContext
from fastapi_identity.authorization.exc import AuthorizationError
from fastapi_identity.authorization.policy_builder import AuthorizationPolicyBuilder
from fastapi_identity.authorization.authorization_provider import AuthorizationProvider
from fastapi_identity.exc import InvalidOperationException

__all__ = ("authorize",)


async def _check_roles(
        roles: Union[set[str], str],
        context: AuthorizationHandlerContext
):
    if context.user is None:
        raise AuthorizationError()

    if isinstance(roles, str):
        roles = set(roles.replace(' ', '').split(','))

    result = any([context.user.is_in_role(r) for r in roles])

    if not result:
        raise AuthorizationError()


async def _check_policy(
        policy: str,
        context: AuthorizationHandlerContext,
        provider: AuthorizationProvider
):
    _policy = provider.get_policy(policy)

    if _policy is None:
        raise InvalidOperationException()

    for req in _policy.requirements:
        await req.handle(context)

    if not context.has_succeeded:
        raise AuthorizationError()


def authorize(
        *,
        roles: Optional[Union[set[str], str]] = None,
        policy: Optional[str] = None
):
    async def wrapped(
            context: AuthorizationHandlerContext = Depends(),
            provider: AuthorizationProvider = Depends()
    ):
        if not roles and not policy:
            if not context.is_authenticated:
                raise AuthorizationError()

        if roles:
            await _check_roles(roles, context)
            return

        if policy:
            await _check_policy(policy, context, provider)

    return wrapped
