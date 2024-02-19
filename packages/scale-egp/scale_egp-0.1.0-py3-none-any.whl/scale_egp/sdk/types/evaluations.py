from __future__ import annotations

from datetime import datetime
from typing import Optional, Dict, Any, Union

from pydantic import Field

from scale_egp.sdk.enums import EvaluationStatus
from scale_egp.sdk.types.evaluation_configs import StudioEvaluationConfig
from scale_egp.utils.model_utils import Entity, BaseModel


class Evaluation(Entity):
    """
    A data model representing an evaluation.

    Attributes:
        id: The ID of the evaluation
        name: The name of the evaluation
        description: The description of the evaluation
        status: The status of the evaluation
        application_spec_id: The ID of the application spec that the evaluation is for
        evaluation_config: The evaluation config of the evaluation
        tags: The tags of the evaluation represented as a dictionary of key value pairs
        created_at: The time the evaluation was created
    """

    id: str
    name: str
    description: str
    status: EvaluationStatus
    application_spec_id: str
    evaluation_config: Union[StudioEvaluationConfig]
    tags: Optional[Dict[str, Any]] = None
    created_at: datetime


class EvaluationRequest(BaseModel):
    name: str
    description: str
    application_spec_id: str
    tags: Optional[Dict[str, Any]] = None
    evaluation_config: Union[StudioEvaluationConfig]
    account_id: Optional[str] = Field(
        description="Account to create knowledge base in. If you have access to more than one "
                    "account, you must specify an account_id"
    )
