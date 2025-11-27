from dataclasses import dataclass
from datetime import datetime, timedelta, timezone

from resentry.database.schemas.auth import (
    LoginSchema,
    RefreshTokenSchema,
    TokenSchema,
    TokenPayload,
)
from resentry.database.models.user import User
from resentry.repos.user import UserRepository
from resentry.core.hashing import Hasher
from resentry.config import settings


import jwt


@dataclass
class JTW:
    _secret: str = settings.SECRET_KEY
    algorithm: str = settings.ALGORITHM

    def _encode(self, payload: dict[str, str | datetime]) -> str:
        return jwt.encode(payload, self._secret, algorithm=self.algorithm)

    def get_refresh_token(self, user_id: int) -> str:
        return self._encode(
            {
                "sub": str(user_id),
                "exp": datetime.now(tz=timezone.utc)
                + timedelta(minutes=settings.REFRESH_TOKEN_EXPIRE_MINUTES),
            }
        )

    def get_access_token(self, user_id: int) -> str:
        return self._encode(
            {
                "sub": str(user_id),
                "exp": datetime.now(tz=timezone.utc)
                + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES),
            }
        )

    def decode(self, encoded: str) -> TokenPayload:
        # jwt.exceptions.ExpiredSignatureError: Signature has expired
        # jwt.exceptions.InvalidSignatureError: Signature verification failed
        return TokenPayload(
            **jwt.decode(encoded, self._secret, algorithms=self.algorithm)
        )


@dataclass(frozen=True)
class Login:
    repo: UserRepository
    hasher: Hasher

    def validate_password(self, user: User, password: str) -> bool:
        return self.hasher.verify_password(password, user.password)

    async def execute(self, body: LoginSchema) -> TokenSchema:
        user_db = await self.repo.get_by_name(body.login)
        if not user_db or not self.validate_password(user_db, body.password):
            raise ValueError("")
        token_gen = JTW()
        return TokenSchema(
            access_token=token_gen.get_access_token(user_id=user_db.id),
            refresh_token=token_gen.get_refresh_token(user_id=user_db.id),
        )


@dataclass(frozen=True)
class RefreshToken:
    async def execute(self, body: RefreshTokenSchema) -> TokenSchema:
        token_gen = JTW()
        data = token_gen.decode(body.refresh_token)
        return TokenSchema(
            access_token=token_gen.get_access_token(user_id=data.sub),
            refresh_token=token_gen.get_refresh_token(user_id=data.sub),
        )
