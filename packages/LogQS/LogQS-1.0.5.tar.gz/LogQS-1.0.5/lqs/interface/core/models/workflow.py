from typing import List, Optional

from pydantic import BaseModel

from lqs.interface.core.models.__common__ import (
    CommonModel,
    PaginationModel,
    optional_field,
)


class Workflow(CommonModel["Workflow"]):
    name: str
    note: Optional[str]
    context: Optional[dict]
    managed: bool
    default: bool
    disabled: bool
    context_schema: Optional[dict]


class WorkflowDataResponse(BaseModel):
    data: Workflow


class WorkflowListResponse(PaginationModel):
    data: List[Workflow]


class WorkflowCreateRequest(BaseModel):
    name: str
    note: Optional[str] = None
    context: Optional[dict] = None
    default: bool = False
    disabled: bool = False
    managed: bool = False
    context_schema: Optional[dict] = None


class WorkflowUpdateRequest(BaseModel):
    name: str = optional_field
    note: Optional[str] = optional_field
    context: Optional[dict] = optional_field
    default: bool = optional_field
    disabled: bool = optional_field
    context_schema: Optional[dict] = optional_field
