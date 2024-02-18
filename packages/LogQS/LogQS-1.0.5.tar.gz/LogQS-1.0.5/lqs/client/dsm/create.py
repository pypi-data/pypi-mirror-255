from lqs.interface.dsm import CreateInterface
from lqs.client.common import RESTInterface
import lqs.interface.dsm.models as models


class Create(CreateInterface, RESTInterface):
    service: str = "dsm"

    def __init__(self, app):
        super().__init__(app=app)

    def _announcement(self, **params):
        return self._create_resource(
            "announcements", params, models.AnnouncementDataResponse
        )

    def _api_key(self, **params):
        return self._create_resource("apiKeys", params, models.APIKeyDataResponse)

    def _comment(self, **params):
        return self._create_resource("comments", params, models.CommentDataResponse)

    def _configuration(self, **params):
        return self._create_resource(
            "configurations", params, models.ConfigurationDataResponse
        )

    def _datastore(self, **params):
        return self._create_resource("dataStores", params, models.DataStoreDataResponse)

    def _datastore_association(self, **params):
        return self._create_resource(
            "dataStoreAssociations", params, models.DataStoreAssociationDataResponse
        )

    def _role(self, **params):
        return self._create_resource("roles", params, models.RoleDataResponse)

    def _usage_tick(self, **params):
        datastore_id = params.pop("datastore_id")
        return self._create_resource(
            f"dataStores/{datastore_id}/usageTicks",
            params,
            models.UsageTickDataResponse,
        )

    def _user(self, **params):
        return self._create_resource("users", params, models.UserDataResponse)
