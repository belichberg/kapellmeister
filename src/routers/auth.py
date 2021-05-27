from datetime import timedelta
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.responses import RedirectResponse
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.templating import Jinja2Templates

from src.database.models import User
from src.dependencies import time_utc_now, pwd_hash, pwd_verify, JWT_TOKEN_EXPIRE, token_create, JWT_KEY, JWT_ALGORITHM
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

    # all ok
    # return token
    # return request.session.get('token')
    return RedirectResponse(url="/", status_code=status.HTTP_303_SEE_OTHER)
    # return templates.TemplateResponse("index.html",
    #                                       {"request": request, "username": username})
