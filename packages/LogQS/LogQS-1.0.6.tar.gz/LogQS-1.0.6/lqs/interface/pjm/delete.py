from abc import ABC, abstractmethod
from uuid import UUID


class DeleteInterface(ABC):
    @abstractmethod
    def _event(self, **kwargs):
        pass

    def event(self, event_id: UUID):
        return self._event(
            event_id=event_id,
        )

    @abstractmethod
    def _job(self, **kwargs):
        pass

    def job(self, job_id: UUID):
        return self._job(
            job_id=job_id,
        )
