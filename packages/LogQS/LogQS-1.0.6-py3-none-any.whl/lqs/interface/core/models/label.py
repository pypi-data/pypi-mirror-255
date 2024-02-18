from typing import List, Optional

from pydantic import BaseModel

from lqs.interface.core.models.__common__ import (
    CommonModel,
    PaginationModel,
    optional_field,
)


class Label(CommonModel["Label"]):
    value: str
    note: Optional[str]


class LabelDataResponse(BaseModel):
    data: Label


class LabelListResponse(PaginationModel):
    data: List[Label]


class LabelCreateRequest(BaseModel):
    value: str
    note: Optional[str] = None


class LabelUpdateRequest(BaseModel):
    value: str = optional_field
    note: Optional[str] = optional_field
