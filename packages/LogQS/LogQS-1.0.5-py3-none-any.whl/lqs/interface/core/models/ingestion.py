from typing import List, Optional
from uuid import UUID

from pydantic import BaseModel, Field

from lqs.interface.core.models.__common__ import (
    PaginationModel,
    ProcessModel,
    ProcessCreateRequest,
    ProcessUpdateRequest,
    optional_field,
)


class Ingestion(ProcessModel["Ingestion"]):
    log_id: UUID = Field(
        ..., description="The ID of the log to which this ingestion belongs."
    )

    object_store_id: Optional[UUID] = Field(
        ...,
        description="If the ingestion object is stored in an object store, the ID of the object store.",
    )
    object_key: Optional[str] = Field(
        ..., description="The key of the ingestion object."
    )

    name: Optional[str] = Field(
        ..., description="The name of the ingestion (not unique)."
    )
    note: Optional[str] = Field(
        ..., description="A general note about the ingestion for reference."
    )
    context: Optional[dict] = Field(
        ..., description="A JSON context for the ingestion."
    )

    group_id: Optional[UUID] = None


class IngestionDataResponse(BaseModel):
    data: Ingestion


class IngestionListResponse(PaginationModel):
    data: List[Ingestion]


class IngestionCreateRequest(ProcessCreateRequest):
    log_id: UUID
    name: Optional[str] = None
    object_store_id: Optional[UUID] = None
    object_key: Optional[str] = None
    note: Optional[str] = None
    context: Optional[dict] = None


class IngestionUpdateRequest(ProcessUpdateRequest):
    name: Optional[str] = optional_field
    object_store_id: Optional[UUID] = optional_field
    object_key: Optional[str] = optional_field
    note: Optional[str] = optional_field
    context: Optional[dict] = optional_field
