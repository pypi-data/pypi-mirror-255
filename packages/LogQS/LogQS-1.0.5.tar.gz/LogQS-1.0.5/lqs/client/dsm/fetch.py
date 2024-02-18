from lqs.interface.dsm import FetchInterface
from lqs.client.common import RESTInterface
import lqs.interface.dsm.models as models


class Fetch(FetchInterface, RESTInterface):
    service: str = "dsm"

    def __init__(self, app):
        super().__init__(app=app)

    def _announcement(self, **params):
        announcement_id = params.pop("announcement_id")
        result = self._get_resource(
            f"announcements/{announcement_id}",
            response_model=models.AnnouncementDataResponse,
        )
        return result

    def _api_key(self, **params):
        api_key_id = params.pop("api_key_id")
        result = self._get_resource(
            f"apiKeys/{api_key_id}", response_model=models.APIKeyDataResponse
        )
        return result

    def _comment(self, **params):
        comment_id = params.pop("comment_id")
        result = self._get_resource(
            f"comments/{comment_id}", response_model=models.CommentDataResponse
        )
        return result

    def _configuration(self, **params):
        configuration_id = params.pop("configuration_id")
        result = self._get_resource(
            f"configurations/{configuration_id}",
            response_model=models.ConfigurationDataResponse,
        )
        return result

    def _datastore(self, **params):
        datastore_id = params.pop("datastore_id")
        result = self._get_resource(
            f"dataStores/{datastore_id}", response_model=models.DataStoreDataResponse
        )
        return result

    def _datastore_association(self, **params):
        datastore_association_id = params.pop("datastore_association_id")
        result = self._get_resource(
            f"dataStoreAssociations/{datastore_association_id}",
            response_model=models.DataStoreAssociationDataResponse,
        )
        return result

    def _me(self, **params):
        result = self._get_resource("users/me", response_model=models.MeDataResponse)
        return result

    def _role(self, **params):
        role_id = params.pop("role_id")
        result = self._get_resource(
            f"roles/{role_id}", response_model=models.RoleDataResponse
        )
        return result

    def _usage_tick(self, **params):
        datastore_id = params.pop("datastore_id")
        timestamp = params.pop("timestamp")
        result = self._get_resource(
            f"dataStores/{datastore_id}/usageTicks/{timestamp}",
            response_model=models.UsageTickDataResponse,
        )
        return result

    def _user(self, **params):
        user_id = params.pop("user_id")
        result = self._get_resource(
            f"users/{user_id}", response_model=models.UserDataResponse
        )
        return result
