from abc import ABC, abstractmethod
from uuid import UUID

import lqs.interface.pjm.models as models


class FetchInterface(ABC):
    @abstractmethod
    def _event(self, **kwargs) -> models.EventDataResponse:
        pass

    def event(self, event_id: UUID):
        return self._event(
            event_id=event_id,
        )

    @abstractmethod
    def _job(self, **kwargs) -> models.JobDataResponse:
        pass

    def job(self, job_id: UUID):
        return self._job(
            job_id=job_id,
        )
