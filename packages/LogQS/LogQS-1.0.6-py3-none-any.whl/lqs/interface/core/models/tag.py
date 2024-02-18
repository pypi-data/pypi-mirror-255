from typing import List, Optional
from uuid import UUID

from pydantic import BaseModel

from lqs.interface.core.models.__common__ import (
    CommonModel,
    PaginationModel,
    optional_field,
)


class Tag(CommonModel["Tag"]):
    label_id: UUID
    log_id: UUID
    topic_id: Optional[UUID]

    note: Optional[str]
    context: Optional[dict]
    start_time: Optional[int]
    end_time: Optional[int]


class TagDataResponse(BaseModel):
    data: Tag


class TagListResponse(PaginationModel):
    data: List[Tag]


class TagCreateRequest(BaseModel):
    label_id: UUID
    topic_id: Optional[UUID] = None

    note: Optional[str] = None
    context: Optional[dict] = None
    start_time: Optional[int] = None
    end_time: Optional[int] = None


class TagUpdateRequest(BaseModel):
    label_id: UUID = optional_field
    topic_id: Optional[UUID] = optional_field

    note: Optional[str] = optional_field
    context: Optional[dict] = optional_field
    start_time: Optional[int] = optional_field
    end_time: Optional[int] = optional_field
