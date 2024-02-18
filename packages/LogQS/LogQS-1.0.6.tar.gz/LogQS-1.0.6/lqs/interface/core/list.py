from typing import Optional
from datetime import datetime
from uuid import UUID
from abc import abstractmethod

import lqs.interface.core.models as models
from lqs.interface.base.list import ListInterface as BaseListInterface


class ListInterface(BaseListInterface):
    @abstractmethod
    def _digestion(self, **kwargs) -> models.DigestionListResponse:
        pass

    def digestion(
        self,
        group_id: Optional[UUID] = None,
        log_id: Optional[UUID] = None,
        workflow_id: Optional[UUID] = None,
        workflow_id_null: Optional[bool] = None,
        state: Optional[str] = None,
        name: Optional[str] = None,
        name_like: Optional[str] = None,
        progress_null: Optional[bool] = None,
        progress_gte: Optional[float] = None,
        progress_lte: Optional[float] = None,
        error_like: Optional[str] = None,
        note_like: Optional[str] = None,
        context_filter: Optional[str] = None,
        workflow_context_filter: Optional[str] = None,
        offset: Optional[int] = 0,
        limit: Optional[int] = 100,
        order: Optional[str] = "created_at",
        sort: Optional[str] = "ASC",
        created_by: Optional[UUID] = None,
        updated_by: Optional[UUID] = None,
        deleted_by: Optional[UUID] = None,
        updated_by_null: Optional[bool] = None,
        deleted_by_null: Optional[bool] = None,
        updated_at_null: Optional[bool] = None,
        deleted_at_null: Optional[bool] = None,
        created_at_lte: Optional[datetime] = None,
        updated_at_lte: Optional[datetime] = None,
        deleted_at_lte: Optional[datetime] = None,
        created_at_gte: Optional[datetime] = None,
        updated_at_gte: Optional[datetime] = None,
        deleted_at_gte: Optional[datetime] = None,
    ):
        """
        Lists digestions.
        """
        return self._digestion(
            group_id=group_id,
            log_id=log_id,
            workflow_id=workflow_id,
            workflow_id_null=workflow_id_null,
            state=state,
            name=name,
            name_like=name_like,
            progress_null=progress_null,
            progress_gte=progress_gte,
            progress_lte=progress_lte,
            error_like=error_like,
            note_like=note_like,
            context_filter=context_filter,
            workflow_context_filter=workflow_context_filter,
            offset=offset,
            limit=limit,
            order=order,
            sort=sort,
            created_by=created_by,
            updated_by=updated_by,
            deleted_by=deleted_by,
            updated_by_null=updated_by_null,
            deleted_by_null=deleted_by_null,
            updated_at_null=updated_at_null,
            deleted_at_null=deleted_at_null,
            created_at_lte=created_at_lte,
            updated_at_lte=updated_at_lte,
            deleted_at_lte=deleted_at_lte,
            created_at_gte=created_at_gte,
            updated_at_gte=updated_at_gte,
            deleted_at_gte=deleted_at_gte,
        )

    def digestions(self, **kwargs):
        return self.digestion(**kwargs)

    @abstractmethod
    def _digestion_part(self, **kwargs) -> models.DigestionPartListResponse:
        pass

    def digestion_part(
        self,
        group_id: Optional[UUID] = None,
        log_id: Optional[UUID] = None,
        sequence: Optional[int] = None,
        digestion_id: Optional[UUID] = None,
        workflow_id: Optional[UUID] = None,
        workflow_id_null: Optional[bool] = None,
        state: Optional[str] = None,
        offset: Optional[int] = 0,
        limit: Optional[int] = 100,
        order: Optional[str] = "created_at",
        sort: Optional[str] = "ASC",
        created_by: Optional[UUID] = None,
        updated_by: Optional[UUID] = None,
        deleted_by: Optional[UUID] = None,
        updated_by_null: Optional[bool] = None,
        deleted_by_null: Optional[bool] = None,
        updated_at_null: Optional[bool] = None,
        deleted_at_null: Optional[bool] = None,
        created_at_lte: Optional[datetime] = None,
        updated_at_lte: Optional[datetime] = None,
        deleted_at_lte: Optional[datetime] = None,
        created_at_gte: Optional[datetime] = None,
        updated_at_gte: Optional[datetime] = None,
        deleted_at_gte: Optional[datetime] = None,
    ):
        """
        Lists digestion parts.
        """
        return self._digestion_part(
            group_id=group_id,
            log_id=log_id,
            sequence=sequence,
            digestion_id=digestion_id,
            workflow_id=workflow_id,
            workflow_id_null=workflow_id_null,
            state=state,
            offset=offset,
            limit=limit,
            order=order,
            sort=sort,
            created_by=created_by,
            updated_by=updated_by,
            deleted_by=deleted_by,
            updated_by_null=updated_by_null,
            deleted_by_null=deleted_by_null,
            updated_at_null=updated_at_null,
            deleted_at_null=deleted_at_null,
            created_at_lte=created_at_lte,
            updated_at_lte=updated_at_lte,
            deleted_at_lte=deleted_at_lte,
            created_at_gte=created_at_gte,
            updated_at_gte=updated_at_gte,
            deleted_at_gte=deleted_at_gte,
        )

    def digestion_parts(self, **kwargs):
        return self.digestion_part(**kwargs)

    @abstractmethod
    def _digestion_topic(self, **kwargs) -> models.DigestionTopicListResponse:
        pass

    def digestion_topic(
        self,
        digestion_id: UUID,  # TODO: should this still be a required parameter with group and log id changes?
        group_id: Optional[UUID] = None,
        log_id: Optional[UUID] = None,
        topic_id: Optional[UUID] = None,
        start_time_null: Optional[bool] = None,
        start_time_gte: Optional[int] = None,
        start_time_lte: Optional[int] = None,
        end_time_null: Optional[bool] = None,
        end_time_gte: Optional[int] = None,
        end_time_lte: Optional[int] = None,
        offset: Optional[int] = 0,
        limit: Optional[int] = 100,
        order: Optional[str] = "created_at",
        sort: Optional[str] = "ASC",
        created_by: Optional[UUID] = None,
        updated_by: Optional[UUID] = None,
        deleted_by: Optional[UUID] = None,
        updated_by_null: Optional[bool] = None,
        deleted_by_null: Optional[bool] = None,
        updated_at_null: Optional[bool] = None,
        deleted_at_null: Optional[bool] = None,
        created_at_lte: Optional[datetime] = None,
        updated_at_lte: Optional[datetime] = None,
        deleted_at_lte: Optional[datetime] = None,
        created_at_gte: Optional[datetime] = None,
        updated_at_gte: Optional[datetime] = None,
        deleted_at_gte: Optional[datetime] = None,
    ):
        """
        Lists digestion topics.
        """
        return self._digestion_topic(
            group_id=group_id,
            log_id=log_id,
            digestion_id=digestion_id,
            topic_id=topic_id,
            start_time_null=start_time_null,
            start_time_gte=start_time_gte,
            start_time_lte=start_time_lte,
            end_time_null=end_time_null,
            end_time_gte=end_time_gte,
            end_time_lte=end_time_lte,
            offset=offset,
            limit=limit,
            order=order,
            sort=sort,
            created_by=created_by,
            updated_by=updated_by,
            deleted_by=deleted_by,
            updated_by_null=updated_by_null,
            deleted_by_null=deleted_by_null,
            updated_at_null=updated_at_null,
            deleted_at_null=deleted_at_null,
            created_at_lte=created_at_lte,
            updated_at_lte=updated_at_lte,
            deleted_at_lte=deleted_at_lte,
            created_at_gte=created_at_gte,
            updated_at_gte=updated_at_gte,
            deleted_at_gte=deleted_at_gte,
        )

    def digestion_topics(self, **kwargs):
        return self.digestion_topic(**kwargs)

    @abstractmethod
    def _group(self, **kwargs) -> models.GroupListResponse:
        pass

    def group(
        self,
        name: Optional[str] = None,
        name_like: Optional[str] = None,
        default_workflow_id: Optional[UUID] = None,
        default_workflow_id_null: Optional[bool] = None,
        offset: Optional[int] = 0,
        limit: Optional[int] = 100,
        order: Optional[str] = "created_at",
        sort: Optional[str] = "ASC",
        created_by: Optional[UUID] = None,
        updated_by: Optional[UUID] = None,
        deleted_by: Optional[UUID] = None,
        updated_by_null: Optional[bool] = None,
        deleted_by_null: Optional[bool] = None,
        updated_at_null: Optional[bool] = None,
        deleted_at_null: Optional[bool] = None,
        created_at_lte: Optional[datetime] = None,
        updated_at_lte: Optional[datetime] = None,
        deleted_at_lte: Optional[datetime] = None,
        created_at_gte: Optional[datetime] = None,
        updated_at_gte: Optional[datetime] = None,
        deleted_at_gte: Optional[datetime] = None,
    ):
        """
        Lists groups.
        """
        return self._group(
            name=name,
            name_like=name_like,
            default_workflow_id=default_workflow_id,
            default_workflow_id_null=default_workflow_id_null,
            offset=offset,
            limit=limit,
            order=order,
            sort=sort,
            created_by=created_by,
            updated_by=updated_by,
            deleted_by=deleted_by,
            updated_by_null=updated_by_null,
            deleted_by_null=deleted_by_null,
            updated_at_null=updated_at_null,
            deleted_at_null=deleted_at_null,
            created_at_lte=created_at_lte,
            updated_at_lte=updated_at_lte,
            deleted_at_lte=deleted_at_lte,
            created_at_gte=created_at_gte,
            updated_at_gte=updated_at_gte,
            deleted_at_gte=deleted_at_gte,
        )

    def groups(self, **kwargs):
        return self.group(**kwargs)

    @abstractmethod
    def _hook(self, **kwargs) -> models.HookListResponse:
        pass

    def hook(
        self,
        workflow_id: Optional[UUID] = None,
        trigger_process: Optional[str] = None,
        trigger_state: Optional[str] = None,
        name: Optional[str] = None,
        name_like: Optional[str] = None,
        note_like: Optional[str] = None,
        managed: Optional[bool] = None,
        disabled: Optional[bool] = None,
        uri: Optional[str] = None,
        uri_like: Optional[str] = None,
        offset: Optional[int] = 0,
        limit: Optional[int] = 100,
        order: Optional[str] = "created_at",
        sort: Optional[str] = "ASC",
        created_by: Optional[UUID] = None,
        updated_by: Optional[UUID] = None,
        deleted_by: Optional[UUID] = None,
        updated_by_null: Optional[bool] = None,
        deleted_by_null: Optional[bool] = None,
        updated_at_null: Optional[bool] = None,
        deleted_at_null: Optional[bool] = None,
        created_at_lte: Optional[datetime] = None,
        updated_at_lte: Optional[datetime] = None,
        deleted_at_lte: Optional[datetime] = None,
        created_at_gte: Optional[datetime] = None,
        updated_at_gte: Optional[datetime] = None,
        deleted_at_gte: Optional[datetime] = None,
    ):
        """
        Lists hooks.
        """
        return self._hook(
            workflow_id=workflow_id,
            trigger_process=trigger_process,
            trigger_state=trigger_state,
            name=name,
            name_like=name_like,
            note_like=note_like,
            uri=uri,
            uri_like=uri_like,
            managed=managed,
            disabled=disabled,
            offset=offset,
            limit=limit,
            order=order,
            sort=sort,
            created_by=created_by,
            updated_by=updated_by,
            deleted_by=deleted_by,
            updated_by_null=updated_by_null,
            deleted_by_null=deleted_by_null,
            updated_at_null=updated_at_null,
            deleted_at_null=deleted_at_null,
            created_at_lte=created_at_lte,
            updated_at_lte=updated_at_lte,
            deleted_at_lte=deleted_at_lte,
            created_at_gte=created_at_gte,
            updated_at_gte=updated_at_gte,
            deleted_at_gte=deleted_at_gte,
        )

    def hooks(self, **kwargs):
        return self.hook(**kwargs)

    @abstractmethod
    def _ingestion(self, **kwargs) -> models.IngestionListResponse:
        pass

    def ingestion(
        self,
        group_id: Optional[UUID] = None,
        log_id: Optional[UUID] = None,
        object_store_id: Optional[UUID] = None,
        name: Optional[str] = None,
        name_like: Optional[str] = None,
        object_key: Optional[str] = None,
        object_key_like: Optional[str] = None,
        workflow_id: Optional[UUID] = None,
        workflow_id_null: Optional[bool] = None,
        workflow_context_filter: Optional[str] = None,
        state: Optional[str] = None,
        progress_null: Optional[bool] = None,
        progress_gte: Optional[float] = None,
        progress_lte: Optional[float] = None,
        error_like: Optional[str] = None,
        note_like: Optional[str] = None,
        context_filter: Optional[str] = None,
        offset: Optional[int] = 0,
        limit: Optional[int] = 100,
        order: Optional[str] = "created_at",
        sort: Optional[str] = "ASC",
        created_by: Optional[UUID] = None,
        updated_by: Optional[UUID] = None,
        deleted_by: Optional[UUID] = None,
        updated_by_null: Optional[bool] = None,
        deleted_by_null: Optional[bool] = None,
        updated_at_null: Optional[bool] = None,
        deleted_at_null: Optional[bool] = None,
        created_at_lte: Optional[datetime] = None,
        updated_at_lte: Optional[datetime] = None,
        deleted_at_lte: Optional[datetime] = None,
        created_at_gte: Optional[datetime] = None,
        updated_at_gte: Optional[datetime] = None,
        deleted_at_gte: Optional[datetime] = None,
    ):
        """
        Lists ingestions.
        """
        return self._ingestion(
            group_id=group_id,
            log_id=log_id,
            object_store_id=object_store_id,
            name=name,
            name_like=name_like,
            object_key=object_key,
            object_key_like=object_key_like,
            workflow_id=workflow_id,
            workflow_id_null=workflow_id_null,
            workflow_context_filter=workflow_context_filter,
            state=state,
            progress_null=progress_null,
            progress_gte=progress_gte,
            progress_lte=progress_lte,
            error_like=error_like,
            note_like=note_like,
            context_filter=context_filter,
            offset=offset,
            limit=limit,
            order=order,
            sort=sort,
            created_by=created_by,
            updated_by=updated_by,
            deleted_by=deleted_by,
            updated_by_null=updated_by_null,
            deleted_by_null=deleted_by_null,
            updated_at_null=updated_at_null,
            deleted_at_null=deleted_at_null,
            created_at_lte=created_at_lte,
            updated_at_lte=updated_at_lte,
            deleted_at_lte=deleted_at_lte,
            created_at_gte=created_at_gte,
            updated_at_gte=updated_at_gte,
            deleted_at_gte=deleted_at_gte,
        )

    def ingestions(self, **kwargs):
        return self.ingestion(**kwargs)

    @abstractmethod
    def _ingestion_part(self, **kwargs) -> models.IngestionPartListResponse:
        pass

    def ingestion_part(
        self,
        group_id: Optional[UUID] = None,
        log_id: Optional[UUID] = None,
        ingestion_id: Optional[UUID] = None,
        sequence: Optional[int] = None,
        source: Optional[str] = None,
        workflow_id: Optional[UUID] = None,
        workflow_id_null: Optional[bool] = None,
        state: Optional[str] = None,
        offset: Optional[int] = 0,
        limit: Optional[int] = 100,
        order: Optional[str] = "created_at",
        sort: Optional[str] = "ASC",
        created_by: Optional[UUID] = None,
        updated_by: Optional[UUID] = None,
        deleted_by: Optional[UUID] = None,
        updated_by_null: Optional[bool] = None,
        deleted_by_null: Optional[bool] = None,
        updated_at_null: Optional[bool] = None,
        deleted_at_null: Optional[bool] = None,
        created_at_lte: Optional[datetime] = None,
        updated_at_lte: Optional[datetime] = None,
        deleted_at_lte: Optional[datetime] = None,
        created_at_gte: Optional[datetime] = None,
        updated_at_gte: Optional[datetime] = None,
        deleted_at_gte: Optional[datetime] = None,
    ):
        """
        Lists ingestion parts.
        """
        return self._ingestion_part(
            group_id=group_id,
            log_id=log_id,
            sequence=sequence,
            ingestion_id=ingestion_id,
            workflow_id=workflow_id,
            workflow_id_null=workflow_id_null,
            state=state,
            source=source,
            offset=offset,
            limit=limit,
            order=order,
            sort=sort,
            created_by=created_by,
            updated_by=updated_by,
            deleted_by=deleted_by,
            updated_by_null=updated_by_null,
            deleted_by_null=deleted_by_null,
            updated_at_null=updated_at_null,
            deleted_at_null=deleted_at_null,
            created_at_lte=created_at_lte,
            updated_at_lte=updated_at_lte,
            deleted_at_lte=deleted_at_lte,
            created_at_gte=created_at_gte,
            updated_at_gte=updated_at_gte,
            deleted_at_gte=deleted_at_gte,
        )

    def ingestion_parts(self, **kwargs):
        return self.ingestion_part(**kwargs)

    @abstractmethod
    def _label(self, **kwargs) -> models.LabelListResponse:
        pass

    def label(
        self,
        value: Optional[str] = None,
        value_like: Optional[str] = None,
        note_like: Optional[str] = None,
        offset: Optional[int] = 0,
        limit: Optional[int] = 100,
        order: Optional[str] = "created_at",
        sort: Optional[str] = "ASC",
        created_by: Optional[UUID] = None,
        updated_by: Optional[UUID] = None,
        deleted_by: Optional[UUID] = None,
        updated_by_null: Optional[bool] = None,
        deleted_by_null: Optional[bool] = None,
        updated_at_null: Optional[bool] = None,
        deleted_at_null: Optional[bool] = None,
        created_at_lte: Optional[datetime] = None,
        updated_at_lte: Optional[datetime] = None,
        deleted_at_lte: Optional[datetime] = None,
        created_at_gte: Optional[datetime] = None,
        updated_at_gte: Optional[datetime] = None,
        deleted_at_gte: Optional[datetime] = None,
    ):
        """
        Lists labels.
        """
        return self._label(
            value=value,
            value_like=value_like,
            note_like=note_like,
            offset=offset,
            limit=limit,
            order=order,
            sort=sort,
            created_by=created_by,
            updated_by=updated_by,
            deleted_by=deleted_by,
            updated_by_null=updated_by_null,
            deleted_by_null=deleted_by_null,
            updated_at_null=updated_at_null,
            deleted_at_null=deleted_at_null,
            created_at_lte=created_at_lte,
            updated_at_lte=updated_at_lte,
            deleted_at_lte=deleted_at_lte,
            created_at_gte=created_at_gte,
            updated_at_gte=updated_at_gte,
            deleted_at_gte=deleted_at_gte,
        )

    def labels(self, **kwargs):
        return self.label(**kwargs)

    @abstractmethod
    def _log(self, **kwargs) -> models.LogListResponse:
        pass

    def log(
        self,
        group_id: Optional[UUID] = None,
        default_workflow_id: Optional[UUID] = None,
        default_workflow_id_null: Optional[bool] = None,
        name: Optional[str] = None,
        name_like: Optional[str] = None,
        locked: Optional[bool] = None,
        note_like: Optional[str] = None,
        context_filter: Optional[str] = None,
        time_adjustment_null: Optional[bool] = None,
        time_adjustment_gte: Optional[int] = None,
        time_adjustment_lte: Optional[int] = None,
        start_time_null: Optional[bool] = None,
        start_time_gte: Optional[int] = None,
        start_time_lte: Optional[int] = None,
        end_time_null: Optional[bool] = None,
        end_time_gte: Optional[int] = None,
        end_time_lte: Optional[int] = None,
        record_size_gte: Optional[int] = None,
        record_size_lte: Optional[int] = None,
        record_count_gte: Optional[int] = None,
        record_count_lte: Optional[int] = None,
        object_size_gte: Optional[int] = None,
        object_size_lte: Optional[int] = None,
        object_count_gte: Optional[int] = None,
        object_count_lte: Optional[int] = None,
        offset: Optional[int] = 0,
        limit: Optional[int] = 100,
        order: Optional[str] = "created_at",
        sort: Optional[str] = "ASC",
        created_by: Optional[UUID] = None,
        updated_by: Optional[UUID] = None,
        deleted_by: Optional[UUID] = None,
        updated_by_null: Optional[bool] = None,
        deleted_by_null: Optional[bool] = None,
        updated_at_null: Optional[bool] = None,
        deleted_at_null: Optional[bool] = None,
        created_at_lte: Optional[datetime] = None,
        updated_at_lte: Optional[datetime] = None,
        deleted_at_lte: Optional[datetime] = None,
        created_at_gte: Optional[datetime] = None,
        updated_at_gte: Optional[datetime] = None,
        deleted_at_gte: Optional[datetime] = None,
    ):
        """
        Lists logs.
        """
        return self._log(
            group_id=group_id,
            default_workflow_id=default_workflow_id,
            default_workflow_id_null=default_workflow_id_null,
            name=name,
            name_like=name_like,
            locked=locked,
            note_like=note_like,
            context_filter=context_filter,
            time_adjustment_null=time_adjustment_null,
            time_adjustment_gte=time_adjustment_gte,
            time_adjustment_lte=time_adjustment_lte,
            start_time_null=start_time_null,
            start_time_gte=start_time_gte,
            start_time_lte=start_time_lte,
            end_time_null=end_time_null,
            end_time_gte=end_time_gte,
            end_time_lte=end_time_lte,
            record_size_gte=record_size_gte,
            record_size_lte=record_size_lte,
            record_count_gte=record_count_gte,
            record_count_lte=record_count_lte,
            object_size_gte=object_size_gte,
            object_size_lte=object_size_lte,
            object_count_gte=object_count_gte,
            object_count_lte=object_count_lte,
            offset=offset,
            limit=limit,
            order=order,
            sort=sort,
            created_by=created_by,
            updated_by=updated_by,
            deleted_by=deleted_by,
            updated_by_null=updated_by_null,
            deleted_by_null=deleted_by_null,
            updated_at_null=updated_at_null,
            deleted_at_null=deleted_at_null,
            created_at_lte=created_at_lte,
            updated_at_lte=updated_at_lte,
            deleted_at_lte=deleted_at_lte,
            created_at_gte=created_at_gte,
            updated_at_gte=updated_at_gte,
            deleted_at_gte=deleted_at_gte,
        )

    def logs(self, **kwargs):
        return self.log(**kwargs)

    @abstractmethod
    def _log_object(self, **kwargs) -> models.ObjectListResponse:
        pass

    def log_object(
        self,
        log_id: UUID,
        processing: Optional[bool] = False,
        max_keys: Optional[int] = None,
        prefix: Optional[str] = None,
        start_after: Optional[str] = None,
        delimiter: Optional[str] = None,
        continuation_token: Optional[str] = None,
    ):
        """
        Lists log objects.
        """
        return self._log_object(
            log_id=log_id,
            processing=processing,
            max_keys=max_keys,
            prefix=prefix,
            start_after=start_after,
            delimiter=delimiter,
            continuation_token=continuation_token,
        )

    def log_objects(self, **kwargs):
        return self.log_object(**kwargs)

    @abstractmethod
    def _log_object_part(self, **kwargs) -> models.ObjectPartListResponse:
        pass

    def log_object_part(
        self,
        object_key: str,
        log_id: UUID,
        max_parts: Optional[int] = None,
        part_number_marker: Optional[int] = None,
    ):
        """
        Lists log object parts.
        """
        return self._log_object_part(
            log_id=log_id,
            object_key=object_key,
            max_parts=max_parts,
            part_number_marker=part_number_marker,
        )

    def log_object_parts(self, **kwargs):
        return self.log_object_part(**kwargs)

    @abstractmethod
    def _object(self, **kwargs) -> models.ObjectListResponse:
        pass

    def object(
        self,
        object_store_id: UUID,
        processing: Optional[bool] = False,
        max_keys: Optional[int] = None,
        prefix: Optional[str] = None,
        start_after: Optional[str] = None,
        delimiter: Optional[str] = None,
        continuation_token: Optional[str] = None,
    ):
        """
        Lists objects.
        """
        return self._object(
            object_store_id=object_store_id,
            processing=processing,
            max_keys=max_keys,
            prefix=prefix,
            start_after=start_after,
            delimiter=delimiter,
            continuation_token=continuation_token,
        )

    def objects(self, **kwargs):
        return self.object(**kwargs)

    @abstractmethod
    def _object_part(self, **kwargs) -> models.ObjectPartListResponse:
        pass

    def object_part(
        self,
        object_key: str,
        object_store_id: UUID,
        max_parts: Optional[int] = None,
        part_number_marker: Optional[int] = None,
    ):
        """
        Lists object parts.
        """
        return self._object_part(
            object_store_id=object_store_id,
            object_key=object_key,
            max_parts=max_parts,
            part_number_marker=part_number_marker,
        )

    def object_parts(self, **kwargs):
        return self.object_part(**kwargs)

    @abstractmethod
    def _object_store(self, **kwargs) -> models.ObjectStoreListResponse:
        pass

    def object_store(
        self,
        bucket_name: Optional[str] = None,
        access_key_id: Optional[str] = None,
        region_name: Optional[str] = None,
        endpoint_url: Optional[str] = None,
        note: Optional[str] = None,
        note_like: Optional[str] = None,
        disabled: Optional[bool] = None,
        offset: Optional[int] = 0,
        limit: Optional[int] = 100,
        order: Optional[str] = "created_at",
        sort: Optional[str] = "ASC",
        created_by: Optional[UUID] = None,
        updated_by: Optional[UUID] = None,
        deleted_by: Optional[UUID] = None,
        updated_by_null: Optional[bool] = None,
        deleted_by_null: Optional[bool] = None,
        updated_at_null: Optional[bool] = None,
        deleted_at_null: Optional[bool] = None,
        created_at_lte: Optional[datetime] = None,
        updated_at_lte: Optional[datetime] = None,
        deleted_at_lte: Optional[datetime] = None,
        created_at_gte: Optional[datetime] = None,
        updated_at_gte: Optional[datetime] = None,
        deleted_at_gte: Optional[datetime] = None,
    ):
        """
        Lists object stores.
        """
        return self._object_store(
            bucket_name=bucket_name,
            access_key_id=access_key_id,
            region_name=region_name,
            endpoint_url=endpoint_url,
            note=note,
            note_like=note_like,
            disabled=disabled,
            offset=offset,
            limit=limit,
            order=order,
            sort=sort,
            created_by=created_by,
            updated_by=updated_by,
            deleted_by=deleted_by,
            updated_by_null=updated_by_null,
            deleted_by_null=deleted_by_null,
            updated_at_null=updated_at_null,
            deleted_at_null=deleted_at_null,
            created_at_lte=created_at_lte,
            updated_at_lte=updated_at_lte,
            deleted_at_lte=deleted_at_lte,
            created_at_gte=created_at_gte,
            updated_at_gte=updated_at_gte,
            deleted_at_gte=deleted_at_gte,
        )

    def object_stores(self, **kwargs):
        return self.object_store(**kwargs)

    @abstractmethod
    def _query(self, **kwargs) -> models.QueryListResponse:
        pass

    def query(
        self,
        log_id: Optional[UUID] = None,
        name: Optional[str] = None,
        name_like: Optional[str] = None,
        note_like: Optional[str] = None,
        statement: Optional[str] = None,
        statement_like: Optional[str] = None,
        workflow_id: Optional[UUID] = None,
        workflow_id_null: Optional[bool] = None,
        workflow_context_filter: Optional[str] = None,
        state: Optional[str] = None,
        context_filter: Optional[str] = None,
        offset: Optional[int] = 0,
        limit: Optional[int] = 100,
        order: Optional[str] = "created_at",
        sort: Optional[str] = "ASC",
        created_by: Optional[UUID] = None,
        updated_by: Optional[UUID] = None,
        deleted_by: Optional[UUID] = None,
        updated_by_null: Optional[bool] = None,
        deleted_by_null: Optional[bool] = None,
        updated_at_null: Optional[bool] = None,
        deleted_at_null: Optional[bool] = None,
        created_at_lte: Optional[datetime] = None,
        updated_at_lte: Optional[datetime] = None,
        deleted_at_lte: Optional[datetime] = None,
        created_at_gte: Optional[datetime] = None,
        updated_at_gte: Optional[datetime] = None,
        deleted_at_gte: Optional[datetime] = None,
    ):
        """
        Lists queries.
        """
        return self._query(
            log_id=log_id,
            name=name,
            name_like=name_like,
            note_like=note_like,
            statement=statement,
            statement_like=statement_like,
            workflow_id=workflow_id,
            workflow_id_null=workflow_id_null,
            workflow_context_filter=workflow_context_filter,
            state=state,
            context_filter=context_filter,
            offset=offset,
            limit=limit,
            order=order,
            sort=sort,
            created_by=created_by,
            updated_by=updated_by,
            deleted_by=deleted_by,
            updated_by_null=updated_by_null,
            deleted_by_null=deleted_by_null,
            updated_at_null=updated_at_null,
            deleted_at_null=deleted_at_null,
            created_at_lte=created_at_lte,
            updated_at_lte=updated_at_lte,
            deleted_at_lte=deleted_at_lte,
            created_at_gte=created_at_gte,
            updated_at_gte=updated_at_gte,
            deleted_at_gte=deleted_at_gte,
        )

    def queries(self, **kwargs):
        return self.query(**kwargs)

    @abstractmethod
    def _record(self, **kwargs) -> models.RecordListResponse:
        pass

    def record(
        self,
        topic_id: UUID,
        log_id: Optional[UUID] = None,
        ingestion_id: Optional[UUID] = None,
        workflow_id: Optional[UUID] = None,
        workflow_id_null: Optional[bool] = None,
        state: Optional[str] = None,
        error_like: Optional[str] = None,
        note_like: Optional[str] = None,
        source: Optional[str] = None,
        query_data_filter: Optional[str] = None,
        context_filter: Optional[str] = None,
        altered: Optional[bool] = None,
        frequency: Optional[float] = None,
        timestamp_gt: Optional[int] = None,
        timestamp_lt: Optional[int] = None,
        timestamp_gte: Optional[int] = None,
        timestamp_lte: Optional[int] = None,
        data_length_gte: Optional[int] = None,
        data_length_lte: Optional[int] = None,
        data_offset_gte: Optional[int] = None,
        data_offset_lte: Optional[int] = None,
        chunk_compression: Optional[str] = None,
        chunk_offset_gte: Optional[int] = None,
        chunk_offset_lte: Optional[int] = None,
        chunk_length_gte: Optional[int] = None,
        chunk_length_lte: Optional[int] = None,
        include_auxiliary_data: Optional[bool] = False,
        include_raw_data: Optional[bool] = False,
        offset: Optional[int] = 0,
        limit: Optional[int] = 100,
        order: Optional[str] = "timestamp",
        sort: Optional[str] = "ASC",
        created_by: Optional[UUID] = None,
        updated_by: Optional[UUID] = None,
        deleted_by: Optional[UUID] = None,
        updated_by_null: Optional[bool] = None,
        deleted_by_null: Optional[bool] = None,
        updated_at_null: Optional[bool] = None,
        deleted_at_null: Optional[bool] = None,
        created_at_lte: Optional[datetime] = None,
        updated_at_lte: Optional[datetime] = None,
        deleted_at_lte: Optional[datetime] = None,
        created_at_gte: Optional[datetime] = None,
        updated_at_gte: Optional[datetime] = None,
        deleted_at_gte: Optional[datetime] = None,
    ):
        """
        Lists records.
        """
        return self._record(
            topic_id=topic_id,
            log_id=log_id,
            ingestion_id=ingestion_id,
            workflow_id=workflow_id,
            workflow_id_null=workflow_id_null,
            state=state,
            error_like=error_like,
            note_like=note_like,
            source=source,
            query_data_filter=query_data_filter,
            context_filter=context_filter,
            altered=altered,
            frequency=frequency,
            timestamp_gt=timestamp_gt,
            timestamp_lt=timestamp_lt,
            timestamp_gte=timestamp_gte,
            timestamp_lte=timestamp_lte,
            data_length_gte=data_length_gte,
            data_length_lte=data_length_lte,
            data_offset_gte=data_offset_gte,
            data_offset_lte=data_offset_lte,
            chunk_compression=chunk_compression,
            chunk_offset_gte=chunk_offset_gte,
            chunk_offset_lte=chunk_offset_lte,
            chunk_length_gte=chunk_length_gte,
            chunk_length_lte=chunk_length_lte,
            include_auxiliary_data=include_auxiliary_data,
            include_raw_data=include_raw_data,
            offset=offset,
            limit=limit,
            order=order,
            sort=sort,
            created_by=created_by,
            updated_by=updated_by,
            deleted_by=deleted_by,
            updated_by_null=updated_by_null,
            deleted_by_null=deleted_by_null,
            updated_at_null=updated_at_null,
            deleted_at_null=deleted_at_null,
            created_at_lte=created_at_lte,
            updated_at_lte=updated_at_lte,
            deleted_at_lte=deleted_at_lte,
            created_at_gte=created_at_gte,
            updated_at_gte=updated_at_gte,
            deleted_at_gte=deleted_at_gte,
        )

    def records(self, **kwargs):
        return self.record(**kwargs)

    @abstractmethod
    def _tag(self, **kwargs) -> models.TagListResponse:
        pass

    def tag(
        self,
        log_id: Optional[UUID] = None,
        label_id: Optional[UUID] = None,
        topic_id: Optional[UUID] = None,
        note: Optional[str] = None,
        note_like: Optional[str] = None,
        context_filter: Optional[str] = None,
        start_time_null: Optional[bool] = None,
        start_time_gte: Optional[int] = None,
        start_time_lte: Optional[int] = None,
        end_time_null: Optional[bool] = None,
        end_time_gte: Optional[int] = None,
        end_time_lte: Optional[int] = None,
        offset: Optional[int] = 0,
        limit: Optional[int] = 100,
        order: Optional[str] = "created_at",
        sort: Optional[str] = "ASC",
        created_by: Optional[UUID] = None,
        updated_by: Optional[UUID] = None,
        deleted_by: Optional[UUID] = None,
        updated_by_null: Optional[bool] = None,
        deleted_by_null: Optional[bool] = None,
        updated_at_null: Optional[bool] = None,
        deleted_at_null: Optional[bool] = None,
        created_at_lte: Optional[datetime] = None,
        updated_at_lte: Optional[datetime] = None,
        deleted_at_lte: Optional[datetime] = None,
        created_at_gte: Optional[datetime] = None,
        updated_at_gte: Optional[datetime] = None,
        deleted_at_gte: Optional[datetime] = None,
    ):
        """
        Lists tags.
        """
        return self._tag(
            label_id=label_id,
            log_id=log_id,
            topic_id=topic_id,
            note=note,
            note_like=note_like,
            context_filter=context_filter,
            start_time_null=start_time_null,
            start_time_gte=start_time_gte,
            start_time_lte=start_time_lte,
            end_time_null=end_time_null,
            end_time_gte=end_time_gte,
            end_time_lte=end_time_lte,
            offset=offset,
            limit=limit,
            order=order,
            sort=sort,
            created_by=created_by,
            updated_by=updated_by,
            deleted_by=deleted_by,
            updated_by_null=updated_by_null,
            deleted_by_null=deleted_by_null,
            updated_at_null=updated_at_null,
            deleted_at_null=deleted_at_null,
            created_at_lte=created_at_lte,
            updated_at_lte=updated_at_lte,
            deleted_at_lte=deleted_at_lte,
            created_at_gte=created_at_gte,
            updated_at_gte=updated_at_gte,
            deleted_at_gte=deleted_at_gte,
        )

    def tags(self, **kwargs):
        return self.tag(**kwargs)

    @abstractmethod
    def _topic(self, **kwargs) -> models.TopicListResponse:
        pass

    def topic(
        self,
        log_id: Optional[UUID] = None,
        group_id: Optional[UUID] = None,
        name: Optional[str] = None,
        name_like: Optional[str] = None,
        associated_topic_id: Optional[UUID] = None,
        latched: Optional[bool] = None,
        strict: Optional[bool] = None,
        locked: Optional[bool] = None,
        context_filter: Optional[str] = None,
        start_time_null: Optional[bool] = None,
        start_time_gte: Optional[int] = None,
        start_time_lte: Optional[int] = None,
        end_time_null: Optional[bool] = None,
        end_time_gte: Optional[int] = None,
        end_time_lte: Optional[int] = None,
        record_size_gte: Optional[int] = None,
        record_size_lte: Optional[int] = None,
        record_count_gte: Optional[int] = None,
        record_count_lte: Optional[int] = None,
        type_name: Optional[str] = None,
        type_name_like: Optional[str] = None,
        type_encoding: Optional[models.TypeEncoding] = None,
        type_data: Optional[str] = None,
        type_data_like: Optional[str] = None,
        type_schema_filter: Optional[str] = None,
        offset: Optional[int] = 0,
        limit: Optional[int] = 100,
        order: Optional[str] = "created_at",
        sort: Optional[str] = "ASC",
        created_by: Optional[UUID] = None,
        updated_by: Optional[UUID] = None,
        deleted_by: Optional[UUID] = None,
        updated_by_null: Optional[bool] = None,
        deleted_by_null: Optional[bool] = None,
        updated_at_null: Optional[bool] = None,
        deleted_at_null: Optional[bool] = None,
        created_at_lte: Optional[datetime] = None,
        updated_at_lte: Optional[datetime] = None,
        deleted_at_lte: Optional[datetime] = None,
        created_at_gte: Optional[datetime] = None,
        updated_at_gte: Optional[datetime] = None,
        deleted_at_gte: Optional[datetime] = None,
    ):
        """
        Lists topics.
        """
        return self._topic(
            group_id=group_id,
            name=name,
            name_like=name_like,
            log_id=log_id,
            associated_topic_id=associated_topic_id,
            latched=latched,
            strict=strict,
            locked=locked,
            context_filter=context_filter,
            start_time_null=start_time_null,
            start_time_gte=start_time_gte,
            start_time_lte=start_time_lte,
            end_time_null=end_time_null,
            end_time_gte=end_time_gte,
            end_time_lte=end_time_lte,
            record_size_gte=record_size_gte,
            record_size_lte=record_size_lte,
            record_count_gte=record_count_gte,
            record_count_lte=record_count_lte,
            type_name=type_name,
            type_name_like=type_name_like,
            type_encoding=type_encoding,
            type_data=type_data,
            type_data_like=type_data_like,
            type_schema_filter=type_schema_filter,
            offset=offset,
            limit=limit,
            order=order,
            sort=sort,
            created_by=created_by,
            updated_by=updated_by,
            deleted_by=deleted_by,
            updated_by_null=updated_by_null,
            deleted_by_null=deleted_by_null,
            updated_at_null=updated_at_null,
            deleted_at_null=deleted_at_null,
            created_at_lte=created_at_lte,
            updated_at_lte=updated_at_lte,
            deleted_at_lte=deleted_at_lte,
            created_at_gte=created_at_gte,
            updated_at_gte=updated_at_gte,
            deleted_at_gte=deleted_at_gte,
        )

    def topics(self, **kwargs):
        return self.topic(**kwargs)

    @abstractmethod
    def _workflow(self, **kwargs) -> models.WorkflowListResponse:
        pass

    def workflow(
        self,
        name: Optional[str] = None,
        name_like: Optional[str] = None,
        default: Optional[bool] = None,
        disabled: Optional[bool] = None,
        managed: Optional[bool] = None,
        context_schema_filter: Optional[str] = None,
        offset: Optional[int] = 0,
        limit: Optional[int] = 100,
        order: Optional[str] = "created_at",
        sort: Optional[str] = "ASC",
        created_by: Optional[UUID] = None,
        updated_by: Optional[UUID] = None,
        deleted_by: Optional[UUID] = None,
        updated_by_null: Optional[bool] = None,
        deleted_by_null: Optional[bool] = None,
        updated_at_null: Optional[bool] = None,
        deleted_at_null: Optional[bool] = None,
        created_at_lte: Optional[datetime] = None,
        updated_at_lte: Optional[datetime] = None,
        deleted_at_lte: Optional[datetime] = None,
        created_at_gte: Optional[datetime] = None,
        updated_at_gte: Optional[datetime] = None,
        deleted_at_gte: Optional[datetime] = None,
    ):
        """
        Lists workflows.
        """
        return self._workflow(
            name=name,
            name_like=name_like,
            default=default,
            disabled=disabled,
            managed=managed,
            context_schema_filter=context_schema_filter,
            offset=offset,
            limit=limit,
            order=order,
            sort=sort,
            created_by=created_by,
            updated_by=updated_by,
            deleted_by=deleted_by,
            updated_by_null=updated_by_null,
            deleted_by_null=deleted_by_null,
            updated_at_null=updated_at_null,
            deleted_at_null=deleted_at_null,
            created_at_lte=created_at_lte,
            updated_at_lte=updated_at_lte,
            deleted_at_lte=deleted_at_lte,
            created_at_gte=created_at_gte,
            updated_at_gte=updated_at_gte,
            deleted_at_gte=deleted_at_gte,
        )

    def workflows(self, **kwargs):
        return self.workflow(**kwargs)
