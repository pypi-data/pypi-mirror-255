from datetime import datetime
from typing import Optional
from pydantic import Field
from scale_egp.utils.model_utils import BaseModel, Entity

class ModelGroup(Entity):
    """
    Entity for grouping models which are tied to the base model. E.g.: gpt-4 can be a group containing all gpt-4 fine-tuned models

    Attributes:
        id: The unique identifier of the entity.
        name: The name of the group
        description: Description of the group
    """

    name: str
    description: str
    id: str = Field(..., description="The unique identifier of the entity.")
    created_at: datetime = Field(
        ..., description="The date and time when the entity was created in ISO format."
    )
    account_id: str = Field(..., description="The ID of the account that owns the given entity.")
    created_by_user_id: str = Field(..., description="The user who originally created the entity.")



class ModelGroupRequest(BaseModel):
    name: str
    description: Optional[str]
    account_id: str = Field(..., description="The ID of the account that owns the given entity.")
