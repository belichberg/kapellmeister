from datetime import timedelta
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.responses import RedirectResponse
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.templating import Jinja2Templates

from src.database.models import User, APIToken, user_project_table, Project
from src.dependencies import time_utc_now, pwd_hash, pwd_verify, JWT_TOKEN_EXPIRE, token_create, JWT_KEY, JWT_ALGORITHM, \
    get_user, get_projects_by_id
from src.models.manager import TokenAPI, ProjectAPI
from src.models.user import UserAPI, TokenData, JWTToken, UserRole
from src.database.helpers import ModelMixin, session

router = APIRouter()

# add templates to project
templates = Jinja2Templates(directory="templates")


@router.post("/user/", response_model=UserAPI)
def create_user(data: UserAPI, user: Optional[UserAPI] = Depends(get_user)) -> UserAPI:
    print(data)
    if user is None or user.role != UserRole.super:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Token"},
        )
    data.password = pwd_hash(data.password)
    data.projects = get_projects_by_id(data.projects)
    return UserAPI.parse_obj(User.create(data.dict()).to_dict())


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
    return UserAPI.parse_obj(User.delete(id=user_id).to_dict())


@router.patch("/is_active/{user_id}/{is_active}")
def change_user_is_active(user_id: str, is_active: bool):
    """Change users status"""
    return UserAPI.parse_obj(User.update({"is_active": is_active}, id=user_id).to_dict())


@router.delete("/token/{token_id}/")
def delete_token(token_id: int):
    """Delete chosen token"""
    return TokenAPI.parse_obj(APIToken.delete(id=token_id).to_dict())


@router.patch("/add/{user_id}/{project_id}/")
def add_user_project(user_id: int, project_id: int):
    """Add project to user"""
    user: Optional[UserAPI] = UserAPI.parse_obj(User.get(id=user_id).to_dict())
    new_projects_list: list = []
    if user.projects:
        new_projects_list = user.projects.copy()
        if Project.get(id=project_id) in new_projects_list:
            new_projects_list.remove(Project.get(id=project_id))
        else:
            new_projects_list.append(Project.get(id=project_id))
    else:
        new_projects_list = [Project.get(id=project_id)]
    UserAPI.parse_obj(User.update({"projects": new_projects_list}, id=user_id).to_dict())
    return {"status": "ok"}

