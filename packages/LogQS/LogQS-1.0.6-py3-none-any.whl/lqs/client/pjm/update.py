from lqs.interface.pjm import UpdateInterface
from lqs.client.common import RESTInterface
import lqs.interface.pjm.models as models


class Update(UpdateInterface, RESTInterface):
    service: str = "pjm"

    def __init__(self, app):
        super().__init__(app=app)

    def _event(self, **params):
        event_id = params.pop("event_id")
        data = params.pop("data")
        return self._update_resource(
            f"events/{event_id}", data, models.EventDataResponse
        )

    def _job(self, **params):
        job_id = params.pop("job_id")
        data = params.pop("data")
        return self._update_resource(f"jobs/{job_id}", data, models.JobDataResponse)
