import typing

from fastapi_identity_sqlalchemy.models import (
    IdentityRole,
    IdentityUser,
    IdentityUserRole,
    IdentityUserClaim,
    IdentityUserLogin,
    IdentityUserToken
)

TUser = typing.TypeVar('TUser', bound=IdentityUser)
TRole = typing.TypeVar('TRole', bound=IdentityRole)
TUserRole = typing.TypeVar('TUserRole', bound=IdentityUserRole)
TUserClaim = typing.TypeVar('TUserClaim', bound=IdentityUserClaim)
TUserLogin = typing.TypeVar('TUserLogin', bound=IdentityUserLogin)
TUserToken = typing.TypeVar('TUserToken', bound=IdentityUserToken)