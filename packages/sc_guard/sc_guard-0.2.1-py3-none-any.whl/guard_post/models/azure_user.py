from datetime import datetime
from typing import TYPE_CHECKING, Any, Dict, List, Type, TypeVar, Union, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field
from pydantic import BaseModel, EmailStr, Field

from ..models.azure_user_acr_type_0 import AzureUserAcrType0
from ..models.azure_user_appidacr_type_0 import AzureUserAppidacrType0
from ..models.azure_user_azpacr_type_0 import AzureUserAzpacrType0
from ..models.azure_user_ver import AzureUserVer
from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.azure_user_claims import AzureUserClaims


T = TypeVar("T", bound="AzureUser")


class User(BaseModel):
    email: EmailStr = Field(..., example="example.name@hussmann.com")
    expiration: datetime = Field(..., example="2024-01-26T01:10:57Z")
    first: str = Field(..., example="Example")
    issued: datetime = Field(..., example="2024-01-26T00:05:57Z")
    last: str = Field(..., example="Name")


@_attrs_define
class AzureUser:
    """
    Attributes:
        aud (str): Identifies the intended audience of the token. In v2.0 tokens, this value is always the client ID of
            the API. In v1.0 tokens, it can be the client ID or the resource URI used in the request.
        iss (str): Identifies the STS that constructs and returns the token, and the Azure AD tenant of the
            authenticated user. If the token issued is a v2.0 token (see the ver claim), the URI ends in /v2.0.
        iat (int): Specifies when the authentication for this token occurred.
        nbf (int): Specifies the time after which the JWT can be processed.
        exp (int): Specifies the expiration time before which the JWT can be accepted for processing.
        sub (str): The principal associated with the token.
        ver (AzureUserVer): Indicates the version of the access token.
        claims (AzureUserClaims): The entire decoded token
        access_token (str): The access_token. Can be used for fetching the Graph API
        idp (Union[Any, Unset, str]): Records the identity provider that authenticated the subject of the token. This
            value is identical to the value of the Issuer claim unless the user account is not in the same tenant as the
            issuer, such as guests. Use the value of iss if the claim is not present.
        aio (Union[Any, Unset, str]): An internal claim used by Azure AD to record data for token reuse. Resources
            should not use this claim.
        name (Union[Any, Unset, str]): Provides a human-readable value that identifies the subject of the token.
        scp (Union[Unset, List[str]]): The set of scopes exposed by the application for which the client application has
            requested (and received) consent. Only included for user tokens.
        roles (Union[Unset, List[str]]): The set of permissions exposed by the application that the requesting
            application or user has been given permission to call.
        wids (Union[Unset, List[str]]): Denotes the tenant-wide roles assigned to this user, from the section of roles
            present in Azure AD built-in roles.
        groups (Union[Unset, List[str]]): Provides object IDs that represent the group memberships of the subject.
        oid (Union[Any, Unset, str]): The immutable identifier for the requestor, which is the verified identity of the
            user or service principal
        tid (Union[Any, Unset, str]): Represents the tenant that the user is signing in to
        uti (Union[Any, Unset, str]): Token identifier claim, equivalent to jti in the JWT specification. Unique, per-
            token identifier that is case-sensitive.
        rh (Union[Any, Unset, str]): Token identifier claim, equivalent to jti in the JWT specification. Unique, per-
            token identifier that is case-sensitive.
        acct (Union[Any, Unset, str]): User's account status in tenant
        auth_time (Union[Any, Unset, int]): Time when the user last authenticated; See OpenID Connect spec
        ctry (Union[Any, Unset, str]): User's country/region
        email (Union[Any, Unset, str]): The addressable email for this user, if the user has one
        family_name (Union[Any, Unset, str]): Provides the last name, surname, or family name of the user as defined in
            the user object
        fwd (Union[Any, Unset, str]): IP address
        given_name (Union[Any, Unset, str]): Provides the first or "given" name of the user, as set on the user object
        idtyp (Union[Any, Unset, str]): Signals whether the token is an app-only token
        in_corp (Union[Any, Unset, str]): Signals if the client is logging in from the corporate network; if they are
            not, the claim is not included
        ipaddr (Union[Any, Unset, str]): The IP address the user authenticated from.
        login_hint (Union[Any, Unset, str]): Login hint
        onprem_sid (Union[Any, Unset, str]): On-premises security identifier
        pwd_exp (Union[Any, Unset, str]): The datetime at which the password expires
        pwd_url (Union[Any, Unset, str]): A URL that the user can visit to change their password
        sid (Union[Any, Unset, str]): Session ID, used for per-session user sign out
        tenant_ctry (Union[Any, Unset, str]): Resource tenant's country/region
        tenant_region_scope (Union[Any, Unset, str]): Region of the resource tenant
        upn (Union[Any, Unset, str]): An identifier for the user that can be used with the username_hint parameter; not
            a durable identifier for the user and should not be used to key data
        verified_primary_email (Union[Unset, List[str]]): Sourced from the user's PrimaryAuthoritativeEmail
        verified_secondary_email (Union[Unset, List[str]]): Sourced from the user's SecondaryAuthoritativeEmail
        vnet (Union[Any, Unset, str]): VNET specifier information
        xms_pdl (Union[Any, Unset, str]): Preferred data location
        xms_pl (Union[Any, Unset, str]): User-preferred language
        xms_tpl (Union[Any, Unset, str]): Tenant-preferred language
        ztdid (Union[Any, Unset, str]): Zero-touch Deployment ID
        acr (Union[Any, AzureUserAcrType0, Unset]): A value of 0 for the "Authentication context class" claim indicates
            the end-user authentication did not meet the requirements of ISO/IEC 29115. Only available in V1.0 tokens
        amr (Union[Unset, List[str]]): Identifies the authentication method of the subject of the token. Only available
            in V1.0 tokens
        appid (Union[Any, Unset, str]): The application ID of the client using the token. Only available in V1.0 tokens
        appidacr (Union[Any, AzureUserAppidacrType0, Unset]): Indicates authentication method of the client. Only
            available in V1.0 tokens
        unique_name (Union[Any, Unset, str]): Provides a human readable value that identifies the subject of the token.
            Only available in V1.0 tokens
        azp (Union[Any, Unset, str]): The application ID of the client using the token. Only available in V2.0 tokens
        azpacr (Union[Any, AzureUserAzpacrType0, Unset]): Indicates the authentication method of the client. Only
            available in V2.0 tokens
        preferred_username (Union[Any, Unset, str]): The primary username that represents the user. Only available in
            V2.0 tokens
        is_guest (Union[Unset, bool]): The user is a guest user in the tenant
    """

    aud: str
    iss: str
    iat: int
    nbf: int
    exp: int
    sub: str
    ver: AzureUserVer
    claims: "AzureUserClaims"
    access_token: str
    idp: Union[Any, Unset, str] = UNSET
    aio: Union[Any, Unset, str] = UNSET
    name: Union[Any, Unset, str] = UNSET
    scp: Union[Unset, List[str]] = UNSET
    roles: Union[Unset, List[str]] = UNSET
    wids: Union[Unset, List[str]] = UNSET
    groups: Union[Unset, List[str]] = UNSET
    oid: Union[Any, Unset, str] = UNSET
    tid: Union[Any, Unset, str] = UNSET
    uti: Union[Any, Unset, str] = UNSET
    rh: Union[Any, Unset, str] = UNSET
    acct: Union[Any, Unset, str] = UNSET
    auth_time: Union[Any, Unset, int] = UNSET
    ctry: Union[Any, Unset, str] = UNSET
    email: Union[Any, Unset, str] = UNSET
    family_name: Union[Any, Unset, str] = UNSET
    fwd: Union[Any, Unset, str] = UNSET
    given_name: Union[Any, Unset, str] = UNSET
    idtyp: Union[Any, Unset, str] = UNSET
    in_corp: Union[Any, Unset, str] = UNSET
    ipaddr: Union[Any, Unset, str] = UNSET
    login_hint: Union[Any, Unset, str] = UNSET
    onprem_sid: Union[Any, Unset, str] = UNSET
    pwd_exp: Union[Any, Unset, str] = UNSET
    pwd_url: Union[Any, Unset, str] = UNSET
    sid: Union[Any, Unset, str] = UNSET
    tenant_ctry: Union[Any, Unset, str] = UNSET
    tenant_region_scope: Union[Any, Unset, str] = UNSET
    upn: Union[Any, Unset, str] = UNSET
    verified_primary_email: Union[Unset, List[str]] = UNSET
    verified_secondary_email: Union[Unset, List[str]] = UNSET
    vnet: Union[Any, Unset, str] = UNSET
    xms_pdl: Union[Any, Unset, str] = UNSET
    xms_pl: Union[Any, Unset, str] = UNSET
    xms_tpl: Union[Any, Unset, str] = UNSET
    ztdid: Union[Any, Unset, str] = UNSET
    acr: Union[Any, AzureUserAcrType0, Unset] = UNSET
    amr: Union[Unset, List[str]] = UNSET
    appid: Union[Any, Unset, str] = UNSET
    appidacr: Union[Any, AzureUserAppidacrType0, Unset] = UNSET
    unique_name: Union[Any, Unset, str] = UNSET
    azp: Union[Any, Unset, str] = UNSET
    azpacr: Union[Any, AzureUserAzpacrType0, Unset] = UNSET
    preferred_username: Union[Any, Unset, str] = UNSET
    is_guest: Union[Unset, bool] = False
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        aud = self.aud
        iss = self.iss
        iat = self.iat
        nbf = self.nbf
        exp = self.exp
        sub = self.sub
        ver = self.ver.value

        claims = self.claims.to_dict()

        access_token = self.access_token
        idp: Union[Any, Unset, str]
        if isinstance(self.idp, Unset):
            idp = UNSET

        else:
            idp = self.idp

        aio: Union[Any, Unset, str]
        if isinstance(self.aio, Unset):
            aio = UNSET

        else:
            aio = self.aio

        name: Union[Any, Unset, str]
        if isinstance(self.name, Unset):
            name = UNSET

        else:
            name = self.name

        scp: Union[Unset, List[str]] = UNSET
        if not isinstance(self.scp, Unset):
            scp = self.scp

        roles: Union[Unset, List[str]] = UNSET
        if not isinstance(self.roles, Unset):
            roles = self.roles

        wids: Union[Unset, List[str]] = UNSET
        if not isinstance(self.wids, Unset):
            wids = self.wids

        groups: Union[Unset, List[str]] = UNSET
        if not isinstance(self.groups, Unset):
            groups = self.groups

        oid: Union[Any, Unset, str]
        if isinstance(self.oid, Unset):
            oid = UNSET

        else:
            oid = self.oid

        tid: Union[Any, Unset, str]
        if isinstance(self.tid, Unset):
            tid = UNSET

        else:
            tid = self.tid

        uti: Union[Any, Unset, str]
        if isinstance(self.uti, Unset):
            uti = UNSET

        else:
            uti = self.uti

        rh: Union[Any, Unset, str]
        if isinstance(self.rh, Unset):
            rh = UNSET

        else:
            rh = self.rh

        acct: Union[Any, Unset, str]
        if isinstance(self.acct, Unset):
            acct = UNSET

        else:
            acct = self.acct

        auth_time: Union[Any, Unset, int]
        if isinstance(self.auth_time, Unset):
            auth_time = UNSET

        else:
            auth_time = self.auth_time

        ctry: Union[Any, Unset, str]
        if isinstance(self.ctry, Unset):
            ctry = UNSET

        else:
            ctry = self.ctry

        email: Union[Any, Unset, str]
        if isinstance(self.email, Unset):
            email = UNSET

        else:
            email = self.email

        family_name: Union[Any, Unset, str]
        if isinstance(self.family_name, Unset):
            family_name = UNSET

        else:
            family_name = self.family_name

        fwd: Union[Any, Unset, str]
        if isinstance(self.fwd, Unset):
            fwd = UNSET

        else:
            fwd = self.fwd

        given_name: Union[Any, Unset, str]
        if isinstance(self.given_name, Unset):
            given_name = UNSET

        else:
            given_name = self.given_name

        idtyp: Union[Any, Unset, str]
        if isinstance(self.idtyp, Unset):
            idtyp = UNSET

        else:
            idtyp = self.idtyp

        in_corp: Union[Any, Unset, str]
        if isinstance(self.in_corp, Unset):
            in_corp = UNSET

        else:
            in_corp = self.in_corp

        ipaddr: Union[Any, Unset, str]
        if isinstance(self.ipaddr, Unset):
            ipaddr = UNSET

        else:
            ipaddr = self.ipaddr

        login_hint: Union[Any, Unset, str]
        if isinstance(self.login_hint, Unset):
            login_hint = UNSET

        else:
            login_hint = self.login_hint

        onprem_sid: Union[Any, Unset, str]
        if isinstance(self.onprem_sid, Unset):
            onprem_sid = UNSET

        else:
            onprem_sid = self.onprem_sid

        pwd_exp: Union[Any, Unset, str]
        if isinstance(self.pwd_exp, Unset):
            pwd_exp = UNSET

        else:
            pwd_exp = self.pwd_exp

        pwd_url: Union[Any, Unset, str]
        if isinstance(self.pwd_url, Unset):
            pwd_url = UNSET

        else:
            pwd_url = self.pwd_url

        sid: Union[Any, Unset, str]
        if isinstance(self.sid, Unset):
            sid = UNSET

        else:
            sid = self.sid

        tenant_ctry: Union[Any, Unset, str]
        if isinstance(self.tenant_ctry, Unset):
            tenant_ctry = UNSET

        else:
            tenant_ctry = self.tenant_ctry

        tenant_region_scope: Union[Any, Unset, str]
        if isinstance(self.tenant_region_scope, Unset):
            tenant_region_scope = UNSET

        else:
            tenant_region_scope = self.tenant_region_scope

        upn: Union[Any, Unset, str]
        if isinstance(self.upn, Unset):
            upn = UNSET

        else:
            upn = self.upn

        verified_primary_email: Union[Unset, List[str]] = UNSET
        if not isinstance(self.verified_primary_email, Unset):
            verified_primary_email = self.verified_primary_email

        verified_secondary_email: Union[Unset, List[str]] = UNSET
        if not isinstance(self.verified_secondary_email, Unset):
            verified_secondary_email = self.verified_secondary_email

        vnet: Union[Any, Unset, str]
        if isinstance(self.vnet, Unset):
            vnet = UNSET

        else:
            vnet = self.vnet

        xms_pdl: Union[Any, Unset, str]
        if isinstance(self.xms_pdl, Unset):
            xms_pdl = UNSET

        else:
            xms_pdl = self.xms_pdl

        xms_pl: Union[Any, Unset, str]
        if isinstance(self.xms_pl, Unset):
            xms_pl = UNSET

        else:
            xms_pl = self.xms_pl

        xms_tpl: Union[Any, Unset, str]
        if isinstance(self.xms_tpl, Unset):
            xms_tpl = UNSET

        else:
            xms_tpl = self.xms_tpl

        ztdid: Union[Any, Unset, str]
        if isinstance(self.ztdid, Unset):
            ztdid = UNSET

        else:
            ztdid = self.ztdid

        acr: Union[Any, Unset, str]
        if isinstance(self.acr, Unset):
            acr = UNSET

        elif isinstance(self.acr, AzureUserAcrType0):
            acr = UNSET
            if not isinstance(self.acr, Unset):
                acr = self.acr.value

        else:
            acr = self.acr

        amr: Union[Unset, List[str]] = UNSET
        if not isinstance(self.amr, Unset):
            amr = self.amr

        appid: Union[Any, Unset, str]
        if isinstance(self.appid, Unset):
            appid = UNSET

        else:
            appid = self.appid

        appidacr: Union[Any, Unset, str]
        if isinstance(self.appidacr, Unset):
            appidacr = UNSET

        elif isinstance(self.appidacr, AzureUserAppidacrType0):
            appidacr = UNSET
            if not isinstance(self.appidacr, Unset):
                appidacr = self.appidacr.value

        else:
            appidacr = self.appidacr

        unique_name: Union[Any, Unset, str]
        if isinstance(self.unique_name, Unset):
            unique_name = UNSET

        else:
            unique_name = self.unique_name

        azp: Union[Any, Unset, str]
        if isinstance(self.azp, Unset):
            azp = UNSET

        else:
            azp = self.azp

        azpacr: Union[Any, Unset, str]
        if isinstance(self.azpacr, Unset):
            azpacr = UNSET

        elif isinstance(self.azpacr, AzureUserAzpacrType0):
            azpacr = UNSET
            if not isinstance(self.azpacr, Unset):
                azpacr = self.azpacr.value

        else:
            azpacr = self.azpacr

        preferred_username: Union[Any, Unset, str]
        if isinstance(self.preferred_username, Unset):
            preferred_username = UNSET

        else:
            preferred_username = self.preferred_username

        is_guest = self.is_guest

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "aud": aud,
                "iss": iss,
                "iat": iat,
                "nbf": nbf,
                "exp": exp,
                "sub": sub,
                "ver": ver,
                "claims": claims,
                "access_token": access_token,
            }
        )
        if idp is not UNSET:
            field_dict["idp"] = idp
        if aio is not UNSET:
            field_dict["aio"] = aio
        if name is not UNSET:
            field_dict["name"] = name
        if scp is not UNSET:
            field_dict["scp"] = scp
        if roles is not UNSET:
            field_dict["roles"] = roles
        if wids is not UNSET:
            field_dict["wids"] = wids
        if groups is not UNSET:
            field_dict["groups"] = groups
        if oid is not UNSET:
            field_dict["oid"] = oid
        if tid is not UNSET:
            field_dict["tid"] = tid
        if uti is not UNSET:
            field_dict["uti"] = uti
        if rh is not UNSET:
            field_dict["rh"] = rh
        if acct is not UNSET:
            field_dict["acct"] = acct
        if auth_time is not UNSET:
            field_dict["auth_time"] = auth_time
        if ctry is not UNSET:
            field_dict["ctry"] = ctry
        if email is not UNSET:
            field_dict["email"] = email
        if family_name is not UNSET:
            field_dict["family_name"] = family_name
        if fwd is not UNSET:
            field_dict["fwd"] = fwd
        if given_name is not UNSET:
            field_dict["given_name"] = given_name
        if idtyp is not UNSET:
            field_dict["idtyp"] = idtyp
        if in_corp is not UNSET:
            field_dict["in_corp"] = in_corp
        if ipaddr is not UNSET:
            field_dict["ipaddr"] = ipaddr
        if login_hint is not UNSET:
            field_dict["login_hint"] = login_hint
        if onprem_sid is not UNSET:
            field_dict["onprem_sid"] = onprem_sid
        if pwd_exp is not UNSET:
            field_dict["pwd_exp"] = pwd_exp
        if pwd_url is not UNSET:
            field_dict["pwd_url"] = pwd_url
        if sid is not UNSET:
            field_dict["sid"] = sid
        if tenant_ctry is not UNSET:
            field_dict["tenant_ctry"] = tenant_ctry
        if tenant_region_scope is not UNSET:
            field_dict["tenant_region_scope"] = tenant_region_scope
        if upn is not UNSET:
            field_dict["upn"] = upn
        if verified_primary_email is not UNSET:
            field_dict["verified_primary_email"] = verified_primary_email
        if verified_secondary_email is not UNSET:
            field_dict["verified_secondary_email"] = verified_secondary_email
        if vnet is not UNSET:
            field_dict["vnet"] = vnet
        if xms_pdl is not UNSET:
            field_dict["xms_pdl"] = xms_pdl
        if xms_pl is not UNSET:
            field_dict["xms_pl"] = xms_pl
        if xms_tpl is not UNSET:
            field_dict["xms_tpl"] = xms_tpl
        if ztdid is not UNSET:
            field_dict["ztdid"] = ztdid
        if acr is not UNSET:
            field_dict["acr"] = acr
        if amr is not UNSET:
            field_dict["amr"] = amr
        if appid is not UNSET:
            field_dict["appid"] = appid
        if appidacr is not UNSET:
            field_dict["appidacr"] = appidacr
        if unique_name is not UNSET:
            field_dict["unique_name"] = unique_name
        if azp is not UNSET:
            field_dict["azp"] = azp
        if azpacr is not UNSET:
            field_dict["azpacr"] = azpacr
        if preferred_username is not UNSET:
            field_dict["preferred_username"] = preferred_username
        if is_guest is not UNSET:
            field_dict["is_guest"] = is_guest

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        from ..models.azure_user_claims import AzureUserClaims

        d = src_dict.copy()
        aud = d.pop("aud", None)

        iss = d.pop("iss", None)

        iat = d.pop("iat", None)

        nbf = d.pop("nbf", None)

        exp = d.pop("exp", None)

        sub = d.pop("sub", None)

        ver = AzureUserVer(d.pop("ver"))

        claims = AzureUserClaims.from_dict(d.pop("claims"))

        access_token = d.pop("access_token")

        def _parse_idp(data: object) -> Union[Any, Unset, str]:
            if isinstance(data, Unset):
                return data
            return cast(Union[Any, Unset, str], data)

        idp = _parse_idp(d.pop("idp", UNSET))

        def _parse_aio(data: object) -> Union[Any, Unset, str]:
            if isinstance(data, Unset):
                return data
            return cast(Union[Any, Unset, str], data)

        aio = _parse_aio(d.pop("aio", UNSET))

        def _parse_name(data: object) -> Union[Any, Unset, str]:
            if isinstance(data, Unset):
                return data
            return cast(Union[Any, Unset, str], data)

        name = _parse_name(d.pop("name", UNSET))

        scp = cast(List[str], d.pop("scp", UNSET))

        roles = cast(List[str], d.pop("roles", UNSET))

        wids = cast(List[str], d.pop("wids", UNSET))

        groups = cast(List[str], d.pop("groups", UNSET))

        def _parse_oid(data: object) -> Union[Any, Unset, str]:
            if isinstance(data, Unset):
                return data
            return cast(Union[Any, Unset, str], data)

        oid = _parse_oid(d.pop("oid", UNSET))

        def _parse_tid(data: object) -> Union[Any, Unset, str]:
            if isinstance(data, Unset):
                return data
            return cast(Union[Any, Unset, str], data)

        tid = _parse_tid(d.pop("tid", UNSET))

        def _parse_uti(data: object) -> Union[Any, Unset, str]:
            if isinstance(data, Unset):
                return data
            return cast(Union[Any, Unset, str], data)

        uti = _parse_uti(d.pop("uti", UNSET))

        def _parse_rh(data: object) -> Union[Any, Unset, str]:
            if isinstance(data, Unset):
                return data
            return cast(Union[Any, Unset, str], data)

        rh = _parse_rh(d.pop("rh", UNSET))

        def _parse_acct(data: object) -> Union[Any, Unset, str]:
            if isinstance(data, Unset):
                return data
            return cast(Union[Any, Unset, str], data)

        acct = _parse_acct(d.pop("acct", UNSET))

        def _parse_auth_time(data: object) -> Union[Any, Unset, int]:
            if isinstance(data, Unset):
                return data
            return cast(Union[Any, Unset, int], data)

        auth_time = _parse_auth_time(d.pop("auth_time", UNSET))

        def _parse_ctry(data: object) -> Union[Any, Unset, str]:
            if isinstance(data, Unset):
                return data
            return cast(Union[Any, Unset, str], data)

        ctry = _parse_ctry(d.pop("ctry", UNSET))

        def _parse_email(data: object) -> Union[Any, Unset, str]:
            if isinstance(data, Unset):
                return data
            return cast(Union[Any, Unset, str], data)

        email = _parse_email(d.pop("email", UNSET))

        def _parse_family_name(data: object) -> Union[Any, Unset, str]:
            if isinstance(data, Unset):
                return data
            return cast(Union[Any, Unset, str], data)

        family_name = _parse_family_name(d.pop("family_name", UNSET))

        def _parse_fwd(data: object) -> Union[Any, Unset, str]:
            if isinstance(data, Unset):
                return data
            return cast(Union[Any, Unset, str], data)

        fwd = _parse_fwd(d.pop("fwd", UNSET))

        def _parse_given_name(data: object) -> Union[Any, Unset, str]:
            if isinstance(data, Unset):
                return data
            return cast(Union[Any, Unset, str], data)

        given_name = _parse_given_name(d.pop("given_name", UNSET))

        def _parse_idtyp(data: object) -> Union[Any, Unset, str]:
            if isinstance(data, Unset):
                return data
            return cast(Union[Any, Unset, str], data)

        idtyp = _parse_idtyp(d.pop("idtyp", UNSET))

        def _parse_in_corp(data: object) -> Union[Any, Unset, str]:
            if isinstance(data, Unset):
                return data
            return cast(Union[Any, Unset, str], data)

        in_corp = _parse_in_corp(d.pop("in_corp", UNSET))

        def _parse_ipaddr(data: object) -> Union[Any, Unset, str]:
            if isinstance(data, Unset):
                return data
            return cast(Union[Any, Unset, str], data)

        ipaddr = _parse_ipaddr(d.pop("ipaddr", UNSET))

        def _parse_login_hint(data: object) -> Union[Any, Unset, str]:
            if isinstance(data, Unset):
                return data
            return cast(Union[Any, Unset, str], data)

        login_hint = _parse_login_hint(d.pop("login_hint", UNSET))

        def _parse_onprem_sid(data: object) -> Union[Any, Unset, str]:
            if isinstance(data, Unset):
                return data
            return cast(Union[Any, Unset, str], data)

        onprem_sid = _parse_onprem_sid(d.pop("onprem_sid", UNSET))

        def _parse_pwd_exp(data: object) -> Union[Any, Unset, str]:
            if isinstance(data, Unset):
                return data
            return cast(Union[Any, Unset, str], data)

        pwd_exp = _parse_pwd_exp(d.pop("pwd_exp", UNSET))

        def _parse_pwd_url(data: object) -> Union[Any, Unset, str]:
            if isinstance(data, Unset):
                return data
            return cast(Union[Any, Unset, str], data)

        pwd_url = _parse_pwd_url(d.pop("pwd_url", UNSET))

        def _parse_sid(data: object) -> Union[Any, Unset, str]:
            if isinstance(data, Unset):
                return data
            return cast(Union[Any, Unset, str], data)

        sid = _parse_sid(d.pop("sid", UNSET))

        def _parse_tenant_ctry(data: object) -> Union[Any, Unset, str]:
            if isinstance(data, Unset):
                return data
            return cast(Union[Any, Unset, str], data)

        tenant_ctry = _parse_tenant_ctry(d.pop("tenant_ctry", UNSET))

        def _parse_tenant_region_scope(data: object) -> Union[Any, Unset, str]:
            if isinstance(data, Unset):
                return data
            return cast(Union[Any, Unset, str], data)

        tenant_region_scope = _parse_tenant_region_scope(
            d.pop("tenant_region_scope", UNSET)
        )

        def _parse_upn(data: object) -> Union[Any, Unset, str]:
            if isinstance(data, Unset):
                return data
            return cast(Union[Any, Unset, str], data)

        upn = _parse_upn(d.pop("upn", UNSET))

        verified_primary_email = cast(List[str], d.pop("verified_primary_email", UNSET))

        verified_secondary_email = cast(
            List[str], d.pop("verified_secondary_email", UNSET)
        )

        def _parse_vnet(data: object) -> Union[Any, Unset, str]:
            if isinstance(data, Unset):
                return data
            return cast(Union[Any, Unset, str], data)

        vnet = _parse_vnet(d.pop("vnet", UNSET))

        def _parse_xms_pdl(data: object) -> Union[Any, Unset, str]:
            if isinstance(data, Unset):
                return data
            return cast(Union[Any, Unset, str], data)

        xms_pdl = _parse_xms_pdl(d.pop("xms_pdl", UNSET))

        def _parse_xms_pl(data: object) -> Union[Any, Unset, str]:
            if isinstance(data, Unset):
                return data
            return cast(Union[Any, Unset, str], data)

        xms_pl = _parse_xms_pl(d.pop("xms_pl", UNSET))

        def _parse_xms_tpl(data: object) -> Union[Any, Unset, str]:
            if isinstance(data, Unset):
                return data
            return cast(Union[Any, Unset, str], data)

        xms_tpl = _parse_xms_tpl(d.pop("xms_tpl", UNSET))

        def _parse_ztdid(data: object) -> Union[Any, Unset, str]:
            if isinstance(data, Unset):
                return data
            return cast(Union[Any, Unset, str], data)

        ztdid = _parse_ztdid(d.pop("ztdid", UNSET))

        def _parse_acr(data: object) -> Union[Any, AzureUserAcrType0, Unset]:
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, str):
                    raise TypeError()
                _acr_type_0 = data
                acr_type_0: Union[Unset, AzureUserAcrType0]
                if isinstance(_acr_type_0, Unset):
                    acr_type_0 = UNSET
                else:
                    acr_type_0 = AzureUserAcrType0(_acr_type_0)

                return acr_type_0
            except:  # noqa: E722
                pass
            return cast(Union[Any, AzureUserAcrType0, Unset], data)

        acr = _parse_acr(d.pop("acr", UNSET))

        amr = cast(List[str], d.pop("amr", UNSET))

        def _parse_appid(data: object) -> Union[Any, Unset, str]:
            if isinstance(data, Unset):
                return data
            return cast(Union[Any, Unset, str], data)

        appid = _parse_appid(d.pop("appid", UNSET))

        def _parse_appidacr(data: object) -> Union[Any, AzureUserAppidacrType0, Unset]:
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, str):
                    raise TypeError()
                _appidacr_type_0 = data
                appidacr_type_0: Union[Unset, AzureUserAppidacrType0]
                if isinstance(_appidacr_type_0, Unset):
                    appidacr_type_0 = UNSET
                else:
                    appidacr_type_0 = AzureUserAppidacrType0(_appidacr_type_0)

                return appidacr_type_0
            except:  # noqa: E722
                pass
            return cast(Union[Any, AzureUserAppidacrType0, Unset], data)

        appidacr = _parse_appidacr(d.pop("appidacr", UNSET))

        def _parse_unique_name(data: object) -> Union[Any, Unset, str]:
            if isinstance(data, Unset):
                return data
            return cast(Union[Any, Unset, str], data)

        unique_name = _parse_unique_name(d.pop("unique_name", UNSET))

        def _parse_azp(data: object) -> Union[Any, Unset, str]:
            if isinstance(data, Unset):
                return data
            return cast(Union[Any, Unset, str], data)

        azp = _parse_azp(d.pop("azp", UNSET))

        def _parse_azpacr(data: object) -> Union[Any, AzureUserAzpacrType0, Unset]:
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, str):
                    raise TypeError()
                _azpacr_type_0 = data
                azpacr_type_0: Union[Unset, AzureUserAzpacrType0]
                if isinstance(_azpacr_type_0, Unset):
                    azpacr_type_0 = UNSET
                else:
                    azpacr_type_0 = AzureUserAzpacrType0(_azpacr_type_0)

                return azpacr_type_0
            except:  # noqa: E722
                pass
            return cast(Union[Any, AzureUserAzpacrType0, Unset], data)

        azpacr = _parse_azpacr(d.pop("azpacr", UNSET))

        def _parse_preferred_username(data: object) -> Union[Any, Unset, str]:
            if isinstance(data, Unset):
                return data
            return cast(Union[Any, Unset, str], data)

        preferred_username = _parse_preferred_username(
            d.pop("preferred_username", UNSET)
        )

        is_guest = d.pop("is_guest", UNSET)

        azure_user = cls(
            aud=aud,
            iss=iss,
            iat=iat,
            nbf=nbf,
            exp=exp,
            sub=sub,
            ver=ver,
            claims=claims,
            access_token=access_token,
            idp=idp,
            aio=aio,
            name=name,
            scp=scp,
            roles=roles,
            wids=wids,
            groups=groups,
            oid=oid,
            tid=tid,
            uti=uti,
            rh=rh,
            acct=acct,
            auth_time=auth_time,
            ctry=ctry,
            email=email,
            family_name=family_name,
            fwd=fwd,
            given_name=given_name,
            idtyp=idtyp,
            in_corp=in_corp,
            ipaddr=ipaddr,
            login_hint=login_hint,
            onprem_sid=onprem_sid,
            pwd_exp=pwd_exp,
            pwd_url=pwd_url,
            sid=sid,
            tenant_ctry=tenant_ctry,
            tenant_region_scope=tenant_region_scope,
            upn=upn,
            verified_primary_email=verified_primary_email,
            verified_secondary_email=verified_secondary_email,
            vnet=vnet,
            xms_pdl=xms_pdl,
            xms_pl=xms_pl,
            xms_tpl=xms_tpl,
            ztdid=ztdid,
            acr=acr,
            amr=amr,
            appid=appid,
            appidacr=appidacr,
            unique_name=unique_name,
            azp=azp,
            azpacr=azpacr,
            preferred_username=preferred_username,
            is_guest=is_guest,
        )

        azure_user.additional_properties = d
        return azure_user

    @property
    def additional_keys(self) -> List[str]:
        return list(self.additional_properties.keys())

    def __getitem__(self, key: str) -> Any:
        return self.additional_properties[key]

    def __setitem__(self, key: str, value: Any) -> None:
        self.additional_properties[key] = value

    def __delitem__(self, key: str) -> None:
        del self.additional_properties[key]

    def __contains__(self, key: str) -> bool:
        return key in self.additional_properties
