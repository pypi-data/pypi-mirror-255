from typing import List, Optional

from pydantic import BaseModel

from lqs.interface.base.models.__common__ import (
    CommonModel,
    PaginationModel,
    optional_field,
)


class ObjectStore(CommonModel["ObjectStore"]):
    bucket_name: str
    access_key_id: Optional[str]
    region_name: Optional[str]
    endpoint_url: Optional[str]
    note: Optional[str]
    context: Optional[dict]
    disabled: bool


class ObjectStoreDataResponse(BaseModel):
    data: ObjectStore


class ObjectStoreListResponse(PaginationModel):
    data: List[ObjectStore]


class ObjectStoreCreateRequest(BaseModel):
    bucket_name: str
    access_key_id: Optional[str] = None
    secret_access_key: Optional[str] = None
    region_name: Optional[str] = None
    endpoint_url: Optional[str] = None
    note: Optional[str] = None
    context: Optional[dict] = None
    disabled: bool = False


class ObjectStoreUpdateRequest(BaseModel):
    bucket_name: str = optional_field
    access_key_id: Optional[str] = optional_field
    secret_access_key: Optional[str] = optional_field
    region_name: Optional[str] = optional_field
    endpoint_url: Optional[str] = optional_field
    note: Optional[str] = optional_field
    context: Optional[dict] = optional_field
    disabled: bool = optional_field
