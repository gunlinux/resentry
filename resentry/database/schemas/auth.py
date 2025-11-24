from pydantic import BaseModel
from datetime import datetime


class LoginSchema(BaseModel):
    login: str
    password: str


class RefreshTokenSchema(BaseModel):
    refresh_token: str


class AccessTokenSchema(BaseModel):
    access_token: str


class TokenSchema(RefreshTokenSchema, AccessTokenSchema):
    pass


class TokenPayload(BaseModel):
    user_id: int
    exp: datetime
