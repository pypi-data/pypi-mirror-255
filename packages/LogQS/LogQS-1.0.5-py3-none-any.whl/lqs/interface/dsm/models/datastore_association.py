from typing import List, Optional
from uuid import UUID

from pydantic import BaseModel

from lqs.interface.dsm.models.__common__ import (
    CommonModel,
    PaginationModel,
    optional_field,
)


class DataStoreAssociation(CommonModel):
    user_id: UUID
    datastore_id: UUID
    manager: bool
    disabled: bool

    datastore_user_id: UUID
    datastore_username: Optional[str]
    datastore_role_id: Optional[UUID]
    datastore_admin: bool
    datastore_disabled: bool


class DataStoreAssociationDataResponse(BaseModel):
    data: DataStoreAssociation


class DataStoreAssociationListResponse(PaginationModel):
    data: List[DataStoreAssociation]


class DataStoreAssociationCreateRequest(BaseModel):
    user_id: UUID
    datastore_id: UUID
    manager: bool = False
    disabled: bool = False

    datastore_user_id: Optional[UUID] = None
    datastore_username: Optional[str] = None
    datastore_role_id: Optional[UUID] = None
    datastore_admin: bool = False
    datastore_disabled: bool = False


class DataStoreAssociationUpdateRequest(BaseModel):
    manager: bool = optional_field
    disabled: bool = optional_field

    datastore_username: Optional[str] = optional_field
    datastore_role_id: Optional[UUID] = optional_field
    datastore_admin: bool = optional_field
    datastore_disabled: bool = optional_field
