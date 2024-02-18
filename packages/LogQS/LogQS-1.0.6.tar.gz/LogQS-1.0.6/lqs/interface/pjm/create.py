from abc import ABC, abstractmethod
from uuid import UUID
from typing import Optional

import lqs.interface.pjm.models as models


class CreateInterface(ABC):
    @abstractmethod
    def _event(self, **kwargs) -> models.EventDataResponse:
        pass

    def event(
        self,
        current_state: str,
        process_type: str,
        resource_id: UUID,
        previous_state: Optional[str] = None,
        workflow_id: Optional[UUID] = None,
        hook_id: Optional[UUID] = None,
        datastore_id: Optional[UUID] = None,
        datastore_endpoint: Optional[str] = None,
    ):
        return self._event(
            current_state=current_state,
            process_type=process_type,
            resource_id=resource_id,
            previous_state=previous_state,
            workflow_id=workflow_id,
            hook_id=hook_id,
            datastore_id=datastore_id,
            datastore_endpoint=datastore_endpoint,
        )

    def _event_by_model(self, data: models.EventCreateRequest):
        return self.event(**data.model_dump())

    @abstractmethod
    def _job(self, **kwargs) -> models.JobDataResponse:
        pass

    def job(
        self,
        type: str,
        process_type: str,
        resource_id: UUID,
        event_id: Optional[UUID] = None,
        datastore_id: Optional[UUID] = None,
        datastore_endpoint: Optional[str] = None,
        state: str = "ready",
    ):
        return self._job(
            type=type,
            process_type=process_type,
            resource_id=resource_id,
            event_id=event_id,
            datastore_id=datastore_id,
            datastore_endpoint=datastore_endpoint,
            state=state,
        )

    def _job_by_model(self, data: models.JobCreateRequest):
        return self.job(**data.model_dump())
