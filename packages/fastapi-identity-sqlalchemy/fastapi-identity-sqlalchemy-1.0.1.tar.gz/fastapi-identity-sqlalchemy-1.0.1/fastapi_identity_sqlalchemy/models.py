import datetime
import typing
import uuid

import sqlalchemy as sa
from sqlalchemy.ext.asyncio import AsyncAttrs
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class DbModel(AsyncAttrs, DeclarativeBase):

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({','.join(
            f"{k}={v!r}" for k, v in self.__dict__.items()
            if not k.startswith(('_', '__',))
        )})"


class IdentityUser(DbModel):
    __tablename__ = "identity_users"
    __table_args__ = {'extend_existing': True}

    access_failed_count: Mapped[int] = mapped_column(sa.Boolean, default=0)
    concurrency_stamp: Mapped[typing.Optional[uuid.UUID]] = mapped_column(sa.String(36), nullable=True)
    email: Mapped[typing.Optional[str]] = mapped_column(sa.String(256), nullable=True)
    email_confirmed: Mapped[bool] = mapped_column(sa.Boolean, default=False)
    id: Mapped[uuid.UUID] = mapped_column(sa.String(36), primary_key=True)
    lockout_enabled: Mapped[bool] = mapped_column(sa.Boolean, default=True)
    lockout_end: Mapped[typing.Optional[datetime.datetime]] = mapped_column(sa.TIMESTAMP(timezone=True), nullable=True)
    normalized_email: Mapped[typing.Optional[str]] = mapped_column(sa.String(256), nullable=True, unique=True)
    normalized_username: Mapped[typing.Optional[str]] = mapped_column(sa.String(256), nullable=True, unique=True)
    password_hash: Mapped[typing.Optional[str]] = mapped_column(sa.Text, nullable=True)
    phone_number: Mapped[typing.Optional[str]] = mapped_column(sa.String(256), nullable=True)
    phone_number_confirmed: Mapped[bool] = mapped_column(sa.Boolean, default=False)
    security_stamp: Mapped[typing.Optional[uuid.UUID]] = mapped_column(sa.String(36), nullable=True)
    two_factor_enabled: Mapped[bool] = mapped_column(sa.Boolean, default=False)
    username: Mapped[typing.Optional[str]] = mapped_column(sa.String(256), nullable=True)

    roles: Mapped[typing.List['IdentityRole']] = relationship(
        "IdentityRole", secondary="identity_user_roles", back_populates="users"
    )
    claims: Mapped[typing.List['IdentityUserClaim']] = relationship("IdentityUserClaim", back_populates="user")
    logins: Mapped[typing.List['IdentityUserLogin']] = relationship("IdentityUserLogin", back_populates="user")
    tokens: Mapped[typing.List['IdentityUserToken']] = relationship("IdentityUserToken", back_populates="user")

    def __init__(
            self,
            username: str = None,
            email: str = None,
            phone_number: str = None,
            lockout_enabled: bool = True,
            two_factor_enabled: bool = False,
            **kwargs
    ):
        super().__init__(
            id=str(uuid.uuid4()),
            security_stamp=str(uuid.uuid4()),
            username=username,
            email=email,
            lockout_enabled=lockout_enabled,
            phone_number=phone_number,
            two_factor_enabled=two_factor_enabled,
            **kwargs
        )

    def __str__(self):
        return self.username or self.email or self.id


class IdentityRole(DbModel):
    __tablename__ = "identity_roles"
    __table_args__ = {'extend_existing': True}

    concurrency_stamp: Mapped[typing.Optional[uuid.UUID]] = mapped_column(sa.String(36), nullable=True)
    id: Mapped[uuid.UUID] = mapped_column(sa.String(36), primary_key=True)
    name: Mapped[typing.Optional[str]] = mapped_column(sa.String(256), nullable=True)
    normalized_name: Mapped[typing.Optional[str]] = mapped_column(sa.String(256), nullable=True, unique=True)

    users: Mapped[typing.List['IdentityUser']] = relationship(
        "IdentityUser", secondary="identity_user_roles", back_populates="roles"
    )

    def __init__(self, name: str = None, **kwargs):
        super().__init__(
            id=str(uuid.uuid4()),
            name=name,
            **kwargs
        )

    def __str__(self):
        return self.name or self.id


class IdentityUserRole(DbModel):
    __tablename__ = "identity_user_roles"
    __table_args__ = {'extend_existing': True}

    user_id = sa.Column(sa.String(36), sa.ForeignKey(
        "identity_users.id", ondelete="CASCADE"), primary_key=True
                        )
    role_id = sa.Column(sa.String(36), sa.ForeignKey(
        "identity_roles.id", ondelete="CASCADE"), primary_key=True
                        )


class IdentityUserClaim(DbModel):
    __tablename__ = "identity_user_claims"
    __table_args__ = {'extend_existing': True}

    claim_type: Mapped[typing.Optional[str]] = mapped_column(sa.String(455), primary_key=True)
    claim_value: Mapped[typing.Optional[str]] = mapped_column(sa.Text, nullable=True)
    user_id: Mapped[uuid.UUID] = mapped_column(
        sa.ForeignKey("identity_users.id", ondelete="CASCADE"),
        primary_key=True
    )

    user: Mapped['IdentityUser'] = relationship("IdentityUser", back_populates="claims")


class IdentityUserLogin(DbModel):
    __tablename__ = "identity_user_logins"
    __table_args__ = {'extend_existing': True}

    login_provider: Mapped[str] = mapped_column(sa.String(256), primary_key=True)
    provider_key: Mapped[str] = mapped_column(sa.String(256))
    provider_display_name: Mapped[typing.Optional[str]] = mapped_column(sa.Text, nullable=True)
    user_id: Mapped[uuid.UUID] = mapped_column(sa.ForeignKey(
        "identity_users.id", ondelete="CASCADE"),
        primary_key=True
    )

    user: Mapped['IdentityUser'] = relationship("IdentityUser", back_populates="logins")


class IdentityUserToken(DbModel):
    __tablename__ = "identity_user_tokens"
    __table_args__ = {'extend_existing': True}

    login_provider: Mapped[str] = mapped_column(sa.String(256), primary_key=True)
    name: Mapped[str] = mapped_column(sa.String(256))
    value: Mapped[typing.Optional[str]] = mapped_column(sa.Text, nullable=True)
    user_id: Mapped[uuid.UUID] = mapped_column(
        sa.ForeignKey("identity_users.id", ondelete="CASCADE"),
        primary_key=True
    )

    user: Mapped['IdentityUser'] = relationship("IdentityUser", back_populates="tokens")
