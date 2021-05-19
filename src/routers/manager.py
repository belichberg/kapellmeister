from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from src.models.manager import ContainerAPI
from src.database.models import Container
from src.helpers import get_db

router = APIRouter()


# @router.get("/{project_slug}/{channel_slug}/", response_model=ContainerAPI)
# project_slug: str, channel_slug: str,
# @router.get("/", response_model=ContainerAPI)
# async def get_container(db: Session = Depends(get_db)) -> ContainerAPI:
#     return db.query(Container).all()


@router.get("/{project_slug}/{channel_slug}/", response_model=ContainerAPI)
async def get_container(project_slug: str, channel_slug: str, db: Session = Depends(get_db)) -> ContainerAPI:
    return db.query(Container).first().__dict__


@router.post("/{project_slug}/{channel_slug}/", response_model=ContainerAPI)
async def set_container(project_slug: str, channel_slug: str, item: ContainerAPI, db: Session = Depends(get_db)) -> ContainerAPI:
    container = Container(**item.dict())
    db.add(container)
    db.commit()
    db.refresh(container)
    return ContainerAPI.parse_obj(container.__dict__)

# async def get_post_list():
#     post_list = await database.fetch_all(query=posts.select().where(posts.c.parent_id.is_(None)))
#     return [dict(result) for result in post_list]

# def get_post_list(db: Session):
#     return db.query(Post).all()
#
#
# def create_post(db: Session, item: PostCreate):
#     post = Post(**item.dict())
#     db.add(post)
#     db.commit()
#     db.refresh(post)
#     return post
