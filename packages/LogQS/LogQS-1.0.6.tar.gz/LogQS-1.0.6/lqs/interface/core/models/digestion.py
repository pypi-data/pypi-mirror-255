from typing import List, Optional
from uuid import UUID

from pydantic import BaseModel, Field

from lqs.interface.core.models.__common__ import (
    PaginationModel,
    ProcessModel,
    ProcessCreateRequest,
    ProcessUpdateRequest,
    optional_field_alt as optional_field,
)


class Digestion(ProcessModel["Digestion"]):
    log_id: UUID = Field(
        ..., description="The ID of the log to which this digestion belongs."
    )
    group_id: Optional[UUID] = Field(
        None, description="The ID of the group to which this digestion belongs."
    )
    name: Optional[str] = Field(
        None, description="The name of the digestion (not unique)."
    )
    note: Optional[str] = Field(
        None, description="A general note about the digestion for reference."
    )
    context: Optional[dict] = Field(
        None, description="A JSON context for the digestion."
    )


class DigestionDataResponse(BaseModel):
    data: Digestion


class DigestionListResponse(PaginationModel):
    data: List[Digestion]


class DigestionCreateRequest(ProcessCreateRequest):
    log_id: UUID = Field(
        ..., description="The ID of the log to which the digestion should be added."
    )
    name: Optional[str] = Field(
        None, description="The name of the digestion (not unique)."
    )
    note: Optional[str] = Field(
        None, description="A general note about the digestion for reference."
    )
    context: Optional[dict] = Field(
        None, description="A JSON context for the digestion."
    )


class DigestionUpdateRequest(ProcessUpdateRequest):
    name: Optional[str] = optional_field("The name of the digestion (not unique).")
    note: Optional[str] = optional_field(
        "A general note about the digestion for reference."
    )
    context: Optional[dict] = optional_field("A JSON context for the digestion.")
