from abc import abstractmethod
from typing import Optional
from uuid import UUID

from lqs.interface.base.create import CreateInterface as BaseCreateInterface
import lqs.interface.dsm.models as models


class CreateInterface(BaseCreateInterface):
    @abstractmethod
    def _announcement(self, **kwargs) -> models.AnnouncementDataResponse:
        pass

    def announcement(
        self,
        datastore_id: Optional[UUID] = None,
        subject: Optional[str] = None,
        content: Optional[str] = None,
        context: Optional[dict] = None,
        status: Optional[str] = None,
        starts_at: Optional[int] = None,
        ends_at: Optional[int] = None,
    ):
        return self._announcement(
            datastore_id=datastore_id,
            subject=subject,
            content=content,
            context=context,
            status=status,
            starts_at=starts_at,
            ends_at=ends_at,
        )

    def _announcement_by_model(self, data: models.AnnouncementCreateRequest):
        return self.announcement(**data.model_dump())

    @abstractmethod
    def _comment(self, **kwargs) -> models.CommentDataResponse:
        pass

    def comment(
        self,
        user_id: Optional[UUID] = None,
        datastore_id: Optional[UUID] = None,
        resource_type: Optional[str] = None,
        resource_id: Optional[UUID] = None,
        subject: Optional[str] = None,
        content: Optional[str] = None,
        context: Optional[dict] = None,
    ):
        return self._comment(
            user_id=user_id,
            datastore_id=datastore_id,
            resource_type=resource_type,
            resource_id=resource_id,
            subject=subject,
            content=content,
            context=context,
        )

    def _comment_by_model(self, data: models.CommentCreateRequest):
        return self.comment(**data.model_dump())

    @abstractmethod
    def _configuration(self, **kwargs) -> models.ConfigurationDataResponse:
        pass

    def configuration(
        self,
        value: dict,
        name: Optional[str] = None,
        note: Optional[str] = None,
        default: bool = False,
        disabled: bool = False,
    ):
        return self._configuration(
            value=value,
            name=name,
            note=note,
            default=default,
            disabled=disabled,
        )

    def _configuration_by_model(self, data: models.ConfigurationCreateRequest):
        return self.configuration(**data.model_dump())

    @abstractmethod
    def _datastore(self, **kwargs) -> models.DataStoreDataResponse:
        pass

    def datastore(
        self,
        name: str,
        note: Optional[str] = None,
        context: Optional[dict] = None,
        owner_id: Optional[UUID] = None,
        config: Optional[dict] = None,
        version: Optional[str] = None,
        region: Optional[str] = None,
        endpoint: Optional[str] = None,
        disabled: bool = False,
    ):
        return self._datastore(
            name=name,
            note=note,
            context=context,
            owner_id=owner_id,
            config=config,
            version=version,
            region=region,
            endpoint=endpoint,
            disabled=disabled,
        )

    def _datastore_by_model(self, data: models.DataStoreCreateRequest):
        return self.datastore(**data.model_dump())

    @abstractmethod
    def _datastore_association(
        self, **kwargs
    ) -> models.DataStoreAssociationDataResponse:
        pass

    def datastore_association(
        self,
        user_id: UUID,
        datastore_id: UUID,
        manager: bool = False,
        disabled: bool = False,
        datastore_user_id: Optional[UUID] = None,
        datastore_username: Optional[str] = None,
        datastore_role_id: Optional[UUID] = None,
        datastore_admin: bool = False,
        datastore_disabled: bool = False,
    ):
        return self._datastore_association(
            user_id=user_id,
            datastore_id=datastore_id,
            manager=manager,
            disabled=disabled,
            datastore_user_id=datastore_user_id,
            datastore_username=datastore_username,
            datastore_role_id=datastore_role_id,
            datastore_admin=datastore_admin,
            datastore_disabled=datastore_disabled,
        )

    def _datastore_association_by_model(
        self, data: models.DataStoreAssociationCreateRequest
    ):
        return self.datastore_association(**data.model_dump())

    @abstractmethod
    def _usage_tick(self, **kwargs) -> models.UsageTickDataResponse:
        pass

    def usage_tick(
        self,
        timestamp: int,
        datastore_id: UUID,
        log_count: int,
        record_count: int,
        record_size: int,
        object_count: int,
        object_size: int,
        transfer_size: int,
    ):
        return self._usage_tick(
            timestamp=timestamp,
            datastore_id=datastore_id,
            log_count=log_count,
            record_count=record_count,
            record_size=record_size,
            object_count=object_count,
            object_size=object_size,
            transfer_size=transfer_size,
        )

    def _usage_tick_by_model(
        self, datastore_id: UUID, data: models.UsageTickCreateRequest
    ):
        return self.usage_tick(datastore_id=datastore_id, **data.model_dump())
