from typing import List

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session, Query

from src.database.models import Container, Project, Channel
from src.helpers import get_db
from src.models.manager import ContainerAPI, ProjectAPI, ChannelAPI

router = APIRouter()


@router.post("/project/", response_model=ProjectAPI)
def create_project(data: ProjectAPI, db: Session = Depends(get_db)) -> ProjectAPI:
    return ProjectAPI.parse_obj(Project.create(db, data.dict()).to_dict())


@router.post("/channel/", response_model=ChannelAPI)
def create_channel(data: ChannelAPI, db: Session = Depends(get_db)) -> ChannelAPI:
    return ChannelAPI.parse_obj(Channel.create(db, data.dict()).to_dict())


@router.get("/{project_slug}/{channel_slug}/", response_model=List[ContainerAPI])
def get_containers(project_slug: str, channel_slug: str, db: Session = Depends(get_db)) -> List[ContainerAPI]:
    project: ProjectAPI = ProjectAPI.parse_obj(Project.get(db, project_slug).first().to_dict())
    channel: ChannelAPI = ChannelAPI.parse_obj(
        Channel.get(db, channel_slug).filter_by(project_id=project.id).first().to_dict()
    )
    containers: Query = db.query(Container).filter_by(project_id=project.id).filter_by(channel_id=channel.id)

    return [ContainerAPI.parse_obj(item.to_dict()) for item in containers]


@router.post("/{project_slug}/{channel_slug}/", response_model=ContainerAPI)
def set_container(
    project_slug: str, channel_slug: str, data: ContainerAPI, db: Session = Depends(get_db)
) -> ContainerAPI:
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
    project_slug: str, channel_slug: str, container_slug: str, db: Session = Depends(get_db)
) -> ContainerAPI:
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
