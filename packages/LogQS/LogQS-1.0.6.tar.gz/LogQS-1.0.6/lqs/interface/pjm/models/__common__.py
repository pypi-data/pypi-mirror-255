from typing import Optional, Union
from enum import Enum
from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

optional_field = Field(default=None, json_schema_extra=lambda x: x.pop("default"))


class EmptyModel(BaseModel):
    pass


class CommonModel(BaseModel):
    id: UUID

    created_at: datetime
    updated_at: Optional[datetime]
    deleted_at: Optional[datetime]

    model_config = ConfigDict(from_attributes=True)


class PaginationModel(BaseModel):
    offset: int
    limit: int
    order: str
    sort: str
    count: int


class PatchOperation(BaseModel):
    op: str
    path: str
    value: Optional[Union[str, int, float, bool, dict, list, None]]


class ProcessState(str, Enum):
    ready = "ready"
    queued = "queued"
    processing = "processing"
    finalizing = "finalizing"
    completed = "completed"
    failed = "failed"
    cancelled = "cancelled"
    archived = "archived"


class ProcessType(str, Enum):
    ingestion = "ingestion"
    ingestion_part = "ingestion_part"
    digestion = "digestion"
    digestion_part = "digestion_part"


class JobType(str, Enum):
    ingestion = "ingestion"
    post_ingestion = "post_ingestion"
    failed_ingestion = "failed_ingestion"

    ingestion_part = "ingestion_part"
    post_ingestion_part = "post_ingestion_part"
    failed_ingestion_part = "failed_ingestion_part"

    extraction = "extraction"
    post_extraction = "post_extraction"
    failed_extraction = "failed_extraction"


class JSONFilter(BaseModel):
    var: str
    op: str
    val: Union[str, int, float, bool, list, None]
