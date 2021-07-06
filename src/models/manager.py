from datetime import datetime
from typing import Optional, Dict, Any, List, Union

from pydantic import constr, BaseModel


class ContainerAPI(BaseModel):
    slug: constr(max_length=64)
    auth: Union[Dict[str, Any], str]
    digest: constr(max_length=255)
    parameters: Dict[str, Any]
    updated_time: Optional[datetime]
    channel_id: Optional[int]
    project_id: Optional[int]


class ChannelAPI(BaseModel):
    id: Optional[int]
    name: constr(max_length=64)
    slug: constr(max_length=64)
    description: Optional[constr(max_length=512)]
    project_id: int


class ProjectAPI(BaseModel):
    id: Optional[int]
    name: constr(max_length=64)
    slug: constr(max_length=64)
    description: Optional[constr(max_length=512)] = ""
    channels: Optional[List[ChannelAPI]] = []


class TokenAPI(BaseModel):
    id: Optional[int]
    token: str
    # read_only: bool
    project_id: Optional[int]
    write: bool


class TokenRequestAPI(BaseModel):
    token: Optional[str]
