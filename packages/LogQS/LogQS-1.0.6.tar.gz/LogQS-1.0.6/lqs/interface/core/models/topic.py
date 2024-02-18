from typing import List, Optional
from uuid import UUID

from pydantic import BaseModel, Field

from lqs.interface.core.models.__common__ import (
    CommonModel,
    LockModel,
    LockCreateRequest,
    LockUpdateRequest,
    PaginationModel,
    TypeEncoding,
    optional_field,
)
from lqs.interface.core.models import Record


class Topic(CommonModel["Topic"], LockModel):
    log_id: UUID = Field(
        ..., description="The ID of the log to which this topic belongs."
    )
    group_id: Optional[UUID] = Field(
        None, description="The ID of the group to which this topic belongs."
    )

    name: str = Field(..., description="The name of the topic (unique per log).")
    note: Optional[str] = Field(..., description="A general note about the topic.")
    context: Optional[dict] = Field(..., description="A JSON context for the topic.")

    associated_topic_id: Optional[UUID] = Field(
        ..., description="The ID of an associated topic (if any) for reference."
    )
    start_time: Optional[int] = Field(
        ..., description="The timestamp of the first record of the topic."
    )
    end_time: Optional[int] = Field(
        ..., description="The timestamp of the last record of the topic."
    )

    record_size: int = Field(
        ..., description="The total size of all records in the topic in bytes."
    )
    record_count: int = Field(
        ..., description="The total number of records in the topic."
    )
    object_size: int = Field(
        ..., description="The total size of all objects in the topic in bytes."
    )
    object_count: int = Field(
        ..., description="The total number of objects in the topic."
    )

    strict: bool = Field(
        ..., description="Whether the topic's schema should be strictly enforced."
    )
    type_name: Optional[str] = Field(
        ...,
        description="The name of the message type which the topic's records should conform to.",
    )
    type_encoding: Optional[TypeEncoding] = Field(
        ..., description="The encoding of the message data of the topic's records."
    )
    type_data: Optional[str] = Field(
        ...,
        description="The definition of the message type used to (de)serialize the topic's records.",
    )
    type_schema: Optional[dict] = Field(
        ...,
        description="A JSON schema describing the record data of the topic's records.",
    )

    def list_records(self, **kwargs) -> List["Record"]:
        return self.app.list.record(topic_id=self.id, **kwargs).data


Topic.model_rebuild()


class TopicDataResponse(BaseModel):
    data: Topic


class TopicListResponse(PaginationModel):
    data: List[Topic]


class TopicCreateRequest(LockCreateRequest):
    log_id: UUID
    name: str
    note: Optional[str] = None
    context: Optional[dict] = None
    associated_topic_id: Optional[UUID] = None

    strict: bool = False
    type_name: Optional[str] = None
    type_encoding: Optional[TypeEncoding] = None
    type_data: Optional[str] = None
    type_schema: Optional[dict] = None


class TopicUpdateRequest(LockUpdateRequest):
    name: str = optional_field
    note: Optional[str] = optional_field
    context: Optional[dict] = optional_field
    associated_topic_id: Optional[UUID] = optional_field

    strict: bool = optional_field
    type_name: Optional[str] = optional_field
    type_encoding: Optional[TypeEncoding] = optional_field
    type_data: Optional[str] = optional_field
    type_schema: Optional[dict] = optional_field
