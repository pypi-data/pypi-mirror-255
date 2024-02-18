from lqs.interface.pjm import FetchInterface
from lqs.client.common import RESTInterface
import lqs.interface.pjm.models as models


class Fetch(FetchInterface, RESTInterface):
    service: str = "pjm"

    def __init__(self, app):
        super().__init__(app=app)

    def _event(self, **params):
        event_id = params.pop("event_id")
        result = self._get_resource(
            f"events/{event_id}", response_model=models.EventDataResponse
        )
        return result

    def _job(self, **params):
        job_id = params.pop("job_id")
        result = self._get_resource(
            f"jobs/{job_id}", response_model=models.JobDataResponse
        )
        return result
