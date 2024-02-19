from typing import List

from scale_egp.utils.model_utils import BaseModel


class Account(BaseModel):
    id: str
    name: str


class UserRole(BaseModel):
    role: str
    account: Account


class UserInfoResponse(BaseModel):
    id: str
    first_name: str
    last_name: str
    email: str
    accounts: List[UserRole]
