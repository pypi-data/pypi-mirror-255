from typing import List
from pydantic import BaseModel
from httpx import Client
from scale_egp.utils.api_utils import log_curl_command as log_curl


class UserRole(BaseModel):
    role: str
    account_id: str


class UserInfoResponse(BaseModel):
    id: str
    first_name: str
    last_name: str
    email: str
    accounts: List[UserRole]


def get_user_info(
    httpx_client: Client, endpoint_url: str, log_curl_command: bool = False
) -> UserInfoResponse:
    full_url = f"{endpoint_url}user-info"
    if log_curl_command:
        log_curl(httpx_client, "GET", full_url)
    response = httpx_client.get(full_url)
    return UserInfoResponse.parse_obj(response.json())
