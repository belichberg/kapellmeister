from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Query

from src.database.models import Container, Project, Channel, Token
from src.dependencies import get_api_token, generate_api_token
from src.models.manager import ContainerAPI, ProjectAPI, ChannelAPI, TokenAPI

router = APIRouter()


@router.post("/token/", response_model=TokenAPI)
def create_project(read_only: bool = True) -> TokenAPI:
    data = dict(token=generate_api_token(), read_only=read_only)
    return TokenAPI.parse_obj(Token.create(data).to_dict())


@router.post("/project/", response_model=ProjectAPI)
def create_project(data: ProjectAPI, token: TokenAPI = Depends(get_api_token)) -> ProjectAPI:
    if token.read_only:
        raise HTTPException(status.HTTP_403_FORBIDDEN)

    return ProjectAPI.parse_obj(Project.create(data.dict()).to_dict())


@router.post("/channel/", response_model=ChannelAPI)
def create_channel(data: ChannelAPI, token: TokenAPI = Depends(get_api_token)) -> ChannelAPI:
    if token.read_only:
        raise HTTPException(status.HTTP_403_FORBIDDEN)

    return ChannelAPI.parse_obj(Channel.create(data.dict()).to_dict())


@router.get("/{project_slug}/{channel_slug}/", response_model=List[ContainerAPI])
def get_containers(project_slug: str, channel_slug: str, token: any = Depends(get_api_token)) -> List[ContainerAPI]:
    project: ProjectAPI = ProjectAPI.parse_obj(Project.get(slug=project_slug).to_dict())
    channel: ChannelAPI = ChannelAPI.parse_obj(Channel.get(slug=channel_slug, project_id=project.id).to_dict())
    containers: Query = Container.get_all(project_id=project.id, channel_id=channel.id)

    return [ContainerAPI.parse_obj(item.to_dict()) for item in containers]


@router.post("/{project_slug}/{channel_slug}/", response_model=ContainerAPI)
def set_container(
    project_slug: str, channel_slug: str, data: ContainerAPI, token: any = Depends(get_api_token)
) -> ContainerAPI:
    if token.read_only:
        raise HTTPException(status.HTTP_403_FORBIDDEN)

    project: ProjectAPI = ProjectAPI.parse_obj(Project.get(slug=project_slug).to_dict())
    channel: ChannelAPI = ChannelAPI.parse_obj(Channel.get(slug=channel_slug, project_id=project.id).to_dict())

    data.project_id = project.id
    data.channel_id = channel.id

    return ContainerAPI.parse_obj(
        Container.update_or_create(data.dict(), slug=data.slug, project_id=project.id, channel_id=channel.id).to_dict()
    )


@router.delete("/{project_slug}/{channel_slug}/{container_slug}", response_model=ContainerAPI)
def delete_container(
    project_slug: str, channel_slug: str, container_slug: str, token: any = Depends(get_api_token)
) -> ContainerAPI:
    if token.read_only:
        raise HTTPException(status.HTTP_403_FORBIDDEN)

    project: ProjectAPI = ProjectAPI.parse_obj(Project.get(slug=project_slug).to_dict())
    channel: ChannelAPI = ChannelAPI.parse_obj(Channel.get(slug=channel_slug, project_id=project.id).to_dict())

    return ContainerAPI.parse_obj(
        Container.delete(slug=container_slug, project_id=project.id, channel_id=channel.id).to_dict()
    )
