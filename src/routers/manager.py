from typing import List

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from src.database.models import Container, Project, Channel
from src.helpers import get_db
from src.models.manager import ContainerAPI, ProjectAPI, ChannelAPI

router = APIRouter()


@router.get("/", response_model=List[ContainerAPI])
def get_all_containers(db: Session = Depends(get_db)) -> List[ContainerAPI]:
    return [ContainerAPI.parse_obj(item.to_dict()) for item in db.query(Container).all()]


@router.post("/project/", response_model=ProjectAPI)
def create_project(data: ProjectAPI, db: Session = Depends(get_db)) -> ProjectAPI:
    return ProjectAPI.parse_obj(Project.create(data.dict(), db).to_dict())


@router.post("/channel/", response_model=ChannelAPI)
def create_channel(data: ChannelAPI, db: Session = Depends(get_db)) -> ChannelAPI:
    return ChannelAPI.parse_obj(Channel.create(data.dict(), db).to_dict())


@router.get("/{project_slug}/{channel_slug}/", response_model=List[ContainerAPI])
def get_container(project_slug: str, channel_slug: str, db: Session = Depends(get_db)) -> List[ContainerAPI]:
    project: ProjectAPI = ProjectAPI.parse_obj(Project.get(project_slug, db).first().to_dict())
    channel: ChannelAPI = ChannelAPI.parse_obj(Channel.get(channel_slug, db)
                                               .filter_by(project_id=project.id)
                                               .first().to_dict())
    containers = db.query(Container).filter_by(project_id=project.id).filter_by(channel_id=channel.id)

    return [ContainerAPI.parse_obj(item.to_dict()) for item in containers]


@router.post("/{project_slug}/{channel_slug}/", response_model=ContainerAPI)
def set_container(project_slug: str, channel_slug: str, data: ContainerAPI, db: Session = Depends(get_db)) -> ContainerAPI:
    project: ProjectAPI = ProjectAPI.parse_obj(Project.get(project_slug, db).first().to_dict())
    channel: ChannelAPI = ChannelAPI.parse_obj(Channel.get(channel_slug, db).filter_by(project_id=project.id).first().to_dict())

    data.project_id = project.id
    data.channel_id = channel.id
    container = Container.create(data.dict(), db)

    # TODO: change the incoming model and redo the saving of data
    return container.to_dict()
