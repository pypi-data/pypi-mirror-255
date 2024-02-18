from fastapi_identity.resources import Resources
from fastapi_identity.identity_error import IdentityError
from fastapi_identity.utils import funcname


def _create_error(code, *args):
    return IdentityError(
        code,
        Resources[code].format(*args)
    )


class IdentityErrorDescriber:
    """Service to enable localization for application facing identity errors."""

    @staticmethod
    def DefaultError():
        return _create_error(funcname())

    @staticmethod
    def DuplicateEmail(email: str):
        return _create_error(funcname(), email)

    @staticmethod
    def DuplicateRoleName(name: str):
        return _create_error(funcname(), name)

    @staticmethod
    def DuplicateUserName(name: str):
        return _create_error(funcname(), name)

    @staticmethod
    def InvalidEmail(email: str):
        return _create_error(funcname(), email)

    @staticmethod
    def InvalidRoleName(name: str):
        return _create_error(funcname(), name)

    @staticmethod
    def InvalidDomain(domain: str):
        return _create_error(funcname(), domain)

    @staticmethod
    def InvalidToken():
        return _create_error(funcname())

    @staticmethod
    def InvalidUserName(name: str):
        return _create_error(funcname(), name)

    @staticmethod
    def LoginAlreadyAssociated():
        return _create_error(funcname())

    @staticmethod
    def NullSecurityStamp():
        return _create_error(funcname())

    @staticmethod
    def PasswordMismatch():
        return _create_error(funcname())

    @staticmethod
    def PasswordRequiresDigit():
        return _create_error(funcname())

    @staticmethod
    def PasswordRequiresLower():
        return _create_error(funcname())

    @staticmethod
    def PasswordRequiresNonAlphanumeric():
        return _create_error(funcname())

    @staticmethod
    def PasswordRequiresUpper():
        return _create_error(funcname())

    @staticmethod
    def PasswordTooShort(length: int):
        return _create_error(funcname(), length)

    @staticmethod
    def PasswordRequiresUniqueChars(unique_chars: int):
        return _create_error(funcname(), unique_chars)

    @staticmethod
    def RoleNotFound(name: str):
        return _create_error(funcname(), name)

    @staticmethod
    def RecoveryCodeRedemptionFailed():
        return _create_error(funcname())

    @staticmethod
    def UserAlreadyHasPassword():
        return _create_error(funcname())

    @staticmethod
    def UserAlreadyInRole(name: str):
        return _create_error(funcname(), name)

    @staticmethod
    def UserLockedOut():
        return _create_error(funcname())

    @staticmethod
    def UserLockoutNotEnabled():
        return _create_error(funcname())

    @staticmethod
    def UserNameNotFound(name: str):
        return _create_error(funcname(), name)

    @staticmethod
    def UserNotInRole(name: str):
        return _create_error(funcname(), name)
