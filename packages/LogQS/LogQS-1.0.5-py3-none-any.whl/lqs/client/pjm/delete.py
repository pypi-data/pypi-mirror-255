from uuid import UUID

from lqs.interface.pjm import DeleteInterface

from lqs.client.common import RESTInterface

# TODO: make this consistent with other interfaces


class Delete(DeleteInterface, RESTInterface):
    service: str = "pjm"

    def __init__(self, app):
        super().__init__(app=app)

    def _event(self, event_id: UUID):
        self._delete_resource(f"events/{event_id}")
        return

    def _job(self, job_id: UUID):
        self._delete_resource(f"jobs/{job_id}")
        return
