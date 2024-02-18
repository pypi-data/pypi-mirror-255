import os
import json
from pathlib import Path
from typing import Any, Dict, Tuple, Type

from pydantic.fields import FieldInfo

from pydantic_settings import (
    BaseSettings,
    PydanticBaseSettingsSource,
    SettingsConfigDict,
)


class CommonConfig(BaseSettings):
    log_level: str = "INFO"
    log_as_json: bool = False
    log_to_file: bool = False
    config_path: str = "logqs-config.json"
    config_key: str | None = None

    @classmethod
    def settings_customise_sources(
        cls,
        settings_cls: Type[BaseSettings],
        init_settings: PydanticBaseSettingsSource,
        env_settings: PydanticBaseSettingsSource,
        dotenv_settings: PydanticBaseSettingsSource,
        file_secret_settings: PydanticBaseSettingsSource,
    ) -> Tuple[PydanticBaseSettingsSource, ...]:
        return (
            init_settings,
            JsonConfigSettingsSource(settings_cls),
            env_settings,
            dotenv_settings,
            file_secret_settings,
        )

    model_config = SettingsConfigDict(
        env_file=(".env.default", ".env", ".env.local", ".env.dev", ".env.prod"),
        env_prefix="LQS_",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )


class JsonConfigSettingsSource(PydanticBaseSettingsSource):
    def get_field_value(
        self, field: FieldInfo, field_name: str
    ) -> Tuple[Any, str, bool]:
        encoding = self.config.get("env_file_encoding")
        config_path = (
            self.settings_cls.model_fields["config_path"].default
            if self.settings_cls.model_fields.get("config_path")
            else "config.json"
        )
        if not os.path.exists(config_path):
            return None, field_name, False
        file_content_json = json.loads(Path(config_path).read_text(encoding))
        config_key = (
            self.settings_cls.model_fields["config_key"].default
            if self.settings_cls.model_fields.get("config_key")
            else None
        )
        if config_key:
            file_content_json = file_content_json.get(config_key)
        if not isinstance(file_content_json, dict):
            return None, field_name, False
        field_value = file_content_json.get(field_name)
        return field_value, field_name, False

    def prepare_field_value(
        self, field_name: str, field: FieldInfo, value: Any, value_is_complex: bool
    ) -> Any:
        return value

    def __call__(self) -> Dict[str, Any]:
        d: Dict[str, Any] = {}

        for field_name, field in self.settings_cls.model_fields.items():
            field_value, field_key, value_is_complex = self.get_field_value(
                field, field_name
            )
            field_value = self.prepare_field_value(
                field_name, field, field_value, value_is_complex
            )
            if field_value is not None:
                d[field_key] = field_value

        return d
