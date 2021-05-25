from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session, Query

from src.database.models import Container, Project, Channel, Token
from src.dependencies import get_api_token
from src.helpers import get_db, generate_token
from src.models.manager import ContainerAPI, ProjectAPI, ChannelAPI, TokenAPI

router = APIRouter()


@router.post("/token/", response_model=TokenAPI)
def create_project(read_only: bool = True, db: Session = Depends(get_db)) -> TokenAPI:
    data = dict(token=generate_token(), read_only=read_only)
    return TokenAPI.parse_obj(Token.create(db, data).to_dict())


@router.post("/project/", response_model=ProjectAPI)
def create_project(data: ProjectAPI, db: Session = Depends(get_db), token: TokenAPI = Depends(get_api_token)) -> ProjectAPI:
    if token.read_only:
        raise HTTPException(status.HTTP_403_FORBIDDEN)

    return ProjectAPI.parse_obj(Project.create(db, data.dict()).to_dict())


@router.post("/channel/", response_model=ChannelAPI)
def create_channel(data: ChannelAPI, db: Session = Depends(get_db), token: TokenAPI = Depends(get_api_token)) -> ChannelAPI:
    if token.read_only:
        raise HTTPException(status.HTTP_403_FORBIDDEN)

    return ChannelAPI.parse_obj(Channel.create(db, data.dict()).to_dict())


@router.get("/{project_slug}/{channel_slug}/", response_model=List[ContainerAPI])
def get_containers(project_slug: str, channel_slug: str, db: Session = Depends(get_db), token: any = Depends(get_api_token)) -> List[ContainerAPI]:
    project: ProjectAPI = ProjectAPI.parse_obj(Project.get(db, project_slug).first().to_dict())
    channel: ChannelAPI = ChannelAPI.parse_obj(
        Channel.get(db, channel_slug).filter_by(project_id=project.id).first().to_dict()
    )
    containers: Query = db.query(Container).filter_by(project_id=project.id).filter_by(channel_id=channel.id)

    return [ContainerAPI.parse_obj(item.to_dict()) for item in containers]


@router.post("/{project_slug}/{channel_slug}/", response_model=ContainerAPI)
def set_container(
    project_slug: str, channel_slug: str, data: ContainerAPI, db: Session = Depends(get_db), token: any = Depends(get_api_token)
) -> ContainerAPI:
    if token.read_only:
        raise HTTPException(status.HTTP_403_FORBIDDEN)

    project: ProjectAPI = ProjectAPI.parse_obj(Project.get(db, project_slug).first().to_dict())
    channel: ChannelAPI = ChannelAPI.parse_obj(
        Channel.get(db, channel_slug).filter_by(project_id=project.id).first().to_dict()
    )

    data.project_id = project.id
    data.channel_id = channel.id
    container: Container = Container.update_or_create(db, data)

    return container.to_dict()


@router.delete("/{project_slug}/{channel_slug}/{container_slug}", response_model=ContainerAPI)
def delete_container(
    project_slug: str, channel_slug: str, container_slug: str, db: Session = Depends(get_db), token: any = Depends(get_api_token)
) -> ContainerAPI:
    if token.read_only:
        raise HTTPException(status.HTTP_403_FORBIDDEN)

    project: ProjectAPI = ProjectAPI.parse_obj(Project.get(db, project_slug).first().to_dict())
    channel: ChannelAPI = ChannelAPI.parse_obj(
        Channel.get(db, channel_slug).filter_by(project_id=project.id).first().to_dict()
    )
    container: Container = (
        Container.get(db, container_slug).filter_by(project_id=project.id).filter_by(channel_id=channel.id).first()
    )

    db.delete(container)
    db.commit()

    return container.to_dict()
