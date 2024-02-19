from __future__ import annotations

from datetime import datetime
from typing import Optional

from pydantic import Field

from scale_egp.utils.model_utils import Entity, BaseModel


class StudioProject(Entity):
    """
    A data model representing a Studio project.

    Attributes:
        id: The ID of the Studio project
        name: The name of the Studio project
        description: The description of the Studio project
        created_at: The time the Studio project was created
    """

    id: str
    name: str
    description: str
    created_at: datetime


class StudioProjectRequest(BaseModel):
    name: str
    description: str
    studio_api_key: str
    account_id: Optional[str] = Field(
        description="Account to create knowledge base in. If you have access to more than one "
                    "account, you must specify an account_id"
    )
