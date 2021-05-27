from datetime import datetime
from enum import Enum

from pydantic import BaseModel


class UserRole(str, Enum):
    super = "super"
    admin = "admin"
    user = "user"


class UserAPI(BaseModel):
    username: str
    password: str
    role: UserRole
    is_active: bool


class TokenData(BaseModel):
    sub: str
    exp: datetime


class JWTToken(BaseModel):
    access_token: str
    token_type: str = "bearer"
    token_expire: datetime
