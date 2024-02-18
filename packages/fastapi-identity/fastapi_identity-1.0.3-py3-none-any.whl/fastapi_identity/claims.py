from typing import Optional, Generator, Any, Union, overload

from fastapi_identity.types import Predicate


class IdentityConstants:
    IdentityPrefix: str = "FastAPIIdentity"
    ApplicationScheme: str = IdentityPrefix + ".Application"
    BearerScheme: str = IdentityPrefix + ".Bearer"
    ExternalScheme: str = IdentityPrefix + ".External"
    TwoFactorRememberMeScheme: str = IdentityPrefix + ".TwoFactorRememberMe"
    TwoFactorUserIdScheme: str = IdentityPrefix + ".TwoFactorUserId"


class ClaimTypes:
    AuthenticationInstant = "authenticationinstant"
    AuthenticationMethod = "authenticationmethod"
    CookiePath = "cookiepath"
    DenyOnlyPrimarySid = "denyonlyprimarysid"
    DenyOnlyPrimaryGroupSid = "denyonlyprimarygroupsid"
    DenyOnlyWindowsDeviceGroup = "denyonlywindowsdevicegroup"
    Dsa = "dsa"
    Expiration = "expiration"
    Expired = "expired"
    GroupSid = "groupsid"
    IsPersistent = "ispersistent"
    PrimaryGroupSid = "primarygroupsid"
    PrimarySid = "primarysid"
    Role = "role"
    SecurityStamp = "securitystamp"
    SerialNumber = "serialnumber"
    UserData = "userdata"
    Version = "version"
    WindowsAccountName = "windowsaccountname"
    WindowsDeviceClaim = "windowsdeviceclaim"
    WindowsDeviceGroup = "windowsdevicegroup"
    WindowsUserClaim = "windowsuserclaim"
    WindowsFqbnVersion = "windowsfqbnversion"
    WindowsSubAuthority = "windowssubauthority"
    Anonymous = "anonymous"
    Authentication = "authentication"
    AuthorizationDecision = "authorizationdecision"
    Country = "country"
    DateOfBirth = "dateofbirth"
    Dns = "dns"
    DenyOnlySid = "denyonlysid"
    Email = "emailaddress"
    Gender = "gender"
    GivenName = "givenname"
    Hash = "hash"
    HomePhone = "homephone"
    Locality = "locality"
    MobilePhone = "mobilephone"
    Name = "name"
    NameIdentifier = "nameidentifier"
    OtherPhone = "otherphone"
    PostalCode = "postalcode"
    Rsa = "rsa"
    Sid = "sid"
    Spn = "spn"
    StateOrProvince = "stateorprovince"
    StreetAddress = "streetaddress"
    Surname = "surname"
    System = "system"
    Thumbprint = "thumbprint"
    Upn = "upn"
    Uri = "uri"
    Webpage = "webpage"
    X500DistinguishedName = "x500distinguishedname"
    Actor = "actor"


class Claim:
    def __init__(
            self,
            _type: str,
            _value: Any,
            issuer: Optional[str] = None,
            original_issuer: Optional[str] = None
    ) -> None:
        self._type = _type
        self._value = _value
        self._issuer = issuer
        self._original_issuer = original_issuer

    @property
    def type(self) -> str:
        return self._type

    @property
    def value(self) -> Any:
        return self._value

    @property
    def issuer(self) -> str:
        return self._issuer

    @property
    def original_issuer(self) -> str:
        return self._original_issuer

    def dump(self):
        _temp = {
            'type': self.type,
            'value': self.value,
        }

        if self.issuer is not None:
            _temp['issuer'] = self.issuer

        if self.original_issuer is not None:
            _temp['original_issuer'] = self.original_issuer

        return _temp

    @staticmethod
    def load(data: dict) -> 'Claim':
        return Claim(
            _type=data.get('type'),
            _value=data.get('value'),
            issuer=data.get('issuer'),
            original_issuer=data.get('original_issuer')
        )


class ClaimsPrincipal:
    def __init__(self, *claims: Claim) -> None:
        self._claims = list(claims) if claims else []

    @property
    def claims(self) -> Generator[Claim, Any, None]:
        for claim in set(self._claims):
            yield claim

    @property
    def name(self) -> Optional[str]:
        return self.find_first_value(ClaimTypes.Name)

    def add_claims(self, *claims: Claim):
        self._claims.extend(claims)

    @overload
    def find_all(self, match: str) -> Generator[Claim, Any, None]:
        ...

    @overload
    def find_all(self, match: Predicate[Claim]) -> Generator[Claim, Any, None]:
        ...

    def find_all(self, match: Union[str, Predicate[Claim]]) -> Generator[Claim, Any, None]:
        _match: Predicate[Claim] = match

        if isinstance(match, str):
            def _match(x): return x.type == match

        for claim in self.claims:
            if _match(claim):
                yield claim

    @overload
    def find_first(self, match: str) -> Optional[Claim]:
        ...

    @overload
    def find_first(self, match: Predicate[Claim]) -> Optional[Claim]:
        ...

    def find_first(self, match: Union[str, Predicate[Claim]]) -> Optional[Claim]:
        _match: Predicate[Claim] = match

        if isinstance(match, str):
            def _match(x): return x.type == match

        for claim in self.claims:
            if _match(claim):
                return claim

    @overload
    def find_first_value(self, match: str) -> Optional[Any]:
        ...

    @overload
    def find_first_value(self, match: Predicate[Claim]) -> Optional[Any]:
        ...

    def find_first_value(self, match: Union[str, Predicate[Claim]]) -> Optional[Any]:
        if _claim := self.find_first(match):
            return _claim.value
        return None

    @overload
    def has_claim(self, match: tuple[str, str]) -> bool:
        ...

    @overload
    def has_claim(self, match: Predicate[Claim]) -> bool:
        ...

    def has_claim(self, match: Union[tuple[str, str], Predicate[Claim]]) -> bool:
        _match: Predicate[Claim] = match

        if isinstance(match, tuple):
            type_, value_ = match

            def _match(x: Claim):
                return x.type.casefold() == type_.casefold() and x.value == value_

        for claim in self.claims:
            if _match(claim):
                return True

        return False

    def is_in_role(self, role: str):
        if self.has_claim((ClaimTypes.Role, role)):
            return True
        return False

    def dump(self):
        _roles = []
        _claims = []
        for item in [claim.dump() for claim in self.claims]:
            if item['type'] == ClaimTypes.Role:
                _roles.append(item)
            else:
                _claims.append(item)
        return _roles, _claims
