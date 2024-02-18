from typing import List, Optional
from uuid import UUID

from pydantic import BaseModel

from lqs.interface.base.models.__common__ import (
    CommonModel,
    PaginationModel,
    optional_field,
)


class APIKey(CommonModel["APIKey"]):
    name: str
    user_id: UUID
    disabled: bool
    secret: Optional[str] = optional_field  # TODO: figure out what to do here


class APIKeyDataResponse(BaseModel):
    data: APIKey


class APIKeyListResponse(PaginationModel):
    data: List[APIKey]


class APIKeyCreateRequest(BaseModel):
    name: str
    user_id: UUID
    disabled: bool = False


class APIKeyUpdateRequest(BaseModel):
    name: str = optional_field
    disabled: bool = optional_field
