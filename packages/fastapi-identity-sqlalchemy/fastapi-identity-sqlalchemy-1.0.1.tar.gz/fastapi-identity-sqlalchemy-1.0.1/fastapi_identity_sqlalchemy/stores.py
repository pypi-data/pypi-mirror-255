import uuid
from datetime import datetime
from typing import Generic, Type, Optional, Final

from fastapi_identity.user_login_info import UserLoginInfo
from sqlalchemy import select, delete, insert, update, and_
from sqlalchemy.ext.asyncio import AsyncSession

from fastapi_identity.core.exc import ArgumentNoneError
from fastapi_identity.identity_result import IdentityResult
from fastapi_identity.core.claims import Claim
from fastapi_identity.stores import (
    IRoleStore,
    IUserAuthenticationTokenStore,
    IUserAuthenticatorKeyStore,
    IUserClaimStore,
    IUserEmailStore,
    IUserLockoutStore,
    IUserLoginStore,
    IUserPasswordStore,
    IUserPhoneNumberStore,
    IUserRoleStore,
    IUserSecurityStampStore,
    IUserTwoFactorRecoveryCodeStore,
    IUserTwoFactorStore,
    IUserStore
)

from fastapi_identity_sqlalchemy.exc import RoleNotFound
from fastapi_identity_sqlalchemy.models import (
    IdentityRole,
    IdentityUser,
    IdentityUserRole,
    IdentityUserClaim,
    IdentityUserLogin,
    IdentityUserToken
)
from fastapi_identity_sqlalchemy.types import TRole, TUser, TUserRole, TUserClaim, TUserLogin, TUserToken


class SQLAlchemyRoleStore(IRoleStore[TRole], Generic[TRole]):
    role_model: Type[IdentityRole] = IdentityRole

    def __init__(self, session: AsyncSession):
        self.session = session

    def create_model_from_dict(self, **kwargs):
        return self.role_model(**kwargs)

    async def save_changes(self):
        await self.session.commit()

    async def refresh(self, role):
        await self.session.refresh(role)

    async def all(self) -> list[TRole]:
        statement = select(self.role_model)
        return list((await self.session.scalars(statement)).all())

    async def create(self, role: TRole) -> IdentityResult:
        if role is None:
            raise ArgumentNoneError("role")

        self.session.add(role)
        await self.save_changes()
        await self.refresh(role)
        return IdentityResult.success()

    async def update(self, role: TRole) -> IdentityResult:
        if role is None:
            raise ArgumentNoneError("role")

        role.concurrency_stamp = str(uuid.uuid4())
        await self.save_changes()
        await self.refresh(role)
        return IdentityResult.success()

    async def delete(self, role: TRole) -> IdentityResult:
        if role is None:
            raise ArgumentNoneError("role")

        await self.session.delete(role)
        await self.save_changes()
        return IdentityResult.success()

    async def find_by_id(self, role_id: str) -> Optional[TRole]:
        if role_id is None:
            raise ArgumentNoneError("role_id")

        statement = select(self.role_model).where(self.role_model.id == role_id)
        return await self._find_role(statement)

    async def find_by_name(self, normalized_name: str) -> Optional[TRole]:
        if normalized_name is None:
            raise ArgumentNoneError("normalized_name")

        statement = select(self.role_model).where(self.role_model.normalized_name == normalized_name)
        return await self._find_role(statement)

    async def get_role_id(self, role: TRole) -> str:
        if role is None:
            raise ArgumentNoneError("role")

        return str(role.id)

    async def get_role_name(self, role: TRole) -> Optional[str]:
        if role is None:
            raise ArgumentNoneError("role")

        return role.name

    async def set_role_name(self, role: TRole, role_name: Optional[str]) -> None:
        if role is None:
            raise ArgumentNoneError("role")

        role.name = role_name

    async def get_normalized_role_name(self, role: TRole) -> Optional[str]:
        if role is None:
            raise ArgumentNoneError("role")

        return role.normalized_name

    async def set_normalized_role_name(self, role: TRole, normalized_name: Optional[str]) -> None:
        if role is None:
            raise ArgumentNoneError("role")

        role.normalized_name = normalized_name

    async def _find_role(self, statement) -> Optional[TRole]:
        return (await self.session.execute(statement)).scalar_one_or_none()


class SQLAlchemyUserStore(
    IUserAuthenticationTokenStore[TUser],
    IUserAuthenticatorKeyStore[TUser],
    IUserClaimStore[TUser],
    IUserEmailStore[TUser],
    IUserLockoutStore[TUser],
    IUserLoginStore[TUser],
    IUserPasswordStore[TUser],
    IUserPhoneNumberStore[TUser],
    IUserRoleStore[TUser],
    IUserSecurityStampStore[TUser],
    IUserTwoFactorRecoveryCodeStore[TUser],
    IUserTwoFactorStore[TUser],
    IUserStore[TUser],
    Generic[TUser]
):
    user_model: Type[TUser] = IdentityUser
    role_model: Type[TRole] = IdentityRole
    user_role_model: Type[TUserRole] = IdentityUserRole
    user_claim_model: Type[TUserClaim] = IdentityUserClaim
    user_login_model: Type[TUserLogin] = IdentityUserLogin
    user_token_model: Type[TUserToken] = IdentityUserToken

    InternalLoginProvider: Final[str] = "[FastAPIUserStore]"
    AuthenticatorKeyTokenName: Final[str] = "AuthenticatorKey"
    RecoveryCodeTokenName: Final[str] = "RecoveryCodes"

    def __init__(self, session: AsyncSession):
        self.session: AsyncSession = session

    def create_model_from_dict(self, **kwargs) -> TUser:
        return self.user_model(**kwargs)

    async def save_changes(self):
        await self.session.commit()

    async def refresh(self, role):
        await self.session.refresh(role)

    async def all(self) -> list[TUser]:
        statement = select(self.user_model)
        return list((await self.session.scalars(statement)).all())

    async def create(self, user: TUser) -> IdentityResult:
        if user is None:
            raise ArgumentNoneError("user")

        self.session.add(user)
        await self.save_changes()
        await self.refresh(user)
        return IdentityResult.success()

    async def update(self, user: TUser) -> IdentityResult:
        if user is None:
            raise ArgumentNoneError("user")

        user.concurrency_stamp = str(uuid.uuid4())
        await self.save_changes()
        await self.refresh(user)
        return IdentityResult.success()

    async def delete(self, user: TUser) -> IdentityResult:
        if user is None:
            raise ArgumentNoneError("user")

        await self.session.delete(user)
        await self.save_changes()
        return IdentityResult.success()

    async def find_by_id(self, user_id: str) -> Optional[TUser]:
        if user_id is None:
            raise ArgumentNoneError("user_id")

        statement = select(self.user_model).where(self.user_model.id == user_id)
        return await self._find_user(statement)

    async def find_by_name(self, normalized_username: str) -> Optional[TUser]:
        if normalized_username is None:
            raise ArgumentNoneError("normalized_username")

        statement = select(self.user_model).where(self.user_model.normalized_username == normalized_username)
        return await self._find_user(statement)

    async def get_user_id(self, user: TUser) -> str:
        if user is None:
            raise ArgumentNoneError("user")

        return str(user.id)

    async def get_username(self, user: TUser) -> Optional[str]:
        if user is None:
            raise ArgumentNoneError("user")

        return user.username

    async def set_username(self, user: TUser, username: Optional[str]) -> None:
        if user is None:
            raise ArgumentNoneError("user")

        user.username = username

    async def get_normalized_username(self, user: TUser) -> Optional[str]:
        if user is None:
            raise ArgumentNoneError("user")

        return user.normalized_username

    async def set_normalized_username(self, user: TUser, normalized_name: Optional[str]) -> None:
        if user is None:
            raise ArgumentNoneError("user")

        user.normalized_username = normalized_name

    async def find_by_email(self, normalized_email: str) -> Optional[TUser]:
        if normalized_email is None:
            raise ArgumentNoneError("normalized_email")

        statement = select(self.user_model).where(self.user_model.normalized_email == normalized_email)
        return await self._find_user(statement)

    async def get_email(self, user: TUser) -> Optional[str]:
        if user is None:
            raise ArgumentNoneError("user")

        return user.email

    async def set_email(self, user: TUser, email: Optional[str]) -> None:
        if user is None:
            raise ArgumentNoneError("user")

        user.email = email

    async def get_email_confirmed(self, user: TUser) -> bool:
        if user is None:
            raise ArgumentNoneError("user")

        return user.email and user.email_confirmed

    async def get_normalized_email(self, user: TUser) -> Optional[str]:
        if user is None:
            raise ArgumentNoneError("user")

        return user.normalized_email

    async def set_normalized_email(self, user: TUser, normalized_email: Optional[str]) -> None:
        if user is None:
            raise ArgumentNoneError("user")

        user.normalized_email = normalized_email

    async def set_email_confirmed(self, user: TUser, confirmed: bool) -> None:
        if user is None:
            raise ArgumentNoneError("user")

        user.email_confirmed = confirmed

    async def get_password_hash(self, user: TUser) -> Optional[str]:
        if user is None:
            raise ArgumentNoneError("user")

        return user.password_hash

    async def has_password(self, user: TUser) -> bool:
        if user is None:
            raise ArgumentNoneError("user")

        return bool(user.password_hash)

    async def set_password_hash(self, user: TUser, password_hash: str) -> None:
        if user is None:
            raise ArgumentNoneError("user")

        user.password_hash = password_hash

    async def get_phone_number(self, user: TUser) -> Optional[str]:
        if user is None:
            raise ArgumentNoneError("user")

        return user.phone_number

    async def set_phone_number(self, user: TUser, phone_number: Optional[str]) -> None:
        if user is None:
            raise ArgumentNoneError("user")

        user.phone_number = phone_number

    async def get_phone_number_confirmed(self, user: TUser) -> bool:
        if user is None:
            raise ArgumentNoneError("user")

        return user.phone_number and user.phone_number_confirmed

    async def set_phone_number_confirmed(self, user: TUser, confirmed: bool) -> None:
        if user is None:
            raise ArgumentNoneError("user")

        user.phone_number_confirmed = confirmed

    async def get_access_failed_count(self, user: TUser) -> int:
        if user is None:
            raise ArgumentNoneError("user")

        return user.access_failed_count

    async def get_lockout_enabled(self, user: TUser) -> bool:
        if user is None:
            raise ArgumentNoneError("user")

        return user.lockout_enabled

    async def get_lockout_end_date(self, user: TUser) -> Optional[datetime]:
        if user is None:
            raise ArgumentNoneError("user")

        return user.lockout_end

    async def increment_access_failed_count(self, user: TUser) -> int:
        if user is None:
            raise ArgumentNoneError("user")

        return user.access_failed_count + 1

    async def reset_access_failed_count(self, user: TUser) -> None:
        if user is None:
            raise ArgumentNoneError("user")

        user.access_failed_count = 0

    async def set_lockout_enabled(self, user: TUser, enabled: bool) -> None:
        if user is None:
            raise ArgumentNoneError("user")

        user.lockout_enabled = enabled

    async def set_lockout_end_date(self, user: TUser, lockout_end: Optional[datetime]) -> None:
        if user is None:
            raise ArgumentNoneError("user")

        user.lockout_end = lockout_end

    async def get_security_stamp(self, user: TUser) -> Optional[str]:
        if user is None:
            raise ArgumentNoneError("user")

        return str(user.security_stamp) if user.security_stamp else None

    async def set_security_stamp(self, user: TUser, stamp: str) -> None:
        if user is None:
            raise ArgumentNoneError("user")
        if not stamp:
            raise ArgumentNoneError("stamp")

        user.security_stamp = stamp

    async def add_to_role(self, user: TUser, normalized_role_name: str) -> None:
        if user is None:
            raise ArgumentNoneError("user")
        if not normalized_role_name:
            raise ArgumentNoneError("normalized_role_name")

        if role := await self._find_role(normalized_role_name):
            statement = insert(self.user_role_model).values(user_id=user.id, role_id=role.id)
            await self.session.execute(statement)
            return

        raise RoleNotFound(normalized_role_name)

    async def get_roles(self, user: TUser) -> list[str]:
        if user is None:
            raise ArgumentNoneError("user")

        statement = select(self.role_model.name).where(
            and_(
                self.user_model.id == user.id,
                self.user_model.id == self.user_role_model.user_id,
                self.role_model.id == self.user_role_model.role_id
            )
        )
        roles = (await self.session.scalars(statement)).all()
        return list(roles)

    async def get_users_in_role(self, normalized_role_name: str) -> list[TUser]:
        if not normalized_role_name:
            raise ArgumentNoneError("normalized_role_name")

        if role := await self._find_role(normalized_role_name):
            users: list[TUser] = await role.awaitable_attrs.users
            return users

        raise RoleNotFound(normalized_role_name)

    async def is_in_role(self, user: TUser, normalized_role_name: str) -> bool:
        if not normalized_role_name:
            raise ArgumentNoneError("normalized_role_name")

        if role := await self._find_role(normalized_role_name):
            statement = select(self.user_role_model).where(
                and_(
                    self.user_role_model.user_id == user.id,
                    self.user_role_model.role_id == role.id
                )
            )
            result = await self.session.scalars(statement)
            return bool(result.one_or_none())

        return False

    async def remove_from_role(self, user: TUser, normalized_role_name: str) -> None:
        if user is None:
            raise ArgumentNoneError("user")
        if not normalized_role_name:
            raise ArgumentNoneError("normalized_role_name")

        if role := await self._find_role(normalized_role_name):
            statement = delete(self.user_role_model).where(
                and_(
                    self.user_role_model.user_id == user.id,
                    self.user_role_model.role_id == role.id
                )
            )
            await self.session.execute(statement)

    async def add_login(self, user: TUser, login: UserLoginInfo) -> None:
        if user is None:
            raise ArgumentNoneError("user")
        if login is None:
            raise ArgumentNoneError("login")

        self.session.add(self._create_user_login(user, login))
        await self.save_changes()

    async def find_by_login(self, login_provider: str, provider_key: str) -> Optional[TUser]:
        if not login_provider:
            raise ArgumentNoneError("login_provider")
        if not provider_key:
            raise ArgumentNoneError("provider_key")

        statement = select(self.user_login_model).where(
            and_(
                self.user_login_model.login_provider == login_provider,
                self.user_login_model.provider_key == provider_key
            )
        )

        if user_login := (await self.session.scalars(statement)).one_or_none():
            statement = select(self.user_model).where(self.user_model.id == user_login.user_id)
            return await self._find_user(statement)

    async def get_logins(self, user: TUser) -> list[UserLoginInfo]:
        if user is None:
            raise ArgumentNoneError("user")

        statement = select(self.user_login_model).where(self.user_login_model.user_id == user.id)
        user_logins = (await self.session.scalars(statement)).all()
        return [self._create_user_login_info(ul) for ul in user_logins]

    async def remove_login(self, user: TUser, login_provider: str, provider_key: str) -> None:
        if user is None:
            raise ArgumentNoneError("user")
        if not login_provider:
            raise ArgumentNoneError("login_provider")
        if not provider_key:
            raise ArgumentNoneError("provider_key")

        statement = delete(self.user_login_model).where(
            and_(
                self.user_login_model.user_id == user.id,
                self.user_login_model.login_provider == login_provider,
                self.user_login_model.provider_key == provider_key
            )
        )
        await self.session.execute(statement)

    async def get_token(self, user: TUser, login_provider: str, name: str) -> Optional[str]:
        if user is None:
            raise ArgumentNoneError("user")
        if not login_provider:
            raise ArgumentNoneError("login_provider")
        if not name:
            raise ArgumentNoneError("name")

        if token := await self._find_token(user, login_provider, name):
            return token.value

    async def remove_token(self, user: TUser, login_provider: str, name: str) -> None:
        if user is None:
            raise ArgumentNoneError("user")
        if not login_provider:
            raise ArgumentNoneError("login_provider")
        if not name:
            raise ArgumentNoneError("name")

        statement = delete(self.user_token_model).where(
            and_(
                self.user_token_model.user_id == user.id,
                self.user_token_model.login_provider == login_provider,
                self.user_token_model.name == name
            )
        )
        await self.session.execute(statement)

    async def set_token(self, user: TUser, login_provider: str, name: str, value: Optional[str]) -> None:
        if user is None:
            raise ArgumentNoneError("user")
        if not login_provider:
            raise ArgumentNoneError("login_provider")
        if not name:
            raise ArgumentNoneError("name")

        if token := await self._find_token(user, login_provider, name):
            token.value = value
            await self.save_changes()
            return

        self.session.add(self._create_user_token(user, login_provider, name, value))
        await self.save_changes()

    async def get_two_factor_enabled(self, user: TUser) -> bool:
        if user is None:
            raise ArgumentNoneError("user")

        return user.two_factor_enabled

    async def set_two_factor_enabled(self, user: TUser, enabled: bool) -> None:
        if user is None:
            raise ArgumentNoneError("user")

        user.two_factor_enabled = enabled

    async def get_authenticator_key(self, user: TUser) -> Optional[str]:
        return await self.get_token(user, self.InternalLoginProvider, self.AuthenticatorKeyTokenName)

    async def set_authenticator_key(self, user: TUser, key: str) -> None:
        return await self.set_token(user, self.InternalLoginProvider, self.AuthenticatorKeyTokenName, key)

    async def count_codes(self, user: TUser) -> int:
        if user is None:
            raise ArgumentNoneError("user")

        merged_codes = (await self.get_token(user, self.InternalLoginProvider, self.RecoveryCodeTokenName)) or ""

        if merged_codes:
            return merged_codes.count(';') + 1

        return 0

    async def redeem_code(self, user: TUser, code: str) -> bool:
        if user is None:
            raise ArgumentNoneError("user")
        if not code:
            raise ArgumentNoneError("code")

        merged_codes = (await self.get_token(user, self.InternalLoginProvider, self.RecoveryCodeTokenName)) or ""
        split_codes = merged_codes.split(';')

        if code in split_codes:
            split_codes.remove(code)
            await self.replace_codes(user, *split_codes)
            return True

        return False

    async def replace_codes(self, user: TUser, *recovery_codes: str) -> None:
        if user is None:
            raise ArgumentNoneError("user")
        if not recovery_codes:
            raise ArgumentNoneError("recovery_codes")

        merged_codes = ';'.join(recovery_codes)
        return await self.set_token(user, self.InternalLoginProvider, self.RecoveryCodeTokenName, merged_codes)

    async def add_claims(self, user: TUser, *claims: Claim) -> None:
        if user is None:
            raise ArgumentNoneError("user")
        if not claims:
            raise ArgumentNoneError("claims")

        self.session.add_all(self._create_user_claim(user, claim) for claim in claims)
        await self.save_changes()

    async def get_claims(self, user: TUser) -> list[Claim]:
        if user is None:
            raise ArgumentNoneError("user")

        statement = select(self.user_claim_model).where(self.user_claim_model.user_id == user.id)
        user_claims = (await self.session.scalars(statement)).all()
        return [self._create_claim(uc) for uc in user_claims]

    async def get_users_for_claim(self, claim: Claim) -> list[TUser]:
        if claim is None:
            raise ArgumentNoneError("claim")

        statement = select(self.user_claim_model).where(
            and_(
                self.user_claim_model.claim_type == claim.type,
                self.user_claim_model.claim_value == claim.value
            )
        )
        user_claims = (await self.session.scalars(statement)).all()
        return [await uc.awaitable_attrs.user for uc in user_claims]

    async def remove_claims(self, user: TUser, *claims: Claim) -> None:
        if user is None:
            raise ArgumentNoneError("user")
        if not claims:
            raise ArgumentNoneError("claims")

        for claim in claims:
            statement = select(self.user_claim_model).where(
                and_(
                    self.user_claim_model.user_id == user.id,
                    self.user_claim_model.claim_type == claim.type,
                    self.user_claim_model.claim_value == claim.value
                )
            )

            matches_claims = (await self.session.scalars(statement)).all()

            for c in matches_claims:
                await self.session.delete(c)

        await self.save_changes()

    async def replace_claim(self, user: TUser, claim: Claim, new_claim: Claim) -> None:
        if user is None:
            raise ArgumentNoneError("user")
        if claim is None:
            raise ArgumentNoneError("claim")
        if new_claim is None:
            raise ArgumentNoneError("new_claim")

        statement = update(self.user_claim_model).where(
            and_(
                self.user_claim_model.user_id == user.id,
                self.user_claim_model.claim_type == claim.type,
                self.user_claim_model.claim_value == claim.value
            )
        ).values(claim_type=new_claim.type, claim_value=new_claim.value)

        await self.session.execute(statement)

    def _create_claim(self, model: TUserClaim) -> Claim:  # noqa
        return Claim(
            _type=model.claim_type,
            _value=model.claim_value,
        )

    def _create_user_claim(self, user: TUser, claim: Claim) -> TUserClaim:
        return self.user_claim_model(
            user_id=user.id,
            claim_type=claim.type,
            claim_value=claim.value
        )

    def _create_user_token(self, user: TUser, login_provider: str, name: str, value: Optional[str]) -> TUserToken:
        return self.user_token_model(
            user_id=user.id,
            login_provider=login_provider,
            name=name,
            value=value
        )

    def _create_user_login_info(self, model: TUserLogin) -> UserLoginInfo:  # noqa
        return UserLoginInfo(
            login_provider=model.login_provider,
            provider_key=model.provider_key,
            display_name=model.provider_display_name
        )

    def _create_user_login(self, user: TUser, login: UserLoginInfo) -> TUserLogin:
        return self.user_login_model(
            user_id=user.id,
            login_provider=login.login_provider,
            provider_display_name=login.display_name,
            provider_key=login.provider_key
        )

    async def _find_token(self, user: TUser, login_provider: str, name: str) -> TUserToken:
        statement = select(self.user_token_model).where(
            and_(
                self.user_token_model.user_id == user.id,
                self.user_token_model.login_provider == login_provider,
                self.user_token_model.name == name
            )
        )
        result = await self.session.scalars(statement)
        return result.one_or_none()

    async def _find_user(self, statement) -> Optional[TUser]:
        result = await self.session.scalars(statement)
        return result.one_or_none()

    async def _find_role(self, name: str) -> Optional[TRole]:
        result = await self.session.scalars(
            select(self.role_model)
            .where(self.role_model.normalized_name == name)
        )
        return result.one_or_none()
