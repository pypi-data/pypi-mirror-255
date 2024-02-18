import re
from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Generic, Optional
from email_validator import validate_email, EmailNotValidError

from fastapi_identity.error_describer import IdentityErrorDescriber
from fastapi_identity.exc import ArgumentNoneException
from fastapi_identity.identity_result import IdentityResult
from fastapi_identity.types import TUser
from fastapi_identity.utils import isnull

if TYPE_CHECKING:
    from fastapi_identity.user_manager import UserManager

email_pattern = re.compile(r"^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}$")


class IUserValidator(Generic[TUser], ABC):
    """Provides an abstraction for user validation."""

    @abstractmethod
    async def validate(self, manager: 'UserManager[TUser]', user: TUser) -> IdentityResult:
        """
        Validates the specified user.

        :param manager: The UserManager[TUser] that can be used to retrieve user properties.
        :param user: The user to validate.
        :return:
        """


class UserValidator(IUserValidator[TUser], Generic[TUser]):
    """Provides validation services for user classes."""

    def __init__(self, errors: Optional[IdentityErrorDescriber] = None):
        """

        :param errors: The IdentityErrorDescriber used to provider error messages.
        """
        self._describer = errors or IdentityErrorDescriber()

    async def validate(self, manager: 'UserManager[TUser]', user: TUser) -> IdentityResult:
        if manager is None:
            raise ArgumentNoneException("manager")
        if user is None:
            raise ArgumentNoneException("user")

        options = manager.options.User
        errors = []

        await self._validate_username(manager, user, errors)

        if options.REQUIRE_UNIQUE_EMAIL:
            await self._validate_email(manager, user, errors)

        if not errors:
            return IdentityResult.success()

        return IdentityResult.failed(*errors)

    async def _validate_username(self, manager: 'UserManager[TUser]', user: TUser, errors):
        username = await manager.get_username(user)

        if isnull(username):
            errors.append(self._describer.InvalidUserName(username))
            return

        options = manager.options.User

        if (
                not options.ALLOWED_USERNAME_CHARACTERS.isspace() and
                any(c not in options.ALLOWED_USERNAME_CHARACTERS for c in username)
        ):
            errors.append(self._describer.InvalidUserName(username))
            return

        owner = await manager.find_by_name(username)

        if owner and (await manager.get_user_id(owner) != await manager.get_user_id(user)):
            errors.append(self._describer.DuplicateUserName(username))

    async def _validate_email(self, manager: 'UserManager[TUser]', user: TUser, errors: list):
        email = await manager.get_email(user)

        if isnull(email):
            errors.append(self._describer.InvalidEmail(email))
            return

        try:
            result = validate_email(email, check_deliverability=False)
        except EmailNotValidError as ex:
            errors.append(self._describer.InvalidEmail(email))
            return

        options = manager.options.User

        if options.ALLOWED_EMAIL_DOMAIN:
            if result.domain not in options.ALLOWED_EMAIL_DOMAIN:
                errors.append(self._describer.InvalidDomain(result.domain))
                return

        owner = await manager.find_by_email(email)

        if owner and (await manager.get_user_id(owner) != await manager.get_user_id(user)):
            errors.append(self._describer.DuplicateEmail(email))
