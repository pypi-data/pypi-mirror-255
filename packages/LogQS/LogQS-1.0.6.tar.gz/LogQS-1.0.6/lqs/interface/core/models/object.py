from typing import List, Optional
from datetime import datetime
from enum import Enum

from pydantic import BaseModel

from lqs.interface.base.models.__common__ import (
    ResourceModel,
)


class UploadState(str, Enum):
    complete = "complete"
    processing = "processing"
    aborted = "aborted"


class Object(ResourceModel["Object"]):
    _repr_fields = ("key",)

    key: str
    etag: Optional[str] = None
    size: Optional[int] = None
    last_modified: Optional[datetime] = None
    presigned_url: Optional[str] = None
    upload_state: UploadState


class ObjectDataResponse(BaseModel):
    data: Object


class ObjectListResponse(BaseModel):
    data: List[Object]
    is_truncated: Optional[bool] = None
    key_count: Optional[int] = None
    max_keys: int

    continuation_token: Optional[str] = None
    next_continuation_token: Optional[str] = None
    prefix: Optional[str] = None
    start_after: Optional[str] = None
    delimiter: Optional[str] = None
    common_prefixes: Optional[List[str]] = None


class ObjectCreateRequest(BaseModel):
    key: str
    content_type: Optional[str] = None


class ObjectUpdateRequest(BaseModel):
    upload_state: UploadState


# Object Parts


class ObjectPart(BaseModel):
    part_number: int
    etag: str
    size: int
    last_modified: Optional[datetime] = None
    presigned_url: Optional[str] = None


class ObjectPartDataResponse(BaseModel):
    data: ObjectPart


class ObjectPartListResponse(BaseModel):
    data: List[ObjectPart]
    part_number_marker: Optional[int] = None
    next_part_number_marker: Optional[int] = None
    max_parts: Optional[int] = None
    is_truncated: Optional[bool] = None


class ObjectPartCreateRequest(BaseModel):
    part_number: Optional[int] = None
    size: int
