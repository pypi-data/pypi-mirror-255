from abc import ABC, abstractmethod
from enum import Enum
from typing import Generic

from passlib.context import CryptContext

from fastapi_identity.exc import ArgumentNoneException
from fastapi_identity.types import TUser
from fastapi_identity.utils import isnull


class PasswordVerificationResult(Enum):
    """Specifies the results for password verification."""

    Failed = 0
    """Indicates password verification failed."""
    Success = 1
    """Indicates password verification was successful."""
    SuccessRehashNeeded = 2
    """Indicates password verification was successful however the password was encoded using a deprecated algorithm
    and should be rehashed and updated."""


class IPasswordHasher(Generic[TUser], ABC):
    """Provides an abstraction for hashing passwords."""

    @abstractmethod
    def hash_password(self, user: TUser, password: str) -> str:
        """
        Returns a hashed representation of the supplied password for the specified user.

        :param user: The user whose password is to be hashed.
        :param password: The password to hash.
        :return: A hashed representation of the supplied password for the specified user.
        """

    @abstractmethod
    def verify_hashed_password(self, user: TUser, hashed_password: str, password: str) -> PasswordVerificationResult:
        """
        Return`s the result of password verification.

        :param user: The user whose password should be verified.
        :param hashed_password: The hash password.
        :param password: The password to be verified.
        :return: A PasswordVerificationResult indicating the result of a password hash comparison.
        """


class PasswordHasher(IPasswordHasher[TUser], Generic[TUser]):
    """Implements the standard password hashing."""

    def __init__(self):
        self._crypt = CryptContext(schemes=["bcrypt"])

    def hash_password(self, user: TUser, password: str) -> str:
        if password is None:
            raise ArgumentNoneException("password")

        return self._crypt.hash(password)

    def verify_hashed_password(self, user: TUser, hashed_password: str, password: str) -> PasswordVerificationResult:
        if password is None or isnull(hashed_password):
            return PasswordVerificationResult.Failed

        if self._crypt.verify(password, hashed_password):
            if self._crypt.needs_update(hashed_password):
                return PasswordVerificationResult.SuccessRehashNeeded

            return PasswordVerificationResult.Success

        return PasswordVerificationResult.Failed
