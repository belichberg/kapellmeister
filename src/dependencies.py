import json
import secrets
import string
from datetime import datetime, timezone
from typing import Optional

from envyaml import EnvYAML
from fastapi import Depends, Request
from fastapi.security import OAuth2PasswordBearer, OAuth2
from jose import jwt, JWTError
from passlib.context import CryptContext

from src.database.models import APIToken, User, Project
from src.models.manager import TokenAPI
from src.models.user import TokenData, JWTToken, UserAPI

env_dep: EnvYAML = EnvYAML()

# cookie_sec = APIKeyCookie(name="session")

# JWT VARIABLES
JWT_KEY: str = env_dep["security.key"]
JWT_ALGORITHM: str = env_dep["security.algorithm"]
JWT_TOKEN_EXPIRE: int = env_dep["security.token_expire"]

# create password context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# create oauth2_schema
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/login/")


def time_utc_now(timestamp: int = None) -> datetime:
    return datetime.fromtimestamp(timestamp, tz=timezone.utc) if timestamp else datetime.now(tz=timezone.utc)


def pwd_verify(plain_password: str, hashed_password: str) -> bool:
    return plain_password and hashed_password and pwd_context.verify(plain_password, hashed_password)


def pwd_hash(plain_password: str) -> str:
    return pwd_context.hash(plain_password)


def token_create(key: str, algorithm: str, data: TokenData) -> JWTToken:
    return JWTToken(
        access_token=jwt.encode(data.dict(), key=key, algorithm=algorithm),
        token_expire=data.exp,
    )


def token_validate(token: str) -> Optional[TokenData]:
    try:
        return TokenData.parse_obj(jwt.decode(token, JWT_KEY, JWT_ALGORITHM))
    except JWTError as error:
        print(error)
        pass


def get_token(request: Request) -> Optional[JWTToken]:
    if request.session.get("token"):
        return JWTToken.parse_obj(json.loads(request.session.get("token")))

    return None


def get_user(token: Optional[JWTToken] = Depends(get_token)) -> Optional[UserAPI]:
    if token:
        # get user data
        token_data: Optional[TokenData] = token_validate(token.access_token)

        if token_data:
            user: UserAPI = UserAPI.parse_obj(User.get(username=token_data.sub).to_dict())
            if user.is_active:
                return user

    return None


def generate_api_token():
    return str("".join(secrets.choice(string.ascii_letters + string.digits) for x in range(40)))


def get_api_token(token: str = Depends(OAuth2(auto_error=False))) -> Optional[TokenAPI]:
    # get and compare tokens
    access_token: APIToken = APIToken.get(token=token)
    if access_token is not None and token == access_token.token:
        return TokenAPI.parse_obj(access_token.to_dict())

    return None


def get_projects_by_id(project_id: list) -> list:
    """Convert list with projects id to list with projects as objects"""
    projects_list: list = []
    for item in project_id:
        projects_list.append(Project.get(id=item))
    return projects_list
