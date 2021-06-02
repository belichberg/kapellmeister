from datetime import datetime
from enum import Enum
from typing import Optional

from pydantic import BaseModel


class UserRole(str, Enum):
    super = "super"
    admin = "admin"
    user = "user"


class UserAPI(BaseModel):
    id: Optional[int]
    username: str
    password: str
    role: UserRole
    is_active: Optional[bool]


class TokenData(BaseModel):
    sub: str
    exp: datetime


class JWTToken(BaseModel):
    access_token: str
    token_type: str = "bearer"
    token_expire: datetime


class UserProject(BaseModel):
    user_id: int
    project_id: int
