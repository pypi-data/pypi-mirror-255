import functools
import json
import logging

from typing import IO, TYPE_CHECKING, Any, Callable, Dict, Iterable, List, Optional, Union
from urllib.parse import urlencode, urljoin

from httpx import Client, Response, Timeout
from httpx._types import FileTypes
from scale_egp.exceptions import exception_from_response
from scale_egp.utils.model_utils import BaseModel


if TYPE_CHECKING:
    from scale_egp.sdk.client import EGPClient

DEFAULT_TIMEOUT = 60

ten_minutes = 60 * 10
long_timeout = Timeout(connect=ten_minutes, read=ten_minutes, write=ten_minutes, pool=ten_minutes)
CURL_DEFAULT_HEADERS = {"Content-Type": "application/json"}

curl_logger = logging.getLogger("curl_command_log")
curl_logger.setLevel(logging.INFO)


def handle_api_exceptions(func: Callable) -> Callable:
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        response = func(*args, **kwargs)
        if response.status_code != 200:
            raise exception_from_response(response)
        return response

    return wrapper


def log_curl_command(
    client: Client,
    method: str,
    url: str,
    additional_headers: Optional[Dict[str, str]] = None,
    request: Optional[Dict[str, Any]] = None,
):
    cmd_parts = (
        ["curl", f"-X {method}", url]
        + [
            f"-H '{name}: {value}'"
            for (name, value) in {
                **CURL_DEFAULT_HEADERS,
                **(additional_headers or {}),
                **client.headers,
            }.items()
        ]
        + ([f"-d '{json.dumps(request)}'"] if request is not None else [])
    )
    curl_logger.info(" ".join(cmd_parts))


class APIEngine:
    def __init__(self, api_client: "EGPClient"):
        self._api_client = api_client

    def _log_curl_command(
        self,
        method: str,
        url: str,
        additional_headers: Optional[Dict[str, str]] = None,
        request: Optional[Dict[str, Any]] = None,
        file: Optional[FileTypes] = None,
    ):
        # TODO: log file attachement command
        if self._api_client.log_curl_commands:
            log_curl_command(
                self._api_client.httpx_client, method, url, additional_headers, request
            )

    def _post(
        self,
        sub_path: str,
        request: Optional[Union[BaseModel, Dict]] = None,
        timeout: Optional[int] = None,
        file: Optional[FileTypes] = None,
    ) -> Response:
        request_json = None
        if request is not None:
            request_json = request if isinstance(request, dict) else request.dict()
        response = self._raw_post(
            sub_path=sub_path,
            request_json=request_json,
            timeout=timeout if timeout is not None else DEFAULT_TIMEOUT,
            file=file,
        )
        return response

    def _patch(
        self,
        sub_path: str,
        request: Optional[BaseModel] = None,
        timeout: Optional[int] = None,
    ) -> Response:
        response = self._raw_patch(
            sub_path=sub_path,
            request_json=request.dict() if request is not None else None,
            timeout=timeout if timeout is not None else DEFAULT_TIMEOUT,
        )
        return response

    def _post_stream(
        self,
        sub_path: str,
        request: Optional[BaseModel] = None,
        timeout: Optional[int] = None,
    ) -> Iterable[Dict[str, Any]]:
        response = self._raw_stream(
            sub_path=sub_path,
            request_json=request.dict() if request is not None else None,
            timeout=timeout if timeout is not None else DEFAULT_TIMEOUT,
        )
        with response as lines:
            for line in lines.iter_lines():
                if line.startswith("data: "):
                    event_json_str = line[len("data: ") :]
                    try:
                        yield json.loads(event_json_str)
                    except json.JSONDecodeError:
                        raise ValueError(f"Invalid JSON payload: {event_json_str}")

    def _post_batch(
        self,
        sub_path: str,
        request_batch: Optional[List[BaseModel]] = None,
        timeout: Optional[int] = None,
    ) -> Response:
        response = self._raw_post(
            sub_path=sub_path,
            request_json=[request.dict() for request in request_batch],
            timeout=timeout if timeout is not None else DEFAULT_TIMEOUT,
        )
        return response

    def _get(
        self,
        sub_path: str,
        query_params: Optional[Dict[str, str]] = None,
        timeout: Optional[int] = None,
    ) -> Response:
        response = self._raw_get(
            sub_path=sub_path,
            query_params=query_params,
            timeout=timeout if timeout is not None else DEFAULT_TIMEOUT,
        )
        return response

    def _patch(
        self,
        sub_path: str,
        request: Optional[BaseModel] = None,
        timeout: Optional[int] = None,
    ) -> Response:
        response = self._raw_patch(
            sub_path=sub_path,
            request_json=request.dict() if request is not None else None,
            timeout=timeout if timeout is not None else DEFAULT_TIMEOUT,
        )
        return response

    def _delete(
        self,
        sub_path: str,
        timeout: Optional[int] = None,
    ) -> Response:
        response = self._raw_delete(
            sub_path=sub_path,
            timeout=timeout if timeout is not None else DEFAULT_TIMEOUT,
        )
        return response

    @handle_api_exceptions
    def _raw_post(
        self,
        sub_path: str,
        request_json: Optional[Dict[str, Any]] = None,
        timeout: Optional[int] = None,
        additional_headers: Optional[Dict[str, str]] = None,
        file: Optional[FileTypes] = None,
    ) -> Response:
        url = urljoin(self._api_client.endpoint_url, sub_path)
        self._log_curl_command("POST", url, additional_headers, request_json, file)
        kwargs = {
            **self._universal_request_kwargs(
                timeout=timeout,
                additional_headers=additional_headers,
            ),
            "url": url,
        }
        if file:
            if request_json:
                kwargs["data"] = request_json
            # see: https://www.python-httpx.org/quickstart/#sending-multipart-file-uploads
            kwargs["files"] = {"file": file}
        else:
            kwargs["json"] = request_json
        response = self._api_client.httpx_client.post(**kwargs)
        return response

    def _raw_stream(
        self,
        sub_path: str,
        request_json: Optional[Dict[str, Any]] = None,
        timeout: Optional[int] = None,
        additional_headers: Optional[Dict[str, str]] = None,
        method: str = "POST",
    ):
        url = urljoin(self._api_client.endpoint_url, sub_path)
        self._log_curl_command("POST", url, additional_headers, request_json)
        return self._api_client.httpx_client.stream(
            method=method,
            url=url,
            json=request_json,
            timeout=timeout if timeout is not None else DEFAULT_TIMEOUT,
            headers={
                **(additional_headers if additional_headers is not None else {}),
            },
        )

    @handle_api_exceptions
    def _raw_get(
        self,
        sub_path: str,
        timeout: Optional[int] = None,
        query_params: Optional[Dict[str, str]] = None,
        additional_headers: Optional[Dict[str, str]] = None,
    ) -> Response:
        url = urljoin(self._api_client.endpoint_url, sub_path)
        self._log_curl_command(
            "GET",
            url if query_params is None else f"{url}?{urlencode(query_params)}",
            additional_headers,
        )
        response = self._api_client.httpx_client.get(
            url,
            params=query_params,
            **self._universal_request_kwargs(
                timeout=timeout,
                additional_headers=additional_headers,
            ),
        )
        return response

    @handle_api_exceptions
    def _raw_patch(
        self,
        sub_path: str,
        request_json: Optional[Dict[str, Any]] = None,
        timeout: Optional[int] = None,
        additional_headers: Optional[Dict[str, str]] = None,
    ) -> Response:
        url = urljoin(self._api_client.endpoint_url, sub_path)
        self._log_curl_command("PATCH", url, additional_headers, request_json)
        response = self._api_client.httpx_client.patch(
            url,
            json=request_json,
            **self._universal_request_kwargs(
                timeout=timeout,
                additional_headers=additional_headers,
            ),
        )
        return response

    @handle_api_exceptions
    def _raw_delete(
        self,
        sub_path: str,
        timeout: Optional[int] = None,
        additional_headers: Optional[Dict[str, str]] = None,
    ) -> Response:
        url = urljoin(self._api_client.endpoint_url, sub_path)
        self._log_curl_command("PATCH", url, additional_headers)
        response = self._api_client.httpx_client.delete(
            url=url,
            **self._universal_request_kwargs(
                timeout=timeout,
                additional_headers=additional_headers,
            ),
        )
        return response

    def _universal_request_kwargs(
        self,
        timeout: Optional[int] = None,
        additional_headers: Optional[Dict[str, str]] = None,
    ) -> Dict[str, Any]:
        return dict(
            timeout=timeout if timeout is not None else DEFAULT_TIMEOUT,
            headers={
                **(additional_headers if additional_headers is not None else {}),
            },
        )
