from datetime import datetime, timedelta, UTC
from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Generic, override

from jose import jwt, JWTError

from fastapi_identity.exc import ArgumentNoneException
from fastapi_identity.rfc6238service import Rfc6238AuthenticationService
from fastapi_identity.types import TUser
from fastapi_identity.utils import isnull

if TYPE_CHECKING:
    from fastapi_identity.user_manager import UserManager


class IUserTwoFactorTokenProvider(Generic[TUser], ABC):
    """Provides an abstraction for token generators."""

    @abstractmethod
    async def generate(self, manager: 'UserManager[TUser]', purpose: str, user: TUser) -> str:
        """
        Generates a token for the specified user and purpose.

        :param manager:
        :param purpose: The purpose the token will be used for.
        :param user: The user a token should be generated for.
        :return:
        """

    @abstractmethod
    async def validate(self, manager: 'UserManager[TUser]', purpose: str, token: str, user: TUser) -> bool:
        """
        Returns a flag indicating whether the specified token is valid for the given user and purpose.

        :param manager:
        :param purpose: The purpose the token will be used for.
        :param token: The token to validate.
        :param user: The user a token should be validated for.
        :return:
        """

    @abstractmethod
    async def can_generate_two_factor(self, manager: 'UserManager[TUser]', user: TUser) -> bool:
        """
        Returns a flag indicating whether the token provider can generate a token suitable for two-factor authentication
        token for the specified user.

        :param manager: The UserManager[TUser] that can be used to retrieve user properties.
        :param user: The user a token could be generated for.
        :return:
        """


class TotpSecurityStampBasedTokenProvider(IUserTwoFactorTokenProvider[TUser], Generic[TUser]):

    @abstractmethod
    async def can_generate_two_factor(self, manager: 'UserManager[TUser]', user: TUser) -> bool:
        pass

    async def generate(self, manager: 'UserManager[TUser]', purpose: str, user: TUser) -> str:
        """
        Generates a token for the specified user and purpose.

        The purpose parameter allows a token generator to be used for multiple types of token whilst
        insuring a token for one purpose cannot be used for another. For example if you specified a purpose of "Email"
        and validated it with the same purpose a token with the purpose of TOTP would not pass the check even if it was
        for the same user.

        :param manager: The UserManager[TUser] that can be used to retrieve user properties.
        :param purpose: The purpose the token will be used for.
        :param user: The user a token should be generated for.
        :return:
        """
        if manager is None:
            raise ArgumentNoneException("manager")

        security_token = await manager.create_security_token(user)
        modifier = await self.get_user_modifier(manager, purpose, user)
        return Rfc6238AuthenticationService.generate_code(
            security_token,
            modifier,
            interval=manager.options.Tokens.TOTP_INTERVAL
        )

    async def validate(self, manager: 'UserManager[TUser]', purpose: str, token: str, user: TUser) -> bool:
        """
        Returns a flag indicating whether the specified token is valid for the given user and purpose.

        :param manager: The UserManager[TUser] that can be used to retrieve user properties.
        :param purpose: The purpose the token will be used for.
        :param token: The token to validate.
        :param user: The user a token should be validated for.
        :return:
        """
        if manager is None:
            raise ArgumentNoneException("manager")

        security_token = await manager.create_security_token(user)
        modifier = await self.get_user_modifier(manager, purpose, user)
        return security_token and Rfc6238AuthenticationService.validate_code(
            security_token,
            token,
            modifier,
            interval=manager.options.Tokens.TOTP_INTERVAL
        )

    async def get_user_modifier(self, manager: 'UserManager[TUser]', purpose: str, user: TUser):
        """
        Returns a constant, provider and user unique modifier used for entropy in generated tokens from user information.

        :param manager: The UserManager[TUser] that can be used to retrieve user properties.
        :param purpose: The purpose the token will be generated for.
        :param user: The user a token should be generated for.
        :return:
        """
        if manager is None:
            raise ArgumentNoneException("manager")

        user_id = await manager.get_user_id(user)
        return f"Totp:{purpose}:{user_id}".encode()


class EmailTokenProvider(TotpSecurityStampBasedTokenProvider[TUser], Generic[TUser]):
    """TokenProvider that generates tokens from the user's security stamp and notifies a user via email."""

    async def can_generate_two_factor(self, manager: 'UserManager[TUser]', user: TUser) -> bool:
        if manager is None:
            raise ArgumentNoneException("manager")

        email = await manager.get_email(user)
        return not isnull(email) and await manager.is_email_confirmed(user)

    @override
    async def get_user_modifier(self, manager: 'UserManager[TUser]', purpose: str, user: TUser):
        if manager is None:
            raise ArgumentNoneException("manager")

        email = await manager.get_email(user)
        return f"Email:{purpose}:{email}".encode()


class PhoneNumberTokenProvider(TotpSecurityStampBasedTokenProvider[TUser], Generic[TUser]):
    """Represents a token provider that generates tokens from a user's security stamp and
    sends them to the user via their phone number."""

    async def can_generate_two_factor(self, manager: 'UserManager[TUser]', user: TUser) -> bool:
        if manager is None:
            raise ArgumentNoneException("manager")

        phone_number = await manager.get_phone_number(user)
        return not isnull(phone_number) and await manager.is_phone_number_confirmed(user)

    @override
    async def get_user_modifier(self, manager: 'UserManager[TUser]', purpose: str, user: TUser):
        if manager is None:
            raise ArgumentNoneException("manager")

        phone_number = await manager.get_phone_number(user)
        return f"PhoneNumber:{purpose}:{phone_number}".encode()


class DefaultTokenProvider(TotpSecurityStampBasedTokenProvider[TUser], Generic[TUser]):
    """Represents a token provider that generates tokens from a user's security stamp and
    sends them to the user via their phone number."""

    async def can_generate_two_factor(self, manager: 'UserManager[TUser]', user: TUser) -> bool:
        return True

    @override
    async def generate(self, manager: 'UserManager[TUser]', purpose: str, user: TUser) -> str:
        if manager is None:
            raise ArgumentNoneException("manager")
        if user is None:
            raise ArgumentNoneException("user")

        stamp = await manager.get_security_stamp(user)
        user_id = await manager.get_user_id(user)
        payload = {
            "sub": user_id,
            "exp": datetime.now(UTC) + timedelta(seconds=manager.options.Tokens.TOTP_INTERVAL),
            "aud": purpose
        }
        return jwt.encode(payload, stamp)

    @override
    async def validate(self, manager: 'UserManager[TUser]', purpose: str, token: str, user: TUser) -> bool:
        if manager is None:
            raise ArgumentNoneException("manager")
        if user is None:
            raise ArgumentNoneException("user")

        user_id = await manager.get_user_id(user)
        stamp = await manager.get_security_stamp(user)
        try:
            jwt.decode(
                token,
                stamp,
                subject=user_id,
                audience=purpose
            )
            return True
        except JWTError:
            return False
