from __future__ import annotations

from datetime import datetime
from typing import Optional

from pydantic import Field

from scale_egp.sdk.enums import TestCaseSchemaType
from scale_egp.utils.model_utils import Entity, BaseModel


class EvaluationDataset(Entity):
    """
    A data model representing an evaluation dataset.

    Attributes:
        name: The name of the evaluation dataset
        schema_type: The schema type of the evaluation dataset
        id: The ID of the evaluation dataset
        created_at: The time the evaluation dataset was created
        updated_at: The time the evaluation dataset was last updated
        account_id: The ID of the account that owns the evaluation dataset
        created_by_user_id: The ID of the user that created the evaluation dataset
        version_num: The version number of the evaluation dataset

    """

    name: str
    schema_type: TestCaseSchemaType
    id: str
    created_at: datetime
    updated_at: datetime
    account_id: str
    created_by_user_id: str
    version_num: Optional[int] = None


class EvaluationDatasetRequest(BaseModel):
    name: str
    schema_type: TestCaseSchemaType
    account_id: Optional[str] = Field(
        description="Account to create knowledge base in. If you have access to more than one "
                    "account, you must specify an account_id"
    )


class EvaluationDatasetVersionRequest(BaseModel):
    account_id: str = Field(..., description="The ID of the account that owns the given entity.")


class EvaluationDatasetVersion(Entity):
    num: int
    evaluation_dataset_id: str
    id: str
    created_at: datetime
    account_id: str
    created_by_user_id: str
