from datetime import datetime
from typing import Optional, Any, List

from pydantic import BaseModel

from src.database.models import UserRole


class UserAPI(BaseModel):
    id: Optional[int]
    username: str
    password: str
    role: UserRole
    is_active: Optional[bool]
    # projects: List[Project] = []
    projects: List[Any] = []


class TokenData(BaseModel):
    sub: str
    exp: datetime


class JWTToken(BaseModel):
    access_token: str
    token_type: str = "bearer"
    token_expire: datetime


class UserRequestAPI(BaseModel):
    username: str
    is_active: Optional[bool]
