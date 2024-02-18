LOCALISATION: str = "en-US"

_RESOURCES: dict[str, dict[str, str]] = {
    'DefaultError': {
        'en-US': "An unknown failure has occurred.",
        'ru-RU': "Произошел неизвестный сбой."
    },
    'DuplicateEmail': {
        'en-US': "Email '{0}' is already taken.",
        'ru-RU': "Email '{0}' уже занят."
    },
    'DuplicateRoleName': {
        'en-US': "Role name '{0}' is already taken.",
        'ru-RU': "Имя роли '{0}' уже занято."
    },
    'DuplicateUserName': {
        'en-US': "Username '{0}' is already taken.",
        'ru-RU': "Имя пользователя '{0}' уже занято."
    },
    'InvalidEmail': {
        'en-US': "Email '{0}' is invalid.",
        'ru-RU': "Email '{0}' недействителен."
    },
    'InvalidRoleName': {
        'en-US': "Role name '{0}' is invalid.",
        'ru-RU': "Имя роли '{0}' недопустимо."
    },
    'InvalidDomain': {
        'en-US': "Emails from the specified domain '{0}' are prohibited.",
        'ru-RU': "Email из указанного домена '{0}' запрещены."
    },
    'InvalidToken': {
        'en-US': "Invalid token.",
        'ru-RU': "Недопустимый токен."
    },
    'InvalidUserName': {
        'en-US': "Username '{0}' is invalid, can only contain letters or digits.",
        'ru-RU': "Имя пользователя '{0}' недопустимо, может содержать только буквы или цифры."
    },
    'LoginAlreadyAssociated': {
        'en-US': "A user with this login already exists.",
        'ru-RU': "Пользователь с этим логином уже существует."
    },
    'NoTokenProvider': {
        'en-US': "No IUserTwoFactorTokenProvider[TUser] named '{0}' is registered.",
        'ru-RU': "Не зарегистрирован IUserTwoFactorTokenProvider[TUser] с именем '{0}'."
    },
    'NullSecurityStamp': {
        'en-US': "User security stamp cannot be null.",
        'ru-RU': "Отметка безопасности пользователя не может быть нулевой."
    },
    'PasswordMismatch': {
        'en-US': "Incorrect password.",
        'ru-RU': "Неверный пароль."
    },
    'PasswordRequiresDigit': {
        'en-US': "Passwords must have at least one digit.",
        'ru-RU': "Пароль должен содержать по крайней мере одну цифру."
    },
    'PasswordRequiresLower': {
        'en-US': "Passwords must have at least one lowercase.",
        'ru-RU': "Пароль должен содержать по крайней мере один символ в нижнем регистре."
    },
    'PasswordRequiresNonAlphanumeric': {
        'en-US': "Passwords must have at least one non alphanumeric character.",
        'ru-RU': "Пароль должен содержать по крайней мере один не алфавитно-цифровой символ."
    },
    'PasswordRequiresUpper': {
        'en-US': "Passwords must have at least one uppercase.",
        'ru-RU': "Пароль должен содержать по крайней мере один символ в верхнем регистре."
    },
    'PasswordTooShort': {
        'en-US': "Passwords must be at least {0} characters.",
        'ru-RU': "Пароль должен содержать не менее {0} символов."
    },
    'RoleNotFound': {
        'en-US': "Role {0} does not exist.",
        'ru-RU': "Роль {0} не существует."
    },
    'StoreNotIUserAuthenticationTokenStore': {
        'en-US': "Store does not implement IUserAuthenticationTokenStore[TUser].",
        'ru-RU': "Store не реализует IUserAuthenticationTokenStore[TUser]."
    },
    'StoreNotIUserClaimStore': {
        'en-US': "Store does not implement IUserClaimStore[TUser].",
        'ru-RU': "Store не реализует IUserClaimStore[TUser]."
    },
    'StoreNotIUserConfirmationStore': {
        'en-US': "Store does not implement IUserConfirmationStore[TUser].",
        'ru-RU': "Store не реализует IUserConfirmationStore[TUser]."
    },
    'StoreNotIUserEmailStore': {
        'en-US': "Store does not implement IUserEmailStore[TUser].",
        'ru-RU': "Store не реализует IUserEmailStore[TUser]."
    },
    'StoreNotIUserLockoutStore': {
        'en-US': "Store does not implement IUserLockoutStore[TUser].",
        'ru-RU': "Store не реализует IUserLockoutStore[TUser]."
    },
    'StoreNotIUserLoginStore': {
        'en-US': "Store does not implement IUserLoginStore[TUser].",
        'ru-RU': "Store не реализует IUserLoginStore[TUser]."
    },
    'StoreNotIUserPasswordStore': {
        'en-US': "Store does not implement IUserPasswordStore[TUser].",
        'ru-RU': "Store не реализует IUserPasswordStore[TUser]."
    },
    'StoreNotIUserPhoneNumberStore': {
        'en-US': "Store does not implement IUserPhoneNumberStore[TUser].",
        'ru-RU': "Store не реализует IUserPhoneNumberStore[TUser]."
    },
    'StoreNotIUserRoleStore': {
        'en-US': "Store does not implement IUserRoleStore[TUser].",
        'ru-RU': "Store не реализует IUserRoleStore[TUser]."
    },
    'StoreNotIUserSecurityStampStore': {
        'en-US': "Store does not implement IUserSecurityStampStore[TUser].",
        'ru-RU': "Store не реализует IUserSecurityStampStore[TUser]."
    },
    'StoreNotIUserAuthenticatorKeyStore': {
        'en-US': "Store does not implement IUserAuthenticatorKeyStore<User>.",
        'ru-RU': "Store не реализует IUserAuthenticatorKeyStore[TUser]."
    },
    'StoreNotIUserTwoFactorStore': {
        'en-US': "Store does not implement IUserTwoFactorStore[TUser].",
        'ru-RU': "Store не реализует IUserTwoFactorStore[TUser]."
    },
    'RecoveryCodeRedemptionFailed': {
        'en-US': "Recovery code redemption failed.",
        'ru-RU': "Не удалось восстановить код восстановления."
    },
    'UserAlreadyHasPassword': {
        'en-US': "User already has a password set.",
        'ru-RU': "У пользователя уже установлен пароль."
    },
    'UserAlreadyInRole': {
        'en-US': "User already in role '{0}'.",
        'ru-RU': "Пользователь уже в роли '{0}'."
    },
    'UserLockedOut': {
        'en-US': "User is locked out.",
        'ru-RU': "Пользователь заблокирован."
    },
    'UserLockoutNotEnabled': {
        'en-US': "Lockout is not enabled for this user.",
        'ru-RU': "Блокировка не включена для этого пользователя."
    },
    'UserNameNotFound': {
        'en-US': "User {0} does not exist.",
        'ru-RU': "Пользователь {0} не существует."
    },
    'UserNotInRole': {
        'en-US': "User is not in role '{0}'.",
        'ru-RU': "Пользователь не имеет роли '{0}'."
    },
    'StoreNotIUserTwoFactorRecoveryCodeStore': {
        'en-US': "Store does not implement IUserTwoFactorRecoveryCodeStore[TUser].",
        'ru-RU': "Store не реализует IUserTwoFactorRecoveryCodeStore[TUser]."
    },
    'PasswordRequiresUniqueChars': {
        'en-US': "Passwords must use at least {0} different characters.",
        'ru-RU': "В паролях должно использоваться как минимум {0} разных символов."
    },
}


class _Resources:
    def __getitem__(self, item):
        return _RESOURCES[item][LOCALISATION]

    def __getattr__(self, item):
        return _RESOURCES[item][LOCALISATION]

    @staticmethod
    def FormatNoTokenProvider(token_provider: str):
        return _RESOURCES['NoTokenProvider'][LOCALISATION].format(token_provider)


Resources = _Resources()
