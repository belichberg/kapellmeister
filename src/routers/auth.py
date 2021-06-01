from datetime import timedelta
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.responses import RedirectResponse
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.templating import Jinja2Templates

from src.database.models import User, APIToken
from src.dependencies import time_utc_now, pwd_hash, pwd_verify, JWT_TOKEN_EXPIRE, token_create, JWT_KEY, JWT_ALGORITHM, get_user
from src.models.manager import TokenAPI
from src.models.user import UserAPI, TokenData, JWTToken

router = APIRouter()

# add templates to project
templates = Jinja2Templates(directory="templates")


@router.post("/user/", response_model=UserAPI)
def create_user(user: UserAPI) -> UserAPI:
    user.password = pwd_hash(user.password)
    return UserAPI.parse_obj(User.create(user.dict()).to_dict())


@router.post("/login/")
def login(request: Request, form: OAuth2PasswordRequestForm = Depends()):
    """Create login page"""

    username: str = form.username
    password: str = form.password

    user: Optional[UserAPI] = UserAPI.parse_obj(User.get(username=username).to_dict())

    # validate user
    if not user or not pwd_verify(password, user.password if user else ""):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Invalid user or password")

    # build data
    data: TokenData = TokenData(sub=user.username, exp=time_utc_now() + timedelta(seconds=JWT_TOKEN_EXPIRE))

    # generate token
    token: JWTToken = token_create(JWT_KEY, JWT_ALGORITHM, data)

    request.session["token"] = token.json()
    # response.set_cookie("session", token.access_token)

    return RedirectResponse(url="/", status_code=status.HTTP_303_SEE_OTHER)


@router.get("/users/")
def users():
    """Get all users"""
    return [UserAPI.parse_obj(user.to_dict()) for user in User.get_all()]


@router.delete("/user/{user_id}/")
def delete_user(user_id: int):
    """Delete chosen user"""
    # UserAPI.parse_obj(User.delete(id=user_id))
    return UserAPI.parse_obj(User.delete(id=user_id).to_dict())


@router.post("/is_active/{user_id}/{is_active}")
def change_user_is_active(user_id: str, is_active: bool):
    """Change users status"""
    user: Optional[UserAPI] = UserAPI.parse_obj(User.get(id=user_id).to_dict())
    user.is_active = is_active
    # UserAPI.parse_obj(User.get(id=user_id).update(user.dict()).to_dict())

    # UserAPI.parse_obj(User.update_obj(body=user.dict()).to_dict())
    # return {"status": "ok"}


@router.delete("/token/{token_id}/")
def delete_token(token_id: int):
    """Delete chosen token"""
    return TokenAPI.parse_obj(APIToken.delete(id=token_id).to_dict())
