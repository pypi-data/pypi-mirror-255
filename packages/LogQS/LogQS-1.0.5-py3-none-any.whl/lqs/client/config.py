from uuid import UUID
from lqs.common.config import CommonConfig


class RESTClientConfig(CommonConfig):
    api_key_id: UUID | None = None
    api_key_secret: str | None = None
    api_url: str | None = "https://api.logqs.com"
    api_endpoint_prefix: str = "/apps"
    dsm_api_key_id: UUID | None = None
    dsm_api_key_secret: str | None = None
    datastore_id: UUID | None = None

    pretty: bool = False
    verbose: bool = False
    log_level: str = "INFO"
    log_as_json: bool = False
    dry_run: bool = False
    retry_count: int = 2
    retry_delay: int = 5
    retry_aggressive: bool = False
    api_request_timeout: int = 60
    additional_headers: dict[str, str] = {}
