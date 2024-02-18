from __future__ import annotations

from typing import Optional

from pydantic import Field

from scale_egp.utils.model_utils import BaseModel, Entity


class ApplicationSpecRequest(BaseModel):
    name: str
    description: str
    account_id: Optional[str] = Field(
        description="Account to create application spec in. If you have access to more than one "
                    "account, you must specify an account_id"
    )


class ApplicationSpec(Entity):
    """
    A data model representing an Application Spec.

    Attributes:
        id: The ID of the application spec
        name: The name of the application
        description: The description of the application

    """

    id: str
    name: str
    description: str
