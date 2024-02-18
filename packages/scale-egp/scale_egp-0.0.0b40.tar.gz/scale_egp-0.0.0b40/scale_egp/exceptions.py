"""
TODO: module docstring
"""
# Based on packages/egp-api-backend/egp_api_backend/server/internal/exceptions.py
import json
from typing import Optional
import httpx


class EGPException(Exception):
    """
    General EGP SDK exception.
    """

    message: str
    code: int = 500

    def __init__(self, message: str, code: Optional[int] = None):
        self.message = message
        if code is not None:
            self.code = code

    def __str__(self):
        return self.message

    def __repr__(self):
        return f"{self.__class__.__name__}: {self.message}"


class UnsupportedException(EGPException):
    """
    Raised when an unsupported operation is attempted
    """

    code = 400


class ItemDoesNotExist(EGPException):
    """
    Raised when a query expects one row but finds none
    """

    code = 404


def exception_from_response(response: httpx.Response) -> Exception:
    """
    TODO: docstring
    """
    # TODO: raise useful exceptions
    # 404: not found
    # 403: no permission
    # 422: server-side pydantic validation error
    cls = EGPException
    if response.status_code == 404:
        cls = ItemDoesNotExist
    body = response.content.decode("utf-8")
    if body.startswith("{"):  # assume JSON
        try:
            parsed_body = json.loads(body)
            body = parsed_body["detail"]
        except Exception:  # pylint: disable=broad-exception-caught
            pass
    return cls(body, response.status_code)
