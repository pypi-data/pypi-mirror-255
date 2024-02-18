from lqs.interface.core import CreateInterface
from lqs.client.common import RESTInterface
import lqs.interface.core.models as models


class Create(CreateInterface, RESTInterface):
    service: str = "lqs"

    def __init__(self, app):
        super().__init__(app=app)

    def _api_key(self, **params):
        return self._create_resource("apiKeys", params, models.APIKeyDataResponse)

    def _digestion(self, **params):
        return self._create_resource("digestions", params, models.DigestionDataResponse)

    def _digestion_part(self, **params):
        digestion_id = params.pop("digestion_id")
        return self._create_resource(
            f"digestions/{digestion_id}/parts", params, models.DigestionPartDataResponse
        )

    def _digestion_topic(self, **params):
        digestion_id = params.pop("digestion_id")
        return self._create_resource(
            f"digestions/{digestion_id}/topics",
            params,
            models.DigestionTopicDataResponse,
        )

    def _hook(self, **params):
        workflow_id = params.pop("workflow_id")
        return self._create_resource(
            f"workflows/{workflow_id}/hooks", params, models.HookDataResponse
        )

    def _group(self, **params):
        return self._create_resource("groups", params, models.GroupDataResponse)

    def _ingestion(self, **params):
        return self._create_resource("ingestions", params, models.IngestionDataResponse)

    def _ingestion_part(self, **params):
        ingestion_id = params.pop("ingestion_id")
        return self._create_resource(
            f"ingestions/{ingestion_id}/parts", params, models.IngestionPartDataResponse
        )

    def _label(self, **params):
        return self._create_resource("labels", params, models.LabelDataResponse)

    def _log(self, **params):
        return self._create_resource("logs", params, models.LogDataResponse)

    def _log_object(self, **params):
        log_id = params.pop("log_id")
        return self._create_resource(
            f"logs/{log_id}/objects", params, models.ObjectDataResponse
        )

    def _log_object_part(self, **params):
        log_id = params.pop("log_id")
        object_key = params.pop("object_key")
        return self._create_resource(
            f"logs/{log_id}/objects/{object_key}/parts",
            params,
            models.ObjectPartDataResponse,
        )

    def _object(self, **params):
        raise NotImplementedError

    def _object_part(self, **params):
        raise NotImplementedError

    def _object_store(self, **params):
        return self._create_resource(
            "objectStores", params, models.ObjectStoreDataResponse
        )

    def _query(self, **params):
        log_id = params.pop("log_id")
        return self._create_resource(
            f"logs/{log_id}/queries", params, models.QueryDataResponse
        )

    def _record(self, **params):
        topic_id = params.pop("topic_id")
        return self._create_resource(
            f"topics/{topic_id}/records", params, models.RecordDataResponse
        )

    def _role(self, **params):
        return self._create_resource("roles", params, models.RoleDataResponse)

    def _tag(self, **params):
        log_id = params.pop("log_id")
        return self._create_resource(
            f"logs/{log_id}/tags", params, models.TagDataResponse
        )

    def _topic(self, **params):
        return self._create_resource("topics", params, models.TopicDataResponse)

    def _user(self, **params):
        return self._create_resource("users", params, models.UserDataResponse)

    def _workflow(self, **params):
        return self._create_resource("workflows", params, models.WorkflowDataResponse)
