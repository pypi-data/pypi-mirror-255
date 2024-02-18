from enum import Enum
from uuid import UUID
from typing import Optional
from datetime import datetime

from pydantic import BaseModel, Field

from lqs.interface.base.models.__common__ import (  # noqa: F401
    ResourceModel,
    CommonModel,
    T,
    TimeSeriesModel,
    PaginationModel,
    PatchOperation,
    JSONFilter,
    optional_field,
    optional_field_alt,
)


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


class TypeEncoding(str, Enum):
    ros1 = "ros1"
    rbuf = "rbuf"
    json = "json"


class LockModel(BaseModel):
    locked: bool = Field(
        False,
        description="Whether the process is locked (i.e. cannot be modified).",
    )
    locked_by: Optional[UUID] = Field(
        None, description="The ID of the user who locked the resource."
    )
    locked_at: Optional[datetime] = Field(
        None, description="The time at which the resource was locked."
    )
    lock_token: Optional[str] = Field(
        None, description="The token used to lock the resource."
    )


class LockCreateRequest(BaseModel):
    locked: bool = False


class LockUpdateRequest(BaseModel):
    locked: bool = optional_field


class ProcessModel(CommonModel[T], LockModel):
    # These fields are used by the user to control the process.
    workflow_id: Optional[UUID] = Field(
        None,
        description="The ID of the workflow to be executed during state transitions.",
    )
    workflow_context: Optional[dict] = Field(
        None,
        description="The context to be passed to the workflow during state transitions.",
    )
    state: ProcessState = Field(
        ProcessState.ready, description="The current state of the process."
    )

    # These fields should not be modified by a user and only by the process.
    progress: Optional[float] = Field(
        None,
        description="The progress of the process for the current state (a float in [0,1]).",
    )
    transitioned_at: Optional[datetime] = Field(
        None,
        description="The time at which the process transitioned to the current state.",
    )
    error: Optional[dict] = Field(
        None,
        description="The JSON payload of an error that occurred during the process.",
    )


class ProcessCreateRequest(LockCreateRequest):
    workflow_id: Optional[UUID] = None
    workflow_context: Optional[dict] = None
    state: ProcessState = ProcessState.ready


class ProcessUpdateRequest(LockUpdateRequest):
    workflow_id: Optional[UUID] = optional_field
    workflow_context: Optional[dict] = optional_field
    state: ProcessState = optional_field
    progress: Optional[float] = optional_field
    error: Optional[dict] = optional_field
