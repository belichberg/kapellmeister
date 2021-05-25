from datetime import datetime

from pydantic import BaseModel


class UserAPI(BaseModel):
    username: str
    password: str


class TokenData(BaseModel):
    sub: str
    exp: datetime


class JWTToken(BaseModel):
    access_token: str
    token_type: str = "bearer"
    token_expire: datetime
