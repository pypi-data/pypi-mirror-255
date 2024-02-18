from typing import Optional
from datetime import datetime
from uuid import UUID
from abc import ABC, abstractmethod

import lqs.interface.pjm.models as models


class ListInterface(ABC):
    @abstractmethod
    def _event(self, **kwargs) -> models.EventListResponse:
        pass

    def event(
        self,
        previous_state: Optional[str] = None,
        current_state: Optional[str] = None,
        process_type: Optional[str] = None,
        resource_id: Optional[UUID] = None,
        workflow_id: Optional[UUID] = None,
        hook_id: Optional[UUID] = None,
        datastore_id: Optional[UUID] = None,
        datastore_endpoint: Optional[str] = None,
        offset: Optional[int] = 0,
        limit: Optional[int] = 100,
        order: Optional[str] = "created_at",
        sort: Optional[str] = "ASC",
        created_by: Optional[UUID] = None,
        updated_by: Optional[UUID] = None,
        deleted_by: Optional[UUID] = None,
        updated_by_null: Optional[bool] = None,
        deleted_by_null: Optional[bool] = None,
        updated_at_null: Optional[bool] = None,
        deleted_at_null: Optional[bool] = None,
        created_at_lte: Optional[datetime] = None,
        updated_at_lte: Optional[datetime] = None,
        deleted_at_lte: Optional[datetime] = None,
        created_at_gte: Optional[datetime] = None,
        updated_at_gte: Optional[datetime] = None,
        deleted_at_gte: Optional[datetime] = None,
    ):
        return self._event(
            previous_state=previous_state,
            current_state=current_state,
            process_type=process_type,
            resource_id=resource_id,
            workflow_id=workflow_id,
            hook_id=hook_id,
            datastore_id=datastore_id,
            datastore_endpoint=datastore_endpoint,
            offset=offset,
            limit=limit,
            order=order,
            sort=sort,
            created_by=created_by,
            updated_by=updated_by,
            deleted_by=deleted_by,
            updated_by_null=updated_by_null,
            deleted_by_null=deleted_by_null,
            updated_at_null=updated_at_null,
            deleted_at_null=deleted_at_null,
            created_at_lte=created_at_lte,
            updated_at_lte=updated_at_lte,
            deleted_at_lte=deleted_at_lte,
            created_at_gte=created_at_gte,
            updated_at_gte=updated_at_gte,
            deleted_at_gte=deleted_at_gte,
        )

    def events(self, **kwargs):
        return self.event(**kwargs)

    @abstractmethod
    def _job(self, **kwargs) -> models.JobListResponse:
        pass

    def job(
        self,
        event_id: Optional[UUID] = None,
        process_type: Optional[str] = None,
        resource_id: Optional[UUID] = None,
        datastore_id: Optional[UUID] = None,
        datastore_endpoint: Optional[str] = None,
        state: Optional[str] = None,
        offset: Optional[int] = 0,
        limit: Optional[int] = 100,
        order: Optional[str] = "created_at",
        sort: Optional[str] = "ASC",
        created_by: Optional[UUID] = None,
        updated_by: Optional[UUID] = None,
        deleted_by: Optional[UUID] = None,
        updated_by_null: Optional[bool] = None,
        deleted_by_null: Optional[bool] = None,
        updated_at_null: Optional[bool] = None,
        deleted_at_null: Optional[bool] = None,
        created_at_lte: Optional[datetime] = None,
        updated_at_lte: Optional[datetime] = None,
        deleted_at_lte: Optional[datetime] = None,
        created_at_gte: Optional[datetime] = None,
        updated_at_gte: Optional[datetime] = None,
        deleted_at_gte: Optional[datetime] = None,
    ):
        return self._job(
            event_id=event_id,
            process_type=process_type,
            resource_id=resource_id,
            datastore_id=datastore_id,
            datastore_endpoint=datastore_endpoint,
            state=state,
            offset=offset,
            limit=limit,
            order=order,
            sort=sort,
            created_by=created_by,
            updated_by=updated_by,
            deleted_by=deleted_by,
            updated_by_null=updated_by_null,
            deleted_by_null=deleted_by_null,
            updated_at_null=updated_at_null,
            deleted_at_null=deleted_at_null,
            created_at_lte=created_at_lte,
            updated_at_lte=updated_at_lte,
            deleted_at_lte=deleted_at_lte,
            created_at_gte=created_at_gte,
            updated_at_gte=updated_at_gte,
            deleted_at_gte=deleted_at_gte,
        )

    def jobs(self, **kwargs):
        return self.job(**kwargs)
