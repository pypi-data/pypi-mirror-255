from abc import ABC, abstractmethod
from uuid import UUID

import lqs.interface.pjm.models as models


class UpdateInterface(ABC):
    def _process_data(self, data) -> dict:
        if not isinstance(data, dict):
            return data.model_dump(exclude_unset=True)
        return data

    @abstractmethod
    def _event(self, **kwargs) -> models.EventDataResponse:
        pass

    def event(self, event_id: UUID, data: models.EventUpdateRequest):
        return self._event(
            event_id=event_id,
            data=self._process_data(data),
        )

    @abstractmethod
    def _job(self, **kwargs) -> models.JobDataResponse:
        pass

    def job(self, job_id: UUID, data: models.JobUpdateRequest):
        return self._job(
            job_id=job_id,
            data=self._process_data(data),
        )
