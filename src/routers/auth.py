from datetime import timedelta
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from src.database.models import User
from src.dependencies import pwd_hash, pwd_verify, get_user, JWT_TOKEN_EXPIRE, token_create, JWT_KEY, JWT_ALGORITHM
from src.helpers import get_db, time_utc_now
from src.models.user import UserAPI, TokenData, Token


router = APIRouter()

# add templates to project
templates = Jinja2Templates(directory="templates")

@router.post("/user/", response_model=UserAPI)
def create_user(user: UserAPI, db: Session = Depends(get_db)) -> UserAPI:
    user.password = pwd_hash(user.password)
    return UserAPI.parse_obj(User.create(db, user.dict()).to_dict())


@router.post("/login/")
def login(form: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    """Create login page"""

    username: str = form.username
    password: str = form.password
    print(f'username = {username}')
    user: Optional[UserAPI] = UserAPI.parse_obj(db.query(User).filter_by(username=username).first().to_dict())

    # validate user
    if not user or not pwd_verify(password, user.password if user else ""):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Invalid user or password"
        )

    # build data
    data: TokenData = TokenData(
        sub=user.username,
        exp=time_utc_now() + timedelta(seconds=JWT_TOKEN_EXPIRE)
    )

    # generate token
    token: Token = token_create(JWT_KEY, JWT_ALGORITHM, data)

    # all ok
    return token
    # return get_user()
    # return templates.TemplateResponse("login.html", {"request": request})
