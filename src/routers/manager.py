import json
from typing import List, Optional, Dict

import yaml
from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Query

from src.database.models import Container, Project, Channel, UserRole
from src.dependencies import get_api_token, get_user, time_utc_now
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


@router.get("/channels/", response_model=List[ChannelAPI])
def get_channels(user: Optional[UserAPI] = Depends(get_user)) -> List[ChannelAPI]:
    # Authentication check
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Token"},
        )

    # Getting all existing projects
    channels: List[ChannelAPI] = [ChannelAPI.parse_obj(channel.to_dict()) for channel in Channel.get_all()]

    if user.role != UserRole.super:
        # Filter projects available to the user
        channels: List[ChannelAPI] = [c for c in channels if Project.get(id=c.project_id) in user.projects]

    return channels


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


@router.patch("/container/", response_model=ContainerAPI)
async def edit_container(container: ContainerAPI, user: Optional[UserAPI] = Depends(get_user)) -> ContainerAPI:
    # container: ContainerAPI = ContainerAPI.parse_obj(yaml.safe_load(await request.body()))

    project: ProjectAPI = ProjectAPI.parse_obj(Project.get(id=container.project_id).to_dict())
    channel: ChannelAPI = ChannelAPI.parse_obj(Channel.get(id=container.channel_id, project_id=project.id).to_dict())

    # Authentication check
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Token"},
        )
    # Checking access rights
    elif user.role != UserRole.super:
        raise HTTPException(status.HTTP_403_FORBIDDEN)

    container.project_id = project.id
    container.channel_id = channel.id
    container.updated_time = time_utc_now()

    # prepare data
    data: Dict = {
        **container.dict(exclude={"auth", "slug", "project_id", "channel_id"}),
        **dict(
            auth=json.dumps(container.auth),
            slug=container.slug,
            project_id=project.id,
            channel_id=channel.id,
        ),
    }

    # create of get container record
    record = Container.update(data, id=container.id)

    # update or create container and then return container api
    return ContainerAPI.parse_obj(record.to_dict())


@router.get("/{project_slug}/{channel_slug}/", response_model=List[ContainerAPI])
async def get_containers(
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
async def set_container(
        project_slug: str,
        channel_slug: str,
        request: Request,
        user: Optional[UserAPI] = Depends(get_user),
        token: Optional[TokenAPI] = Depends(get_api_token),
) -> ContainerAPI:
    container: ContainerAPI = ContainerAPI.parse_obj(yaml.safe_load(await request.body()))

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
            and (not token.write or (token.project_id and token.project_id != project.id))
            or (user and user.role != UserRole.super)
    ):
        raise HTTPException(status.HTTP_403_FORBIDDEN)

    container.project_id = project.id
    container.channel_id = channel.id
    container.updated_time = time_utc_now()

    # prepare data
    data: Dict = {
        **container.dict(exclude={"id", "auth", "slug", "project_id", "channel_id"}),
        **dict(
            auth=json.dumps(container.auth),
            slug=container.slug,
            project_id=project.id,
            channel_id=channel.id,
        ),
    }

    # create of get container record
    record = Container.update_or_create(data, slug=container.slug, project_id=project.id, channel_id=channel.id)

    # update or create container and then return container api
    return ContainerAPI.parse_obj(record.to_dict())


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


@router.get("/containers/", response_model=List[ContainerAPI])
async def get_all_containers(
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

    # Getting all existing projects
    containers: List[ContainerAPI] = [ContainerAPI.parse_obj(item.to_dict()) for item in Container.get_all()]

    if user.role != UserRole.super:
        # Filter projects available to the user
        containers: List[ContainerAPI] = [c for c in containers if Project.get(id=c.project_id) in user.projects]
    return containers
