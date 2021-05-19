from typing import Optional

from pydantic import constr, BaseModel


class ContainerAPI(BaseModel):
    # id: int
    slug: constr(max_length=64)
    auth: Optional[constr(max_length=2000)]
    hash: constr(max_length=255)
    parameters: constr(max_length=2000)
    project_id: Optional[int]
    channel_id: Optional[int]


class ProjectAPI(BaseModel):
    id: Optional[int]
    name: constr(max_length=64)
    slug: constr(max_length=64)
    description: Optional[constr(max_length=512)]


class ChannelAPI(BaseModel):
    id: Optional[int]
    name: constr(max_length=64)
    slug: constr(max_length=64)
    description: Optional[constr(max_length=512)]
    project_id: int
