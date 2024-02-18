from typing import List, Optional
from uuid import UUID

from pydantic import BaseModel, Field

from lqs.interface.core.models.__common__ import (
    TimeSeriesModel,
    PaginationModel,
    LockModel,
    LockCreateRequest,
    LockUpdateRequest,
    optional_field,
)


class Record(TimeSeriesModel["Record"], LockModel):
    _repr_fields = ("timestamp", "topic_id", "log_id")

    log_id: UUID = Field(
        ..., description="The ID of the log to which this record's topic belongs."
    )
    topic_id: UUID = Field(
        ..., description="The ID of the topic to which this record belongs."
    )
    timestamp: int = Field(
        ..., description="The timestamp, in nanoseconds, of the record."
    )

    ingestion_id: Optional[UUID] = Field(
        ..., description="The ID of the ingestion which created this record, if any."
    )
    data_offset: Optional[int] = Field(
        ...,
        description="The offset, in bytes, of the record's message data in the log object.",
    )
    data_length: Optional[int] = Field(
        ...,
        description="The length, in bytes, of the record's message data in the log object.",
    )
    chunk_compression: Optional[str] = Field(
        ...,
        description="The compression algorithm used to compress the record's message data in the log object, if any.",
    )
    chunk_offset: Optional[int] = Field(
        ...,
        description="The offset, in bytes, of the record's message data in the log object's uncompressed data relative to the start of the uncompressed chunk, if compressed.",
    )
    chunk_length: Optional[int] = Field(
        ...,
        description="The length, in bytes, of the record's message data in the log object's uncompressed data, if compressed.",
    )
    source: Optional[str] = Field(
        ...,
        description="A relative path to the record's log object relative to the record's ingestion object, if any.",
    )
    error: Optional[dict] = Field(
        ...,
        description="The JSON payload of an error that occurred during record processing.",
    )

    query_data: Optional[dict] = Field(
        ...,
        description="A JSON data representation of the record's message data which is queryable.",
    )
    auxiliary_data: Optional[dict] = Field(
        None,
        description="A JSON data representation of the record's auxiliary data which can be used for functional purposes.",
    )
    raw_data: Optional[str] = Field(
        None,
        description="A string representation of the record's message data, presented as-is. This data will be base 64 encoded if needed.",
    )
    context: Optional[dict] = Field(..., description="A JSON context for the record.")
    note: Optional[str] = Field(
        ..., description="A general note about the record for reference."
    )

    def get_auxiliary_data(self):
        if self.auxiliary_data is None:
            record = self.fetch(
                self.timestamp, self.topic_id, include_auxiliary_data=True
            )
            self.auxiliary_data = record.auxiliary_data
        return self.auxiliary_data

    def load_auxiliary_data_image(self):
        return self.app.utils.load_auxiliary_data_image(self)


class RecordDataResponse(BaseModel):
    data: Record


class RecordListResponse(PaginationModel):
    data: List[Record]


class RecordCreateRequest(LockCreateRequest):
    timestamp: int
    note: Optional[str] = None
    context: Optional[dict] = None
    query_data: Optional[dict] = None
    auxiliary_data: Optional[dict] = None

    data_offset: Optional[int] = None
    data_length: Optional[int] = None
    chunk_compression: Optional[str] = None
    chunk_offset: Optional[int] = None
    chunk_length: Optional[int] = None
    source: Optional[str] = None


class RecordUpdateRequest(LockUpdateRequest):
    error: Optional[dict] = optional_field
    query_data: Optional[dict] = optional_field
    auxiliary_data: Optional[dict] = optional_field
    context: Optional[dict] = optional_field
    note: Optional[str] = optional_field
