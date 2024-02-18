from lqs.interface.dsm import ListInterface
from lqs.client.common import RESTInterface
import lqs.interface.dsm.models as models


class List(ListInterface, RESTInterface):
    service: str = "dsm"

    def __init__(self, app):
        super().__init__(app=app)

    def _announcement(self, **params):
        resource_path = "announcements" + self._get_url_param_string(params, [])
        result = self._get_resource(
            resource_path, response_model=models.AnnouncementListResponse
        )
        return result

    def _api_key(self, **params):
        resource_path = "apiKeys" + self._get_url_param_string(params, [])
        result = self._get_resource(
            resource_path, response_model=models.APIKeyListResponse
        )
        return result

    def _comment(self, **params):
        resource_path = "comments" + self._get_url_param_string(params, [])
        result = self._get_resource(
            resource_path, response_model=models.CommentListResponse
        )
        return result

    def _configuration(self, **params):
        resource_path = "configurations" + self._get_url_param_string(params, [])
        result = self._get_resource(
            resource_path, response_model=models.ConfigurationListResponse
        )
        return result

    def _datastore(self, **params):
        resource_path = "dataStores" + self._get_url_param_string(params, [])
        result = self._get_resource(
            resource_path, response_model=models.DataStoreListResponse
        )
        return result

    def _datastore_association(self, **params):
        resource_path = "dataStoreAssociations" + self._get_url_param_string(params, [])
        result = self._get_resource(
            resource_path, response_model=models.DataStoreAssociationListResponse
        )
        return result

    def _role(self, **params):
        resource_path = "roles" + self._get_url_param_string(params, [])
        result = self._get_resource(
            resource_path, response_model=models.RoleListResponse
        )
        return result

    def _usage_tick(self, **params):
        datastore_id = params.pop("datastore_id")
        resource_path = (
            f"dataStores/{datastore_id}/usageTicks"
            + self._get_url_param_string(params, [])
        )
        result = self._get_resource(
            resource_path, response_model=models.UsageTickListResponse
        )
        return result

    def _user(self, **params):
        resource_path = "users" + self._get_url_param_string(params, [])
        result = self._get_resource(
            resource_path, response_model=models.UserListResponse
        )
        return result
