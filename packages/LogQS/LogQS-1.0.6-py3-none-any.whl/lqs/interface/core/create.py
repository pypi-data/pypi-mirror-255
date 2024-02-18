from abc import abstractmethod
from typing import List, Optional
from uuid import UUID

from lqs.interface.base.create import CreateInterface as BaseCreateInterface
import lqs.interface.core.models as models


class CreateInterface(BaseCreateInterface):
    @abstractmethod
    def _digestion(self, **kwargs) -> models.DigestionDataResponse:
        pass

    def digestion(
        self,
        log_id: UUID,
        name: Optional[str] = None,
        note: Optional[str] = None,
        context: Optional[dict] = None,
        locked: Optional[bool] = False,
        workflow_id: Optional[UUID] = None,
        workflow_context: Optional[dict] = None,
        state: str = "ready",
    ):
        """
        Creates a digestion.

        Args:
            log_id: The ID of the log to which the digestion should be added.
            name (optional): The name of the digestion.
            context (optional): The context to use for the digestion.
            note (optional): A note about the digestion.
            locked (optional): Whether the digestion is locked. Defaults to False.
            workflow_id (optional): The ID of the workflow to use for the digestion.
            workflow_context (optional): The context to use for the workflow.
            state (optional): The state of the digestion. Defaults to "ready".
        Returns:
            A data response with the created digestion.
        """

        return self._digestion(
            log_id=log_id,
            name=name,
            note=note,
            context=context,
            locked=locked,
            workflow_id=workflow_id,
            workflow_context=workflow_context,
            state=state,
        )

    def _digestion_by_model(self, data: models.DigestionCreateRequest):
        return self.digestion(**data.model_dump())

    @abstractmethod
    def _digestion_part(self, **kwargs) -> models.DigestionPartDataResponse:
        pass

    def digestion_part(
        self,
        digestion_id: UUID,
        sequence: int,
        locked: Optional[bool] = False,
        workflow_id: Optional[UUID] = None,
        workflow_context: Optional[dict] = None,
        state: str = "ready",
        index: Optional[List[models.DigestionPartIndex]] = None,
    ):
        """
        Creates a digestion part.

        Args:
            digestion_id: The ID of the digestion to which the digestion part should be added.
            sequence: The sequence of the digestion part.
            locked (optional): Whether the digestion part is locked. Defaults to False.
            workflow_id (optional): The ID of the workflow to use for the digestion part.
            workflow_context (optional): The context to use for the workflow.
            state (optional): The state of the digestion part. Defaults to "ready".
            index (optional): The index of the digestion part.
        Returns:
            A data response with the created digestion part.
        """
        return self._digestion_part(
            digestion_id=digestion_id,
            sequence=sequence,
            locked=locked,
            workflow_id=workflow_id,
            workflow_context=workflow_context,
            state=state,
            index=index,
        )

    def _digestion_part_by_model(
        self, digestion_id: UUID, data: models.DigestionPartCreateRequest
    ):
        return self.digestion_part(digestion_id=digestion_id, **data.model_dump())

    @abstractmethod
    def _digestion_topic(self, **kwargs) -> models.DigestionTopicDataResponse:
        pass

    def digestion_topic(
        self,
        digestion_id: UUID,
        topic_id: UUID,
        start_time: Optional[int] = None,
        end_time: Optional[int] = None,
        frequency: Optional[float] = None,
        query_data_filter: Optional[dict] = None,
        context_filter: Optional[dict] = None,
    ):
        """
        Creates a digestion topic.

        Args:
            digestion_id: The ID of the digestion to which the digestion topic should be added.
            topic_id: The ID of the topic to be digested.
            start_time (optional): The start time of the digestion topic.
            end_time (optional): The end time of the digestion topic.
            frequency (optional): The frequency of the digestion topic.
            query_data_filter (optional): The data filter of the digestion topic.
            context_filter (optional): The context filter of the digestion topic.
        Returns:
            A data response with the created digestion topic.
        """
        return self._digestion_topic(
            digestion_id=digestion_id,
            topic_id=topic_id,
            start_time=start_time,
            end_time=end_time,
            frequency=frequency,
            query_data_filter=query_data_filter,
            context_filter=context_filter,
        )

    def _digestion_topic_by_model(
        self, digestion_id: UUID, data: models.DigestionTopicCreateRequest
    ):
        return self.digestion_topic(digestion_id=digestion_id, **data.model_dump())

    @abstractmethod
    def _group(self, **kwargs) -> models.GroupDataResponse:
        pass

    def group(
        self,
        name: str,
        note: Optional[str] = None,
        context: Optional[dict] = None,
        locked: Optional[bool] = False,
        default_workflow_id: Optional[UUID] = None,
    ):
        """
        Creates a group.

        Args:
            name: The name of the group.
            note (optional): A note about the group.
            context (optional): The context to use for the group.
            locked (optional): Whether the group is locked. Defaults to False.
            default_workflow_id (optional): The ID of the default workflow for the group.
        Returns:
            A data response with the created group.
        """
        return self._group(
            name=name,
            note=note,
            context=context,
            locked=locked,
            default_workflow_id=default_workflow_id,
        )

    def _group_by_model(self, data: models.GroupCreateRequest):
        return self.group(**data.model_dump())

    @abstractmethod
    def _hook(self, **kwargs) -> models.HookDataResponse:
        pass

    def hook(
        self,
        workflow_id: UUID,
        trigger_process: str,
        trigger_state: str,
        name: Optional[str] = None,
        note: Optional[str] = None,
        context: Optional[dict] = None,
        managed: Optional[bool] = False,
        disabled: Optional[bool] = False,
        uri: Optional[str] = None,
        secret: Optional[str] = None,
    ):
        """
        Creates a hook.

        Args:
            workflow_id: The ID of the workflow to which the hook should be added.
            trigger_process: The process to trigger.
            trigger_state: The state to trigger.
            name (optional): The name of the hook.
            note (optional): A note about the hook.
            context (optional): The context to use for the hook.
            managed (optional): Whether the hook is managed. Defaults to False.
            disabled (optional): Whether the hook is disabled. Defaults to False.
            uri (optional): The URI of the hook.
            secret (optional): The secret of the hook.
        Returns:
            A data response with the created hook.
        """
        return self._hook(
            workflow_id=workflow_id,
            trigger_process=trigger_process,
            trigger_state=trigger_state,
            name=name,
            note=note,
            context=context,
            managed=managed,
            disabled=disabled,
            uri=uri,
            secret=secret,
        )

    def _hook_by_model(self, workflow_id: UUID, data: models.HookCreateRequest):
        return self.hook(workflow_id=workflow_id, **data.model_dump())

    @abstractmethod
    def _ingestion(self, **kwargs) -> models.IngestionDataResponse:
        pass

    def ingestion(
        self,
        log_id: UUID,
        name: Optional[str] = None,
        note: Optional[str] = None,
        context: Optional[dict] = None,
        object_store_id: Optional[UUID] = None,
        object_key: Optional[str] = None,
        locked: Optional[bool] = False,
        workflow_id: Optional[UUID] = None,
        workflow_context: Optional[dict] = None,
        state: str = "ready",
    ):
        """
        Creates an ingestion.

        Args:
            log_id: The ID of the log to which the ingestion should be added.
            name (optional): The name of the ingestion.
            note (optional): A note about the ingestion.
            context (optional): The context to use for the ingestion.
            object_store_id (optional): The ID of the object store to use for the ingestion.
            object_key (optional): The key of the object to use for the ingestion.
            locked (optional): Whether the ingestion is locked. Defaults to False.
            workflow_id (optional): The ID of the workflow to use for the ingestion.
            workflow_context (optional): The context to use for the workflow.
            state (optional): The state of the ingestion. Defaults to "ready".
        Returns:
            A data response with the created ingestion.
        """
        return self._ingestion(
            log_id=log_id,
            name=name,
            note=note,
            context=context,
            object_store_id=object_store_id,
            object_key=object_key,
            locked=locked,
            workflow_id=workflow_id,
            workflow_context=workflow_context,
            state=state,
        )

    def _ingestion_by_model(self, data: models.IngestionCreateRequest):
        return self.ingestion(**data.model_dump())

    @abstractmethod
    def _ingestion_part(self, **kwargs) -> models.IngestionPartDataResponse:
        pass

    def ingestion_part(
        self,
        ingestion_id: UUID,
        sequence: int,
        source: Optional[str] = None,
        locked: Optional[bool] = False,
        workflow_id: Optional[UUID] = None,
        workflow_context: Optional[dict] = None,
        state: str = "ready",
        index: Optional[List[models.IngestionPartIndex]] = None,
    ):
        """
        Creates an ingestion part.

        Args:
            ingestion_id: The ID of the ingestion to which the ingestion part should be added.
            sequence: The sequence of the ingestion part.
            source (optional): The source of the ingestion part.
            locked (optional): Whether the ingestion part is locked. Defaults to False.
            workflow_id (optional): The ID of the workflow to use for the ingestion part.
            workflow_context (optional): The context to use for the workflow.
            state (optional): The state of the ingestion part. Defaults to "queued".
            index (optional): The index of the ingestion part.
        Returns:
            A data response with the created ingestion part.
        """
        return self._ingestion_part(
            ingestion_id=ingestion_id,
            sequence=sequence,
            source=source,
            locked=locked,
            workflow_id=workflow_id,
            workflow_context=workflow_context,
            state=state,
            index=index,
        )

    def _ingestion_part_by_model(
        self, ingestion_id: UUID, data: models.IngestionPartCreateRequest
    ):
        return self.ingestion_part(ingestion_id=ingestion_id, **data.model_dump())

    @abstractmethod
    def _label(self, **kwargs) -> models.LabelDataResponse:
        pass

    def label(self, value: str, note: Optional[str] = None):
        """
        Creates a label.

        Args:
            value: The value of the label.
            note (optional): A note about the label.
        Returns:
            A data response with the created label.
        """
        return self._label(
            value=value,
            note=note,
        )

    def _label_by_model(self, data: models.LabelCreateRequest):
        return self.label(**data.model_dump())

    @abstractmethod
    def _log(self, **kwargs) -> models.LogDataResponse:
        pass

    def log(
        self,
        group_id: UUID,
        name: str,
        note: Optional[str] = None,
        context: Optional[dict] = None,
        locked: Optional[bool] = False,
        default_workflow_id: Optional[UUID] = None,
    ):
        """
        Creates a log.

        Args:
            group_id: The ID of the group to which the log should be added.
            name: The name of the log.
            note (optional): A note about the log.
            context (optional): The context to use for the log.
            locked (optional): Whether the log is locked. Defaults to False.
            default_workflow_id (optional): The ID of the default workflow for the log.
        Returns:
            A data response with the created log.
        """
        return self._log(
            group_id=group_id,
            name=name,
            note=note,
            context=context,
            locked=locked,
            default_workflow_id=default_workflow_id,
        )

    def _log_by_model(self, data: models.LogCreateRequest):
        return self.log(**data.model_dump())

    @abstractmethod
    def _log_object(self, **kwargs) -> models.ObjectDataResponse:
        pass

    def log_object(
        self,
        key: str,
        log_id: UUID,
        content_type: Optional[str] = None,
    ):
        """
        Creates a log object.

        Args:
            key: The key of the log object.
            log_id: The ID of the log to which the log object should be added.
            content_type (optional): The content type of the log object.
        Returns:
            A data response with the created log object.
        """
        return self._log_object(
            key=key,
            log_id=log_id,
            content_type=content_type,
        )

    def _log_object_by_model(self, log_id: UUID, data: models.ObjectCreateRequest):
        return self.log_object(log_id=log_id, **data.model_dump())

    @abstractmethod
    def _log_object_part(self, **kwargs) -> models.ObjectPartDataResponse:
        pass

    def log_object_part(
        self,
        object_key: str,
        size: int,
        log_id: UUID,
        part_number: Optional[int] = None,
    ):
        """
        Creates a log object part.

        Args:
            object_key: The key of the log object to which the log object part should be added.
            size: The size of the log object part.
            log_id: The ID of the log to which the log object part should be added.
            part_number (optional): The part number of the log object part.
        Returns:
            A data response with the created log object part.
        """
        return self._log_object_part(
            object_key=object_key,
            log_id=log_id,
            part_number=part_number,
            size=size,
        )

    def _log_object_part_by_model(
        self, object_key: str, log_id: UUID, data: models.ObjectPartCreateRequest
    ):
        return self.log_object_part(
            object_key=object_key, log_id=log_id, **data.model_dump()
        )

    @abstractmethod
    def _object(self, **kwargs) -> models.ObjectDataResponse:
        pass

    def object(
        self,
        key: str,
        object_store_id: UUID,
        content_type: Optional[str] = None,
    ):
        """
        Creates an object.

        Args:
            key: The key of the object.
            object_store_id: The ID of the object store to which the object should be added.
            content_type (optional): The content type of the object.
        Returns:
            A data response with the created object.
        """
        return self._object(
            key=key,
            object_store_id=object_store_id,
            content_type=content_type,
        )

    def _object_by_model(self, object_store_id: UUID, data: models.ObjectCreateRequest):
        return self.object(object_store_id=object_store_id, **data.model_dump())

    @abstractmethod
    def _object_part(self, **kwargs) -> models.ObjectPartDataResponse:
        pass

    def object_part(
        self,
        object_key: str,
        size: int,
        object_store_id: UUID,
        part_number: Optional[int] = None,
    ):
        """
        Creates an object part.

        Args:
            object_key: The key of the object to which the object part should be added.
            size: The size of the object part.
            object_store_id: The ID of the object store to which the object part should be added.
            part_number (optional): The part number of the object part.
        Returns:
            A data response with the created object part.
        """
        return self._object_part(
            object_key=object_key,
            object_store_id=object_store_id,
            part_number=part_number,
            size=size,
        )

    def _object_part_by_model(
        self,
        object_key: str,
        object_store_id: UUID,
        data: models.ObjectPartCreateRequest,
    ):
        return self.object_part(
            object_key=object_key, object_store_id=object_store_id, **data.model_dump()
        )

    @abstractmethod
    def _object_store(self, **kwargs) -> models.ObjectStoreDataResponse:
        pass

    def object_store(
        self,
        bucket_name: str,
        access_key_id: Optional[str] = None,
        secret_access_key: Optional[str] = None,
        region_name: Optional[str] = None,
        endpoint_url: Optional[str] = None,
        note: Optional[str] = None,
        context: Optional[dict] = None,
        disabled: Optional[bool] = False,
    ):
        """
        Creates an object store.

        Args:
            bucket_name: The name of the bucket.
            access_key_id (optional): The access key ID of the object store.
            secret_access_key (optional): The secret access key of the object store.
            region_name (optional): The region name of the object store.
            endpoint_url (optional): The endpoint URL of the object store.
            note (optional): A note about the object store.
            context (optional): The context to use for the object store.
            disabled (optional): Whether the object store is disabled. Defaults to False.
        Returns:
            A data response with the created object store.
        """
        return self._object_store(
            bucket_name=bucket_name,
            access_key_id=access_key_id,
            secret_access_key=secret_access_key,
            region_name=region_name,
            endpoint_url=endpoint_url,
            note=note,
            context=context,
            disabled=disabled,
        )

    def _object_store_by_model(self, data: models.ObjectStoreCreateRequest):
        return self.object_store(**data.model_dump())

    @abstractmethod
    def _query(self, **kwargs) -> models.QueryDataResponse:
        pass

    def query(
        self,
        log_id: UUID,
        name: Optional[str] = None,
        note: Optional[str] = None,
        context: Optional[dict] = None,
        statement: Optional[str] = None,
        parameters: Optional[dict] = None,
    ):
        """
        Creates a query.

        Args:
            log_id: The ID of the log to which the query should be added.
            name (optional): The name of the query.
            note (optional): A note about the query.
            context (optional): The context to use for the query.
            statement (optional): The statement of the query.
            parameters (optional): The parameters of the query.
        Returns:
            A data response with the created query.
        """
        return self._query(
            log_id=log_id,
            name=name,
            note=note,
            context=context,
            statement=statement,
            parameters=parameters,
        )

    def _query_by_model(self, log_id: UUID, data: models.QueryCreateRequest):
        return self.query(log_id=log_id, **data.model_dump())

    @abstractmethod
    def _record(self, **kwargs) -> models.RecordDataResponse:
        pass

    def record(
        self,
        timestamp: int,
        topic_id: UUID,
        note: Optional[str] = None,
        context: Optional[dict] = None,
        locked: Optional[bool] = False,
        query_data: Optional[dict] = None,
        auxiliary_data: Optional[dict] = None,
        data_offset: Optional[int] = None,
        data_length: Optional[int] = None,
        chunk_compression: Optional[str] = None,
        chunk_offset: Optional[int] = None,
        chunk_length: Optional[int] = None,
        source: Optional[str] = None,
    ):
        """
        Creates a record.

        Args:
            timestamp: The timestamp of the record.
            topic_id: The ID of the topic to which the record should be added.
            note (optional): A note about the record.
            context (optional): The context to use for the record.
            locked (optional): Whether the record is locked. Defaults to False.
            query_data (optional): A JSON representation of the record's message data which is queryable.
            auxiliary_data (optional): A JSON representation of the record's message data which is not queryable.

            data_offset (optional): The data offset of the record.
            data_length (optional): The data length of the record.
            chunk_compression (optional): The chunk compression of the record.
            chunk_offset (optional): The chunk offset of the record.
            chunk_length (optional): The chunk length of the record.
            source (optional): The source of the record.
        Returns:
            A data response with the created record.
        """
        return self._record(
            timestamp=timestamp,
            topic_id=topic_id,
            note=note,
            context=context,
            locked=locked,
            query_data=query_data,
            auxiliary_data=auxiliary_data,
            data_offset=data_offset,
            data_length=data_length,
            chunk_compression=chunk_compression,
            chunk_offset=chunk_offset,
            chunk_length=chunk_length,
            source=source,
        )

    def _record_by_model(self, topic_id: UUID, data: models.RecordCreateRequest):
        return self.record(topic_id=topic_id, **data.model_dump())

    @abstractmethod
    def _tag(self, **kwargs) -> models.TagDataResponse:
        pass

    def tag(
        self,
        label_id: UUID,
        log_id: UUID,
        topic_id: Optional[UUID] = None,
        note: Optional[str] = None,
        context: Optional[dict] = None,
        start_time: Optional[int] = None,
        end_time: Optional[int] = None,
    ):
        """
        Creates a tag.

        Args:
            label_id: The ID of the label to which the tag should be added.
            log_id: The ID of the log to which the tag should be added.
            topic_id (optional): The ID of the topic to which the tag should be added.
            note (optional): A note about the tag.
            context (optional): The context to use for the tag.
            start_time (optional): The start time of the tag.
            end_time (optional): The end time of the tag.
        Returns:
            A data response with the created tag.
        """
        return self._tag(
            label_id=label_id,
            log_id=log_id,
            topic_id=topic_id,
            note=note,
            context=context,
            start_time=start_time,
            end_time=end_time,
        )

    def _tag_by_model(self, log_id: UUID, data: models.TagCreateRequest):
        return self.tag(log_id=log_id, **data.model_dump())

    @abstractmethod
    def _topic(self, **kwargs) -> models.TopicDataResponse:
        pass

    def topic(
        self,
        log_id: UUID,
        name: str,
        note: Optional[str] = None,
        context: Optional[dict] = None,
        associated_topic_id: Optional[UUID] = None,
        locked: Optional[bool] = False,
        strict: Optional[bool] = False,
        type_name: Optional[str] = None,
        type_encoding: Optional[str] = None,
        type_data: Optional[str] = None,
        type_schema: Optional[dict] = None,
    ):
        """
        Creates a topic.

        Args:
            log_id: The ID of the log to which the topic should be added.
            name: The name of the topic.
            note (optional): A note about the topic.
            context (optional): The context to use for the topic.
            associated_topic_id (optional): The ID of the associated topic.
            locked (optional): Whether the topic is locked. Defaults to False.

            strict (optional): Whether the topic is strict. Defaults to False.
            type_name (optional): The type name of the topic.
            type_encoding (optional): The type encoding of the topic.
            type_data (optional): The type data of the topic.
            type_schema (optional): The type schema of the topic.
        Returns:
            A data response with the created topic.
        """
        return self._topic(
            log_id=log_id,
            name=name,
            note=note,
            context=context,
            associated_topic_id=associated_topic_id,
            locked=locked,
            strict=strict,
            type_name=type_name,
            type_encoding=type_encoding,
            type_data=type_data,
            type_schema=type_schema,
        )

    def _topic_by_model(self, data: models.TopicCreateRequest):
        return self.topic(**data.model_dump())

    @abstractmethod
    def _workflow(self, **kwargs) -> models.WorkflowDataResponse:
        pass

    def workflow(
        self,
        name: str,
        note: Optional[str] = None,
        context: Optional[dict] = None,
        default: Optional[bool] = False,
        disabled: Optional[bool] = False,
        managed: Optional[bool] = False,
        context_schema: Optional[dict] = None,
    ):
        """
        Creates a workflow.

        Args:
            name: The name of the workflow.
            note (optional): A note about the workflow.
            context (optional): The context to use for the workflow.

            default (optional): Whether the workflow is default. Defaults to False.
            disabled (optional): Whether the workflow is disabled. Defaults to False.
            managed (optional): Whether the workflow is managed. Defaults to False.
            context_schema (optional): The context schema of the workflow.
        Returns:
            A data response with the created workflow.
        """
        return self._workflow(
            name=name,
            note=note,
            context=context,
            default=default,
            disabled=disabled,
            managed=managed,
            context_schema=context_schema,
        )

    def _workflow_by_model(self, data: models.WorkflowCreateRequest):
        return self.workflow(**data.model_dump())
