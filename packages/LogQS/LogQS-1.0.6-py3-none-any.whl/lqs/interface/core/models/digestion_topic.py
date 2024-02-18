from typing import List, Optional
from uuid import UUID

from pydantic import BaseModel

from lqs.interface.core.models.__common__ import (
    CommonModel,
    PaginationModel,
    optional_field,
)


class DigestionTopic(CommonModel["DigestionTopic"]):
    digestion_id: UUID
    topic_id: UUID
    start_time: Optional[int]
    end_time: Optional[int]
    frequency: Optional[float]
    query_data_filter: Optional[dict]
    context_filter: Optional[dict]


class DigestionTopicDataResponse(BaseModel):
    data: DigestionTopic


class DigestionTopicListResponse(PaginationModel):
    data: List[DigestionTopic]


class DigestionTopicCreateRequest(BaseModel):
    topic_id: UUID
    start_time: Optional[int] = None
    end_time: Optional[int] = None
    frequency: Optional[float] = None
    query_data_filter: Optional[dict] = None
    context_filter: Optional[dict] = None


class DigestionTopicUpdateRequest(BaseModel):
    start_time: Optional[int] = optional_field
    end_time: Optional[int] = optional_field
    frequency: Optional[float] = optional_field
    query_data_filter: Optional[dict] = optional_field
    context_filter: Optional[dict] = optional_field
