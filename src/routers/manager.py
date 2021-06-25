from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import func
from sqlalchemy.orm import Query

from src.database.models import Container, Project, Channel, UserRole
from src.dependencies import get_api_token, get_user
from src.models.manager import ContainerAPI, ProjectAPI, ChannelAPI, TokenAPI
from src.models.user import UserAPI

router = APIRouter()


@router.get("/projects/", response_model=List[ProjectAPI])
def get_projects(user: Optional[UserAPI] = Depends(get_user)) -> List[ProjectAPI]:
    # Authentication check
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Token"},
        )

    if user.role == UserRole.super:
        # Getting all existing projects
        projects: List[ProjectAPI] = [ProjectAPI.parse_obj(project.to_dict()) for project in Project.get_all()]
    else:
        # Getting projects available to the user
        projects: List[ProjectAPI] = [ProjectAPI.parse_obj(project.to_dict()) for project in user.projects]

    for project in projects:
        project.channels = [
            ChannelAPI.parse_obj(channel.to_dict()) for channel in Channel.get_all(project_id=project.id)
        ]

    return projects


@router.post("/projects/", response_model=ProjectAPI)
def create_project(data: ProjectAPI, user: Optional[UserAPI] = Depends(get_user)) -> ProjectAPI:
    # Authentication check
    if user is None or user.role != UserRole.super:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Token"},
        )

    return ProjectAPI.parse_obj(Project.create(data.dict(exclude_defaults=True)).to_dict())


@router.delete("/projects/{project_id}/", response_model=ProjectAPI)
def delete_project(project_id: int, user: Optional[UserAPI] = Depends(get_user)) -> ProjectAPI:
    # Authentication check
    if user is None or user.role != UserRole.super:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Token"},
        )

    # deleting a project
    project: ProjectAPI = ProjectAPI.parse_obj(Project.delete(id=project_id).to_dict())
    # deleting all related channels
    project.channels = [
        ChannelAPI.parse_obj(channel.to_dict()) for channel in Channel.delete_all(project_id=project_id)
    ]
    return project


@router.post("/channels/", response_model=ChannelAPI)
def create_channel(data: ChannelAPI, user: Optional[UserAPI] = Depends(get_user)) -> ChannelAPI:
    # Authentication check
    if user is None or user.role != UserRole.super:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Token"},
        )

    return ChannelAPI.parse_obj(Channel.create(data.dict()).to_dict())


@router.delete("/channels/{channel_id}/", response_model=ChannelAPI)
def delete_channel(channel_id: int, user: Optional[UserAPI] = Depends(get_user)) -> ChannelAPI:
    # Authentication check
    if user is None or user.role != UserRole.super:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Token"},
        )

    # deleting a channel
    return ChannelAPI.parse_obj(Channel.delete(id=channel_id).to_dict())


@router.get("/{project_slug}/{channel_slug}/", response_model=List[ContainerAPI])
def get_containers(
    project_slug: str,
    channel_slug: str,
    user: Optional[UserAPI] = Depends(get_user),
    token: Optional[TokenAPI] = Depends(get_api_token),
) -> List[ContainerAPI]:
    # Authentication check
    if user is None and token is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Token"},
        )

    project: ProjectAPI = ProjectAPI.parse_obj(Project.get(slug=project_slug).to_dict())
    channel: ChannelAPI = ChannelAPI.parse_obj(Channel.get(slug=channel_slug, project_id=project.id).to_dict())

    if token and token.project_id and token.project_id != project.id:
        raise HTTPException(status.HTTP_403_FORBIDDEN)

    containers: Query = Container.get_all(project_id=project.id, channel_id=channel.id)
    return [ContainerAPI.parse_obj(item.to_dict()) for item in containers]


@router.post("/{project_slug}/{channel_slug}/", response_model=ContainerAPI)
def set_container(
    project_slug: str,
    channel_slug: str,
    data: ContainerAPI,
    user: Optional[UserAPI] = Depends(get_user),
    token: Optional[TokenAPI] = Depends(get_api_token),
) -> ContainerAPI:

    project: ProjectAPI = ProjectAPI.parse_obj(Project.get(slug=project_slug).to_dict())
    channel: ChannelAPI = ChannelAPI.parse_obj(Channel.get(slug=channel_slug, project_id=project.id).to_dict())

    # Authentication check
    if user is None and token is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Token"},
        )

    # Checking access rights
    elif (
        token
        and (token.read_only or (token.project_id and token.project_id != project.id))
        or (user and user.role != UserRole.super)
    ):
        raise HTTPException(status.HTTP_403_FORBIDDEN)

    data.project_id = project.id
    data.channel_id = channel.id
    data.updated_time = func.now()

    return ContainerAPI.parse_obj(
        Container.update_or_create(data.dict(), slug=data.slug, project_id=project.id, channel_id=channel.id).to_dict()
    )


@router.delete("/{project_slug}/{channel_slug}/{container_slug}/", response_model=ContainerAPI)
def delete_container(
    project_slug: str, channel_slug: str, container_slug: str, user: Optional[UserAPI] = Depends(get_user)
) -> ContainerAPI:
    # Authentication check
    if user is None or user.role != UserRole.super:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Token"},
        )

    project: ProjectAPI = ProjectAPI.parse_obj(Project.get(slug=project_slug).to_dict())
    channel: ChannelAPI = ChannelAPI.parse_obj(Channel.get(slug=channel_slug, project_id=project.id).to_dict())

    return ContainerAPI.parse_obj(
        Container.delete(slug=container_slug, project_id=project.id, channel_id=channel.id).to_dict()
    )
