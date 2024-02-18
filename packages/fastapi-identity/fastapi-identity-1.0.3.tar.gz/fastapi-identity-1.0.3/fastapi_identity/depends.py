from fastapi import Depends

from fastapi_identity.confirmation import DefaultUserConfirmation
from fastapi_identity.error_describer import IdentityErrorDescriber
from fastapi_identity.http_context import HttpContext
from fastapi_identity.lookup_normalizer import UpperLookupNormalizer
from fastapi_identity.password_hasher import PasswordHasher
from fastapi_identity.password_validator import PasswordValidator
from fastapi_identity.role_manager import RoleManager
from fastapi_identity.role_validator import RoleValidator
from fastapi_identity.signin_manager import SignInManager
from fastapi_identity.user_claims_principal_factory import UserClaimsPrincipalFactory
from fastapi_identity.user_manager import UserManager
from fastapi_identity.user_validator import UserValidator


class di:
    class IdentityOptions:
        pass

    class IdentityErrorDescriber:
        pass

    class IUserStore:
        pass

    class IRoleStore:
        pass

    class IUserValidators:
        pass

    class IPasswordValidators:
        pass

    class IPasswordHasher:
        pass

    class ILookupNormalizer:
        pass

    class IRoleValidators:
        pass

    class IUserConfirmation:
        pass

    class IUserClaimsPrincipalFactory:
        pass

    class UserManager:
        pass

    class RoleManager:
        pass

    class SignInManager:
        pass


def get_error_describer():
    yield IdentityErrorDescriber()


def get_user_validator(errors=Depends(di.IdentityErrorDescriber)):
    yield [UserValidator(errors)]


def get_password_validator(errors=Depends(di.IdentityErrorDescriber)):
    yield [PasswordValidator(errors)]


def get_password_hasher():
    yield PasswordHasher()


def get_lookup_normalizer():
    yield UpperLookupNormalizer()


def get_role_validator(errors=Depends(di.IdentityErrorDescriber)):
    yield [RoleValidator(errors)]


def get_user_confirmation():
    yield DefaultUserConfirmation()


def get_user_manager(
        store=Depends(di.IUserStore),
        options=Depends(di.IdentityOptions),
        password_hasher=Depends(di.IPasswordHasher),
        password_validators=Depends(di.IPasswordValidators),
        user_validators=Depends(di.IUserValidators),
        key_normalizer=Depends(di.ILookupNormalizer),
        errors=Depends(di.IdentityErrorDescriber)
):
    yield UserManager(
        store,
        options=options,
        password_hasher=password_hasher,
        password_validators=password_validators,
        user_validators=user_validators,
        key_normalizer=key_normalizer,
        errors=errors
    )


def get_role_manager(
        store=Depends(di.IRoleStore),
        role_validators=Depends(di.IRoleValidators),
        key_normalizer=Depends(di.ILookupNormalizer),
        errors=Depends(di.IdentityErrorDescriber)
):
    yield RoleManager(
        store,
        role_validators=role_validators,
        key_normalizer=key_normalizer,
        errors=errors
    )


def get_claims_factory(
        user_manager=Depends(di.UserManager),
        role_manager=Depends(di.RoleManager)
):
    yield UserClaimsPrincipalFactory(user_manager, role_manager)


def get_signin_manager(
        context=Depends(HttpContext),
        user_manager=Depends(di.UserManager),
        claims_factory=Depends(di.IUserClaimsPrincipalFactory),
        confirmation=Depends(di.IUserConfirmation),
        options=Depends(di.IdentityOptions),
):
    yield SignInManager(
        user_manager,
        context=context,
        claims_factory=claims_factory,
        confirmation=confirmation,
        options=options
    )
