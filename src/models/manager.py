from typing import Optional, Dict, Any

from pydantic import constr, BaseModel


class ContainerAPI(BaseModel):
    slug: constr(max_length=64)
    auth: Optional[constr(max_length=2000)]
    digest: constr(max_length=255)
    parameters: Dict[str, Any]
    channel_id: Optional[int]
    project_id: Optional[int]


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


class TokenAPI(BaseModel):
    token: str
    read_only: bool
