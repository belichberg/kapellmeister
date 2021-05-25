from typing import Optional

from envyaml import EnvYAML
from fastapi import Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordBearer, OAuth2
from jose import jwt, JWTError
from passlib.context import CryptContext
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from src.database.models import Token
from src.models.manager import TokenAPI
from src.models.user import TokenData, JWTToken

env_dep: EnvYAML = EnvYAML()

# JWT VARIABLES
JWT_KEY: str = env_dep["security.key"]
JWT_ALGORITHM: str = env_dep["security.algorithm"]
JWT_TOKEN_EXPIRE: int = env_dep["security.token_expire"]

# create password context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# create oauth2_schema
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/login/")


def pwd_verify(plain_password: str, hashed_password: str) -> bool:
    return plain_password and hashed_password and pwd_context.verify(plain_password, hashed_password)


def pwd_hash(plain_password: str) -> str:
    return pwd_context.hash(plain_password)


def token_validate(token: str) -> Optional[TokenData]:
    try:
        return TokenData.parse_obj(jwt.decode(token, JWT_KEY, JWT_ALGORITHM))
    except JWTError:
        pass


def get_user():
    pass


def token_create(key: str, algorithm: str, data: TokenData) -> JWTToken:
    return JWTToken(
        access_token=jwt.encode(data.dict(), key=key, algorithm=algorithm),
        token_expire=data.exp,
    )


def get_api_token(request: Request, token: str = Depends(OAuth2())) -> TokenAPI:
    # create connection to database
    session: Session = request.state.db

    try:
        # get and compare tokens
        access_token: Token = session.query(Token).filter_by(token=token).first()
        if access_token is None or token != access_token.token:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate credentials",
                headers={"WWW-Authenticate": "Token"},
            )

        return TokenAPI.parse_obj(access_token.to_dict())

    except SQLAlchemyError as err:
        print("Database error:", err)
