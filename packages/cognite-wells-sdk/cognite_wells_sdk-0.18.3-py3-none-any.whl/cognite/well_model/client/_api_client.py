import json as _json
import logging
from collections.abc import Iterable
from json import JSONDecodeError
from typing import Any, Callable, Dict, List, NoReturn, Optional, Union

import requests.utils
from requests.structures import CaseInsensitiveDict

from cognite.well_model import __version__
from cognite.well_model.client._http_client import HTTPClient, HTTPClientConfig
from cognite.well_model.client.utils import _client_config
from cognite.well_model.client.utils.exceptions import CogniteAPIError

log = logging.getLogger(__name__)


class APIClient:
    def __init__(self, config: _client_config.ClientConfig, api_version: str = None, cognite_client=None):
        self._config = config
        self._api_version = api_version  # remove?
        self._cognite_client = cognite_client

        self._http_client_with_retry = HTTPClient(
            config=HTTPClientConfig(
                status_codes_to_retry={429, 502, 503, 504},
                backoff_factor=0.5,
                max_backoff_seconds=self._config.max_retry_backoff,
                max_retries_total=self._config.max_retries,
                max_retries_read=self._config.max_retries,
                max_retries_connect=self._config.max_retries,
                max_retries_status=self._config.max_retries,
            )
        )

    def delete(
        self, url_path: str, params: Optional[Dict[str, Any]] = None, headers: Optional[Dict[str, Any]] = None
    ) -> requests.Response:
        """Perform a DELETE request to an arbitrary path in the API."""
        return self._do_request("DELETE", url_path, params=params, headers=headers, timeout=self._config.timeout)

    def get(
        self, url_path: str, params: Optional[Dict[str, Any]] = None, headers: Optional[Dict[str, Any]] = None
    ) -> requests.Response:
        """Perform a GET request to an arbitrary path in the API."""
        return self._do_request("GET", url_path, params=params, headers=headers, timeout=self._config.timeout)

    def post(
        self,
        url_path: str,
        json: Optional[Any] = None,
        params: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, Any]] = None,
    ) -> requests.Response:
        """Perform a POST request to an arbitrary path in the API."""
        return self._do_request(
            "POST", url_path, json=json, headers=headers, params=params, timeout=self._config.timeout
        )

    def put(
        self, url_path: str, json: Optional[Dict[str, Any]] = None, headers: Optional[Dict[str, Any]] = None
    ) -> requests.Response:
        """Perform a PUT request to an arbitrary path in the API."""
        return self._do_request("PUT", url_path, json=json, headers=headers, timeout=self._config.timeout)

    def _do_request(self, method: str, url_path: str, **kwargs) -> requests.Response:
        if not url_path.startswith("/"):
            raise ValueError("URL path must start with '/'")
        base_url = self._get_base_url_with_base_path
        full_url = base_url + url_path

        json_payload = kwargs.get("json")
        headers = self._configure_headers(self._config.headers.copy())
        headers.update(kwargs.get("headers") or {})

        if json_payload:
            if isinstance(json_payload, str):
                kwargs["data"] = json_payload
            else:
                data = _json.dumps(json_payload)
                kwargs["data"] = data

        kwargs["headers"] = headers
        response: requests.Response = self._http_client_with_retry.request(method=method, url=full_url, **kwargs)
        if not self._status_is_valid(response.status_code):
            self._raise_API_error(response, payload=json_payload)
        return response

    def _configure_headers(self, additional_headers: Dict[str, str]) -> CaseInsensitiveDict:
        """http header, or, meta-information in addition to the actual data

        Args:
            additional_headers: pass additional information with an HTTP request or response
        Returns:
            A dictionary of case-insensitive key-value pairs
        """
        headers: CaseInsensitiveDict = CaseInsensitiveDict()
        headers.update(requests.utils.default_headers())
        if self._config.token is None:
            headers["api-key"] = self._config.api_key
        elif isinstance(self._config.token, str):
            headers["Authorization"] = "Bearer {}".format(self._config.token)
        elif isinstance(self._config.token, Callable):  # type: ignore
            headers["Authorization"] = "Bearer {}".format(self._config.token())
        else:
            raise TypeError("'token' must be str, Callable, or None.")
        headers["x-cdp-app"] = self._config.client_name
        headers["x-cdp-sdk"] = "CogniteWellsSDK:{}".format(__version__)
        headers["cdf-version"] = "20221206-beta"

        headers["content-type"] = "application/json"
        headers.update(additional_headers)
        return headers

    @property
    def _get_base_url_with_base_path(self) -> str:
        base_url: str = self._config.base_url
        return base_url

    @staticmethod
    def _status_is_valid(status_code: int) -> bool:
        """True if status is considered 2xx Success, else False"""
        return 200 <= status_code < 300

    @staticmethod
    def _sanitize_headers(headers: Optional[Dict]) -> None:
        if headers is None:
            return
        if "api-key" in headers:
            headers["api-key"] = "***"
        if "Authorization" in headers:
            headers["Authorization"] = "***"

    @staticmethod
    def _truncate(s: str, limit: int = 500) -> str:
        if len(s) > limit:
            return s[:limit] + "..."
        return s

    @staticmethod
    def _get_response_content_safe(res: requests.Response) -> str:
        try:
            return _json.dumps(res.json())
        except JSONDecodeError:
            pass

        try:
            return res.content.decode()
        except UnicodeDecodeError:
            pass

        return "<binary>"

    @staticmethod
    def _raise_API_error(res: requests.Response, payload: Union[Dict[Any, Any], str, None]) -> NoReturn:
        x_request_id = res.headers.get("X-Request-Id")
        code = res.status_code
        missing = None
        duplicated = None
        extra = {}
        try:
            error: Any = res.json()["error"]
            if isinstance(error, str):
                msg = error
            elif isinstance(error, Dict):
                msg = error["message"]
                missing = error.get("missing")
                duplicated = error.get("duplicated")
                for k, v in error.items():
                    if k not in ["message", "missing", "duplicated", "code"]:
                        extra[k] = v
            else:
                msg = res.content.decode("utf-8")
        except Exception:
            msg = res.content.decode("utf-8")

        error_details: Dict = {"X-Request-Id": x_request_id}
        if payload:
            error_details["payload"] = payload
        if missing:
            error_details["missing"] = missing
        if duplicated:
            error_details["duplicated"] = duplicated
        error_details["headers"] = res.request.headers.copy()
        APIClient._sanitize_headers(error_details["headers"])
        error_details["response_payload"] = APIClient._truncate(APIClient._get_response_content_safe(res))
        error_details["response_headers"] = res.headers

        if res.history:
            for res_hist in res.history:
                log.debug(
                    f"REDIRECT AFTER HTTP Error {res_hist.status_code}"
                    + f" {res_hist.request.method} {res_hist.request.url}: {res_hist.content.decode()}"
                )
        log.debug(f"HTTP Error {code} {res.request.method} {res.request.url}: {msg}", extra=error_details)

        raise CogniteAPIError(
            message=msg, code=code, x_request_id=x_request_id, missing=missing, duplicated=duplicated, extra=extra
        )

    @staticmethod
    def _reraise_API_error_with_successful_failed(
        error: CogniteAPIError,
        successful: Optional[List],
        failed: Optional[List],
    ) -> NoReturn:
        raise CogniteAPIError(
            message=error.message,
            code=error.code,
            x_request_id=error.x_request_id,
            missing=error.missing,
            duplicated=error.duplicated,
            successful=successful,
            failed=failed,
            extra=error.extra,
        )

    @staticmethod
    def process_by_chunks(
        input_list: Optional[List[Any]],
        function,
        chunk_size=1000,
        **kwargs,
    ) -> Optional[List[Any]]:
        result_list: Optional[List[Any]] = []
        for offset in range(0, len(input_list), chunk_size):
            slice_object = slice(offset, offset + chunk_size)
            try:
                result = function(input_list[slice_object], **kwargs)
                if result is None:
                    result_list = None
                elif isinstance(result, Iterable):
                    result_list.extend(result)
            except CogniteAPIError as error:
                APIClient._reraise_API_error_with_successful_failed(
                    error,
                    input_list[:offset],
                    input_list[offset:],
                )
        return result_list
