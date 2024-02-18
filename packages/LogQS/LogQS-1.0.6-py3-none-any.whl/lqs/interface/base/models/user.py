from typing import List, Optional
from uuid import UUID

from pydantic import BaseModel

from lqs.interface.base.models.__common__ import (
    CommonModel,
    PaginationModel,
    optional_field,
)


class User(CommonModel["User"]):
    _repr_fields = ("id", "username")

    username: str
    role_id: Optional[UUID]
    admin: bool
    disabled: bool
    managed: bool
    external_id: Optional[str] = None


class UserDataResponse(BaseModel):
    data: User


class MeDataResponse(BaseModel):
    data: Optional[User]


class UserListResponse(PaginationModel):
    data: List[User]


class UserCreateRequest(BaseModel):
    username: str
    role_id: Optional[UUID] = None
    admin: bool = False
    disabled: bool = False
    managed: bool = False
    external_id: Optional[str] = None
    password: Optional[str] = None  # note: this is virtual


class UserUpdateRequest(BaseModel):
    username: str = optional_field
    role_id: Optional[UUID] = optional_field
    admin: bool = optional_field
    disabled: bool = optional_field
    external_id: Optional[str] = optional_field
    password: Optional[str] = optional_field  # note: this is virtual
