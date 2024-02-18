from typing import List, Optional

from pydantic import BaseModel

from lqs.interface.dsm.models.__common__ import (
    CommonModel,
    PaginationModel,
    optional_field,
)


class Configuration(CommonModel):
    value: dict
    name: Optional[str]
    note: Optional[str]
    default: bool
    disabled: bool


class ConfigurationDataResponse(BaseModel):
    data: Configuration


class ConfigurationListResponse(PaginationModel):
    data: List[Configuration]


class ConfigurationCreateRequest(BaseModel):
    value: dict
    name: Optional[str] = None
    note: Optional[str] = None
    default: bool = False
    disabled: bool = False


class ConfigurationUpdateRequest(BaseModel):
    value: dict = optional_field
    name: Optional[str] = optional_field
    note: Optional[str] = optional_field
    default: bool = optional_field
    disabled: bool = optional_field
