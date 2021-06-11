from datetime import timedelta
from typing import Optional, List

from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.responses import RedirectResponse
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.templating import Jinja2Templates

from src.database.models import User, APIToken, Project
from src.dependencies import time_utc_now, pwd_hash, pwd_verify, JWT_TOKEN_EXPIRE, token_create, JWT_KEY, JWT_ALGORITHM, \
    get_user
from src.models.manager import TokenAPI, ProjectAPI
from src.models.user import UserAPI, TokenData, JWTToken, UserRole, UserRequestAPI

router = APIRouter()


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

    request.session["token"] = token.access_token
    return RedirectResponse(url="/", status_code=status.HTTP_303_SEE_OTHER)


@router.get("/users/", response_model=List[UserAPI])
def get_users() -> List[UserAPI]:
    """Get all users"""
    return [UserAPI.parse_obj(user.to_dict()) for user in User.get_all()]


@router.post("/users/", response_model=UserAPI)
def create_user(data: UserAPI, user: Optional[UserAPI] = Depends(get_user)) -> UserAPI:
    if user is None or user.role != UserRole.super:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Token"},
        )
    data.password = pwd_hash(data.password)
    data.projects = [ProjectAPI.parse_obj(project.to_dict()) for project in Project.get(id=data.projects)]

    return UserAPI.parse_obj(User.create(data.dict()).to_dict())


@router.delete("/users/{user_id}/", response_model=UserAPI)
def delete_user(user_id: int) -> UserAPI:
    """Delete chosen user"""
    return UserAPI.parse_obj(User.delete(id=user_id).to_dict())


@router.patch("/users/{user_id}/", response_model=UserAPI)
def update_user(user_id: str, data: UserRequestAPI) -> UserAPI:
    """Change users status"""
    return UserAPI.parse_obj(User.update(data.dict(), id=user_id).to_dict())


@router.patch("/users/{user_id}/{project_id}/", response_model=UserAPI)
def add_user_project(user_id: int, project_id: int) -> UserAPI:
    """Add project to user"""
    user: Optional[UserAPI] = UserAPI.parse_obj(User.get(id=user_id).to_dict())
    if user.projects:
        projects: List[Project] = user.projects.copy()
        if Project.get(id=project_id) in projects:
            projects.remove(Project.get(id=project_id))
        else:
            projects.append(Project.get(id=project_id))
    else:
        projects: List[Project] = [Project.get(id=project_id)]
    return UserAPI.parse_obj(User.update({"projects": projects}, id=user_id).to_dict())
