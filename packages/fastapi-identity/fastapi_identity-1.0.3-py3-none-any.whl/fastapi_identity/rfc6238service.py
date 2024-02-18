import base64
from typing import cast

import pyotp


class Rfc6238AuthenticationService:
    @staticmethod
    def _apply_modifier(input_: bytes, modifier_bytes: bytes = None) -> str:
        return cast(str, base64.b32encode(input_ + modifier_bytes if modifier_bytes else input_))

    @staticmethod
    def generate_code(security_token: bytes, modifier: bytes = None, interval: int = 180):
        b32secret = Rfc6238AuthenticationService._apply_modifier(security_token, modifier)
        totp = pyotp.TOTP(b32secret, interval=interval)
        return totp.now()

    @staticmethod
    def validate_code(security_token: bytes, code: str, modifier: bytes = None, interval: int = 180):
        b32secret = Rfc6238AuthenticationService._apply_modifier(security_token, modifier)
        totp = pyotp.TOTP(b32secret, interval=interval)
        return totp.verify(code)
