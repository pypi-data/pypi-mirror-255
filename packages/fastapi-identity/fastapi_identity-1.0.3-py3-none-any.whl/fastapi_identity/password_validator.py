from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Generic, Optional

from fastapi_identity.error_describer import IdentityErrorDescriber
from fastapi_identity.exc import ArgumentNoneException
from fastapi_identity.identity_result import IdentityResult
from fastapi_identity.types import TUser
from fastapi_identity.utils import isnull

if TYPE_CHECKING:
    from fastapi_identity.user_manager import UserManager


class IPasswordValidator(Generic[TUser], ABC):
    """Provides an abstraction for validating passwords."""

    @abstractmethod
    async def validate(self, manager: 'UserManager[TUser]', password: str) -> IdentityResult:
        """
        Validates a password.

        :param manager: The UserManager[TUser] that can be used to retrieve user properties.
        :param password: The password supplied for validation.
        :return:
        """


class PasswordValidator(IPasswordValidator[TUser], Generic[TUser]):
    """Provides the default password policy for Identity."""

    def __init__(self, errors: Optional[IdentityErrorDescriber] = None):
        """

        :param errors: The IdentityErrorDescriber used to provider error messages.
        """
        self._describer = errors or IdentityErrorDescriber()

    async def validate(self, manager: 'UserManager[TUser]', password: str) -> IdentityResult:
        if manager is None:
            raise ArgumentNoneException("manager")
        if password is None:
            raise ArgumentNoneException("password")

        options = manager.options.Password
        errors = []

        if isnull(password) or len(password) < options.REQUIRED_LENGTH:
            errors.append(self._describer.PasswordTooShort(options.REQUIRED_LENGTH))

        if options.REQUIRE_DIGIT and not any(self._is_digit(c) for c in password):
            errors.append(self._describer.PasswordRequiresDigit())

        if options.REQUIRE_LOWERCASE and not any(self._is_lower(c) for c in password):
            errors.append(self._describer.PasswordRequiresLower())

        if options.REQUIRE_UPPERCASE and not any(self._is_upper(c) for c in password):
            errors.append(self._describer.PasswordRequiresUpper())

        if options.REQUIRE_NON_ALPHANUMERIC and all(self._is_letter_or_digit(c) for c in password):
            errors.append(self._describer.PasswordRequiresNonAlphanumeric())

        if options.REQUIRED_UNIQUE_CHARS >= 1 and len(set(password)) < options.REQUIRED_UNIQUE_CHARS:
            errors.append(self._describer.PasswordRequiresUniqueChars(options.REQUIRED_UNIQUE_CHARS))

        if len(errors) == 0:
            return IdentityResult.success()

        return IdentityResult.failed(*errors)

    def _is_lower(self, c: str) -> bool:  # noqa
        return 'a' <= c <= 'z'

    def _is_digit(self, c: str) -> bool:  # noqa
        return '0' <= c <= '9'

    def _is_upper(self, c: str) -> bool:  # noqa
        return 'A' <= c <= 'Z'

    def _is_letter_or_digit(self, c: str) -> bool:
        return self._is_lower(c) or self._is_upper(c) or self._is_digit(c)
