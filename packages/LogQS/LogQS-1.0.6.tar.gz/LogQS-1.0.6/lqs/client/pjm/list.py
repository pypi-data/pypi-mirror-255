from lqs.interface.pjm import ListInterface
from lqs.client.common import RESTInterface
import lqs.interface.pjm.models as models


class List(ListInterface, RESTInterface):
    service: str = "pjm"

    def __init__(self, app):
        super().__init__(app=app)

    def _event(self, **params):
        resource_path = "events" + self._get_url_param_string(params, [])
        result = self._get_resource(
            resource_path, response_model=models.EventListResponse
        )
        return result

    def _job(self, **params):
        resource_path = "jobs" + self._get_url_param_string(params, [])
        result = self._get_resource(
            resource_path, response_model=models.JobListResponse
        )
        return result
