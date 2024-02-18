from typing import Optional, TYPE_CHECKING
import requests

import time
import json
import base64
import pprint
import decimal
from datetime import datetime, date
from uuid import UUID

if TYPE_CHECKING:
    from lqs.client import RESTClient

from lqs.common import exceptions


class LogQSEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, UUID):
            return obj.hex

        if isinstance(obj, (datetime, date)):
            return obj.isoformat()

        if isinstance(obj, bytes):
            return obj.decode("utf-8")

        if isinstance(obj, decimal.Decimal):
            return float(obj)

        return json.JSONEncoder.default(self, obj)


def output_decorator(func):
    def wrapper(*args, **kwargs):
        if args[0]._pretty:
            return pprint.pprint(func(*args, **kwargs))
        return func(*args, **kwargs)

    return wrapper


class RESTInterface:
    service: str

    def __init__(self, app: "RESTClient"):
        self.app = app
        if self.app.http_client is None:
            self._client = requests
            self._use_content = False
        else:
            self._client = self.app.http_client
            self._use_content = True

    def _get_headers(self, url=None):
        headers = {
            "Content-Type": "application/json",
        }

        api_key_id = self.app.config.api_key_id
        api_key_secret = self.app.config.api_key_secret
        if url is not None and "/apps/dsm/api" in url:
            if (
                self.app.config.dsm_api_key_id is not None
                and self.app.config.dsm_api_key_secret is not None
            ):
                self.app.debug("Using DSM API Key")
                api_key_id = self.app.config.dsm_api_key_id
                api_key_secret = self.app.config.dsm_api_key_secret

        if api_key_id is not None and api_key_secret is not None:
            headers["Authorization"] = "Bearer " + base64.b64encode(
                bytes(
                    f"{api_key_id}:{api_key_secret}",
                    "utf-8",
                )
            ).decode("utf-8")

        headers.update(self.app.config.additional_headers)
        return headers

    def _get_url_param_string(self, args, exclude=[]):
        url_params = ""
        for key, value in args.items():
            if value is not None and key not in ["self"] + exclude:
                if type(value) == dict or type(value) == list:
                    value = json.dumps(value, cls=LogQSEncoder)
                url_params += f"&{key}={value}"
        if len(url_params) > 0:
            url_params = "?" + url_params[1:]
        return url_params

    def _get_payload_data(self, args, exclude=[]):
        payload = {}
        for key, value in args.items():
            if value is not None and key not in ["self"] + exclude:
                payload[key] = value
        return payload

    def _handle_response_data(self, response: requests.Response):
        if response.status_code == 204:
            return

        content_type = response.headers.get("content-type")
        if content_type == "application/json":
            try:
                response_data = response.json()
            except json.decoder.JSONDecodeError:
                raise Exception(f"Error: {response.text}")
        elif content_type == "text/plain":
            response_data = response.text
        else:
            response_data = response.content

        try:
            response_ok = response.ok
        except AttributeError:
            # the TestClient from starlette does not have an ok attribute
            response_ok = response.is_success

        if response_ok:
            return response_data
        else:
            response_message = response_data
            if "message" in response_data:
                response_message = response_data["message"]
            if response.status_code == 401:
                raise exceptions.UnauthorizedException(msg=response_message)
            elif response.status_code == 403:
                raise exceptions.ForbiddenException(msg=response_message)
            elif response.status_code == 404:
                raise exceptions.NotFoundException(msg=response_message)
            elif response.status_code == 408:
                raise exceptions.TimeoutException(msg=response_message)
            elif response.status_code == 409:
                raise exceptions.ConflictException(msg=response_message)
            elif response.status_code == 423:
                raise exceptions.LockedException(msg=response_message)
            elif response.status_code == 500:
                raise exceptions.InternalServerErrorException(msg=response_message)
            raise Exception(response_message)

    def _handle_retries(self, func, retry_count=None):
        if retry_count is None:
            retry_count = self.app.config.retry_count
        for i in range(retry_count + 1):
            try:
                return func()
            except Exception as e:
                if not self.app.config.retry_aggressive:
                    # check if the error is one of our expected exceptions,
                    # i.e., an error that probably won't be resolved by retrying
                    lqs_expected_exceptions = [
                        exceptions.UnauthorizedException,
                        exceptions.ForbiddenException,
                        exceptions.NotFoundException,
                        exceptions.ConflictException,
                        exceptions.LockedException,
                    ]
                    for exception in lqs_expected_exceptions:
                        if isinstance(e, exception):
                            raise e
                if retry_count > 0 and i < retry_count:
                    # exponential backoff
                    backoff = self.app.config.retry_delay * (2**i)
                    self.app.error(f"Error: {e}")
                    self.app.info(f"Retrying in {backoff} seconds")
                    time.sleep(backoff)
                else:
                    raise e
        raise Exception("Error: Max retries exceeded")

    def _get_url(self, resource_path):
        path_prefix = f"/{self.service}/api"
        datastore_id = self.app.get_datastore_id()
        if self.service == "lqs" and datastore_id is not None:
            path_prefix = f"/{self.service}/{datastore_id}/api"

        url = self.app.config.api_url or ""
        url += self.app.config.api_endpoint_prefix or ""
        url += path_prefix + "/"
        url += resource_path
        return url

    def _head_resource(self, resource_path):
        url = self._get_url(resource_path)
        if self.app.config.dry_run:
            self.app.info(f"(Dry Run) HEAD {url}")
            return {}

        def make_request():
            r = self._client.head(
                url,
                headers=self._get_headers(url=url),
                timeout=self.app.config.api_request_timeout,
            )
            response_data = self._handle_response_data(r)
            if isinstance(response_data, (dict, list)):
                return response_data
            else:
                raise Exception("Error: HEAD request returned non-JSON data")

        return self._handle_retries(make_request)

    def _get_resource(
        self,
        resource_path,
        expected_content_type: Optional[str] = "application/json",
        additional_headers=None,
        response_model=None,
    ):
        url = self._get_url(resource_path)
        if self.app.config.dry_run:
            self.app.info(f"(Dry Run) GET {url}")
            return {}

        def make_request():
            headers = self._get_headers(url=url)
            if additional_headers:
                headers = {**headers, **additional_headers}
            r = self._client.get(
                url,
                headers=headers,
                timeout=self.app.config.api_request_timeout,
            )
            response_data = self._handle_response_data(r)
            if expected_content_type == "application/json":
                if isinstance(response_data, (dict, list)):
                    if response_model:
                        return response_model(**response_data)
                    return response_data
                else:
                    raise Exception("Error: GET request returned non-JSON data")
            elif expected_content_type == "text/plain":
                if isinstance(response_data, str):
                    return response_data
                else:
                    raise Exception("Error: GET request returned non-string data")
            else:
                if isinstance(response_data, bytes):
                    return response_data
                else:
                    raise Exception(
                        f"Error: GET request returned non-bytes data: {response_data}"
                    )

        return self._handle_retries(make_request)

    def _create_resource(self, resource_path, data, response_model):
        url = self._get_url(resource_path)
        if self.app.config.dry_run:
            self.app.info(f"(Dry Run) POST {url}, {data}")
            return {}

        def make_request():
            if self._use_content:
                params = dict(
                    url=url,
                    content=json.dumps(data, cls=LogQSEncoder),
                    headers=self._get_headers(url=url),
                    timeout=self.app.config.api_request_timeout,
                )
            else:
                params = dict(
                    url=url,
                    data=json.dumps(data, cls=LogQSEncoder),
                    headers=self._get_headers(url=url),
                    timeout=self.app.config.api_request_timeout,
                )

            r = self._client.post(**params)  # type: ignore
            response_data = self._handle_response_data(r)
            if isinstance(response_data, (dict, list)):
                if response_model is None:
                    return response_data
                return response_model(**response_data)
            else:
                raise Exception("Error: POST request returned non-JSON data")

        return self._handle_retries(make_request)

    def _update_resource(self, resource_path, data, response_model):
        url = self._get_url(resource_path)
        if self.app.config.dry_run:
            self.app.info(f"(Dry Run) PATCH {url}, {data}")
            return {}

        def make_request():
            if self._use_content:
                params = dict(
                    url=url,
                    content=json.dumps(data, cls=LogQSEncoder),
                    headers=self._get_headers(url=url),
                    timeout=self.app.config.api_request_timeout,
                )
            else:
                params = dict(
                    url=url,
                    data=json.dumps(data, cls=LogQSEncoder),
                    headers=self._get_headers(url=url),
                    timeout=self.app.config.api_request_timeout,
                )
            r = self._client.patch(**params)  # type: ignore
            response_data = self._handle_response_data(r)
            if isinstance(response_data, (dict, list)):
                return response_model(**response_data)
            else:
                raise Exception("Error: PATCH request returned non-JSON data")

        return self._handle_retries(make_request)

    def _delete_resource(self, resource_path):
        url = self._get_url(resource_path)
        if self.app.config.dry_run:
            self.app.info(f"(Dry Run) DELETE {url}")
            return

        def make_request():
            r = self._client.delete(
                url,
                headers=self._get_headers(url=url),
                timeout=self.app.config.api_request_timeout,
            )
            response_data = self._handle_response_data(r)
            if response_data is not None:
                raise Exception(f"Error: DELETE request returned data: {response_data}")

        return self._handle_retries(make_request)
