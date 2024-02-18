import re
from typing import Optional, Union, TypeVar, Generic, Type
from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

optional_field = Field(default=None, json_schema_extra=lambda x: x.pop("default"))


def optional_field_alt(description: str):
    return Field(
        default=None,
        json_schema_extra=lambda x: x.pop("default"),
        description=description,
    )


class EmptyModel(BaseModel):
    pass


T = TypeVar("T", bound="ResourceModel")


class ResourceModel(BaseModel, Generic[T]):
    # app: "RESTClient | Core | None" = None # TODO: prepend an underscore so Pydantic ignores this
    model_config = ConfigDict(from_attributes=True)

    @classmethod
    def _describe(cls, return_description: bool = False):
        description = f"{cls.__name__}:\n"
        model_field_items = cls.model_fields.items()

        # reorganize the fields so that the common fields are at the top
        top_fields = ("id", "timestamp")
        bottom_fields = (
            "created_at",
            "updated_at",
            "deleted_at",
            "created_by",
            "updated_by",
            "deleted_by",
        )
        model_field_items = sorted(
            model_field_items,
            key=lambda x: (
                0 if x[0] in top_fields else 1,
                1 if x[0] in bottom_fields else 0,
                x[0],
            ),
        )

        for field_name, field_info in model_field_items:
            if field_name in ResourceModel.model_fields:
                continue

            field_type = field_info.annotation
            if str(field_type).startswith("typing."):
                type_name = str(field_type)[7:]
            else:
                type_name = field_type.__name__
            type_name = re.sub(r"(\w+\.)+", "", type_name)

            field_title = f"{field_name} [{type_name}]"
            buffer_length = 38 - len(field_title)
            description += (
                f"{field_title}: {' ' * buffer_length}{field_info.description or ''}\n"
            )
        description = description[:-1]
        if return_description:
            return description
        else:
            print(description)

    _repr_fields = ("id", "name")

    def __repr__(self):
        model_name = self.__class__.__name__
        value = f"<{model_name} "
        for field_name in self._repr_fields:
            if field_name in self.model_fields:
                value += f"{field_name}={getattr(self, field_name)}, "
        value = value[:-2] + ">"
        return value

    @classmethod
    def set_app(cls, app):
        cls.app = app

    @classmethod
    def fetch(cls: Type[T], *args, **kwargs) -> T:
        id = None
        friendly_id = None
        parent_id = None
        if len(args) > 0:
            try:
                if type(args[0]) == UUID:
                    id = args[0]
                elif type(args[0]) == int:
                    id = int(args[0])
                else:
                    id = UUID(args[0])
            except ValueError:
                friendly_id = args[0]
            if len(args) > 1:
                try:
                    if type(args[1]) == UUID:
                        parent_id = args[1]
                    else:
                        parent_id = UUID(args[1])
                except ValueError:
                    raise ValueError(
                        "Second argument must be the UUID of the parent resource."
                    )

        if "id" in kwargs:
            id = kwargs["id"]

        if id is not None:
            fetch_method = getattr(cls.app.fetch, cls.__name__.lower())
            if parent_id is not None:
                return fetch_method(id, parent_id, **kwargs).data
            else:
                return fetch_method(id, **kwargs).data
        else:
            list_method = getattr(cls.app.list, cls.__name__.lower())

            list_args = {
                "order": "created_at",
                "sort": "desc",
                "limit": 1,
            }
            list_args.update(kwargs)
            if friendly_id is not None:
                fields = cls._repr_fields.default
                if len(fields) < 2:
                    raise Exception(f"Cannot fetch {cls.__name__} without it's ID.")
                list_args[fields[1]] = friendly_id

            if parent_id is not None:
                list_res = list_method(parent_id, **list_args)
            else:
                list_res = list_method(**list_args)
            if list_res.count == 0:
                raise ValueError(f"No {cls.__name__} found.")
            elif list_res.count > 1:
                try:
                    cls.app.warn(f"Multiple {cls.__name__}s ({list_res.count}) found.")
                except AttributeError:
                    pass
            return list_res.data[0]

    @classmethod
    def first(cls: Type[T], **kwargs) -> T:
        kwargs["order"] = kwargs.get("order", "created_at")
        kwargs["sort"] = kwargs.get("sort", "asc")
        kwargs["limit"] = 1
        return cls.list(**kwargs)[0]

    @classmethod
    def list(cls: Type[T], **kwargs) -> list[T]:
        list_method = getattr(cls.app.list, cls.__name__.lower())
        return list_method(**kwargs).data

    @classmethod
    def create(cls: Type[T], **kwargs) -> T:
        create_method = getattr(cls.app.create, cls.__name__.lower())
        return create_method(**kwargs).data

    def update(self, **kwargs) -> T:
        # get the class name and convert it to snake case
        class_name = self.__class__.__name__.lower()
        update_method = getattr(self.app.update, class_name)
        updated_resource = update_method(self.id, data=kwargs).data
        for field, value in updated_resource.dict().items():
            # check that the field is a pydantic field
            if field in self.model_fields:
                # set the value of the field
                setattr(self, field, value)
        return self

    @classmethod
    def delete(cls, **kwargs) -> None:
        delete_method = getattr(cls.app.delete, cls.__name__.lower())
        return delete_method(**kwargs)

    @classmethod
    def fetch_or_create(cls, **kwargs):
        try:
            return cls.fetch(**kwargs)
        except Exception:
            return cls.create(**kwargs)

    def refresh(self):
        refreshed_resource = self.fetch(self.id)
        for field, value in refreshed_resource.model_dump().items():
            if field in self.model_fields:
                setattr(self, field, value)
        return self


class CommonModel(ResourceModel[T]):
    id: UUID = Field(..., description="The ID of the resource.")

    created_at: datetime = Field(
        ..., description="The creation timestamp of the resource."
    )
    updated_at: Optional[datetime] = Field(
        ..., description="The last update timestamp of the resource."
    )
    deleted_at: Optional[datetime] = Field(
        ..., description="The deletion timestamp of the resource."
    )
    created_by: Optional[UUID] = Field(
        ..., description="The ID of the user who created the resource."
    )
    updated_by: Optional[UUID] = Field(
        ..., description="The ID of the user who last updated the resource."
    )
    deleted_by: Optional[UUID] = Field(
        ..., description="The ID of the user who deleted the resource."
    )


class TimeSeriesModel(ResourceModel[T]):
    timestamp: int = Field(..., description="The timestamp of the resource.")

    created_at: datetime = Field(
        ..., description="The creation timestamp of the resource."
    )
    updated_at: Optional[datetime] = Field(
        ..., description="The last update timestamp of the resource."
    )
    deleted_at: Optional[datetime] = Field(
        ..., description="The deletion timestamp of the resource."
    )
    created_by: Optional[UUID] = Field(
        ..., description="The ID of the user who created the resource."
    )
    updated_by: Optional[UUID] = Field(
        ..., description="The ID of the user who last updated the resource."
    )
    deleted_by: Optional[UUID] = Field(
        ..., description="The ID of the user who deleted the resource."
    )


class PaginationModel(BaseModel):
    offset: int
    limit: int
    order: str
    sort: str
    count: int


class PatchOperation(BaseModel):
    op: str
    path: str
    value: Optional[Union[str, int, float, bool, dict, list, None]]


class JSONFilter(BaseModel):
    var: str
    op: str
    val: Union[str, int, float, bool, list, None]
