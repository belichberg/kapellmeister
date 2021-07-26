from datetime import timedelta
from typing import Optional, List, Dict, Any

from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.responses import RedirectResponse
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.templating import Jinja2Templates

from src.database.models import User, Project
from src.dependencies import (
    time_utc_now,
    pwd_hash,
    pwd_verify,
    JWT_TOKEN_EXPIRE,
    token_create,
    JWT_KEY,
    JWT_ALGORITHM,
    get_user,
)
from src.models.user import UserAPI, TokenData, JWTToken, UserRole, UserRequestAPI

router = APIRouter()

# add templates to project
templates = Jinja2Templates(directory="templates")

@router.post("/login/")
async def login(request: Request, form: OAuth2PasswordRequestForm = Depends()):
    """Create login page"""

    username: str = form.username
    password: str = form.password

    if User.get(username=username):
        user: Optional[UserAPI] = UserAPI.parse_obj(User.get(username=username).to_dict())

    else:
        request.session["fail_login_message"]: str = f"Username '{username}' doesn't exist!"
        return RedirectResponse(url="/login", status_code=status.HTTP_303_SEE_OTHER)

    # validate user
    if not pwd_verify(password, user.password if user else ""):
        # raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Invalid user or password")
        request.session["fail_login_message"]: str = f"Invalid Username or Password!"
        return RedirectResponse(url="/login", status_code=status.HTTP_303_SEE_OTHER)

    # build data
    data: TokenData = TokenData(sub=user.id, exp=time_utc_now() + timedelta(seconds=JWT_TOKEN_EXPIRE))

    # generate token
    token: JWTToken = token_create(JWT_KEY, JWT_ALGORITHM, data)

    request.session["token"] = token.access_token
    return RedirectResponse(url="/", status_code=status.HTTP_303_SEE_OTHER)


@router.get("/users/", response_model=List[UserAPI])
async def get_users(user: Optional[UserAPI] = Depends(get_user)) -> List[UserAPI]:
    """Get all users"""
    if user is None or user.role != UserRole.super:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Token"},
        )
    return [UserAPI.parse_obj(user.to_dict()) for user in User.get_all()]


@router.post("/users/", response_model=UserAPI)
async def create_user(data: UserAPI, user: Optional[UserAPI] = Depends(get_user)) -> UserAPI:
    if user is None or user.role != UserRole.super:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Token"},
        )
    data.password = pwd_hash(data.password)
    data.projects = [Project.get(id=project_id) for project_id in data.projects]

    return UserAPI.parse_obj(User.create(data.dict()).to_dict())


@router.delete("/users/{user_id}/", response_model=UserAPI)
async def delete_user(user_id: int, user: Optional[UserAPI] = Depends(get_user)) -> UserAPI:
    """Delete chosen user"""
    if user is None or user.role != UserRole.super:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Token"},
        )
    return UserAPI.parse_obj(User.delete(id=user_id).to_dict())


@router.patch("/users/{user_id}/", response_model=UserAPI)
async def update_user(request: Request, user_id: str, data: UserRequestAPI, user: Optional[UserAPI] = Depends(get_user)) -> UserAPI:
    """Update user data"""
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Token"},
        )
    projects: List[Project] = [Project.get(id=project['id']) for project in data.projects]
    context: Dict[Any] = {"username": data.username, "is_active": data.is_active, "projects": projects}
    if data.check_password:
        if not pwd_verify(data.check_password, user.password if user else ""):
            request.session["fail_password_message"]: str = f"Invalid password!"
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Could not validate credentials",
                headers={"WWW-Authenticate": "Token"},
            )
    if data.new_password:
        context["password"] = pwd_hash(data.new_password)

    return UserAPI.parse_obj(User.update(context, id=user_id).to_dict())


@router.get("/users/current/", response_model=UserAPI)
async def get_current_user(user: Optional[UserAPI] = Depends(get_user)) -> UserAPI:
    """Get current user data"""
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Token"},
        )
    return user
