from lqs.interface.pjm import CreateInterface
from lqs.client.common import RESTInterface
import lqs.interface.pjm.models as models


class Create(CreateInterface, RESTInterface):
    service: str = "pjm"

    def __init__(self, app):
        super().__init__(app=app)

    def _event(self, **params):
        return self._create_resource("events", params, models.EventDataResponse)

    def _job(self, **params):
        return self._create_resource("jobs", params, models.JobDataResponse)
