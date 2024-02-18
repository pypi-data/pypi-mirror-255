from abc import ABC, abstractmethod
from typing import Generic, TYPE_CHECKING

from fastapi_identity.claims import ClaimsPrincipal, Claim, ClaimTypes
from fastapi_identity.exc import ArgumentNoneException
from fastapi_identity.types import TUser, TRole

if TYPE_CHECKING:
    from fastapi_identity.user_manager import UserManager
    from fastapi_identity.role_manager import RoleManager


class IUserClaimsPrincipalFactory(Generic[TUser], ABC):
    """Provides an abstraction for a factory to create a ClaimsPrincipal from a user."""

    @abstractmethod
    async def create(self, user: TUser) -> ClaimsPrincipal:
        """
        Creates a ClaimsPrincipal from an user.

        :param user: The user to create a ClaimsPrincipal from.
        :return:
        """


class UserClaimsPrincipalFactory(IUserClaimsPrincipalFactory[TUser], Generic[TUser]):
    def __init__(
            self,
            user_manager: 'UserManager[TUser]',
            role_manager: 'RoleManager[TRole]'
    ):
        self.user_manager = user_manager
        self.role_manager = role_manager

    async def create(self, user: TUser) -> ClaimsPrincipal:
        if not user:
            raise ArgumentNoneException("user")

        user_id = await self.user_manager.get_user_id(user=user)
        username = await self.user_manager.get_username(user=user)
        principal = ClaimsPrincipal()
        principal.add_claims(
            Claim(ClaimTypes.NameIdentifier, user_id),
            Claim(ClaimTypes.Name, username)
        )

        if self.user_manager.supports_user_email:
            if email := await self.user_manager.get_email(user):
                principal.add_claims(Claim(ClaimTypes.Email, email))

        if self.user_manager.supports_user_security_stamp:
            if security := await self.user_manager.get_security_stamp(user):
                principal.add_claims(Claim(ClaimTypes.SecurityStamp, security))

        if self.user_manager.supports_user_claim:
            if claims := await self.user_manager.get_claims(user):
                principal.add_claims(*claims)

        if self.user_manager.supports_user_role:
            roles = await self.user_manager.get_roles(user)
            for role_name in roles:
                principal.add_claims(Claim(ClaimTypes.Role, role_name))

        return principal
