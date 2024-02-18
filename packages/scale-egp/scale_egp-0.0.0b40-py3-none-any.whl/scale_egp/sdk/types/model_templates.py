from __future__ import annotations

from datetime import datetime
from typing import Optional

from pydantic import Field

from scale_egp.sdk.enums import ModelEndpointType, ModelType
from scale_egp.sdk.types.models import ParameterSchema
from scale_egp.utils.model_utils import Entity, BaseModel

from scale_egp.sdk.models.model_vendor_configuration import ModelVendorConfiguration


class ModelTemplate(Entity):
    """
    This is a template for types of models that can be quickly customized by end users.
    It allows users to upload static docker images that can run specific types of models.
    These docker images will expose parameters that can be injected at ModelAlias creation
    time to customize the functionality. A common example of this is to use a
    HuggingFace LLM template, but swap out model weights for a finetuned model.

    Attributes:
        id: The unique identifier of the entity.
        created_at: The date and time when the entity was created in ISO format.
        account_id: The ID of the account that owns the given entity.
        created_by_user_id: The user who originally created the entity.
        name: The name of the model template
        endpoint_type: The type of endpoint that the model template will create
        model_type: The type of model that the model template will create
        vendor_configuration: The vendor configuration of the model template
        model_creation_parameters_schema: The field names and types of available parameter fields
            which may be specified during model creation
        model_request_parameters_schema: The field names and types of available parameter fields
            which may be specified in a model execution API's `model_request_parameters` field.
    """

    name: str
    endpoint_type: ModelEndpointType
    model_type: ModelType
    vendor_configuration: ModelVendorConfiguration
    model_creation_parameters_schema: Optional[ParameterSchema] = Field(
        None,
        description="The field names and types of available parameter fields which may be "
        "specified during model creation",
    )
    model_request_parameters_schema: Optional[ParameterSchema] = Field(
        None,
        description="The field names and types of available parameter fields which may be "
        "specified in a model execution API's `model_request_parameters` field.",
    )
    id: str = Field(..., description="The unique identifier of the entity.")
    created_at: datetime = Field(
        ..., description="The date and time when the entity was created in ISO format."
    )
    account_id: str = Field(..., description="The ID of the account that owns the given entity.")
    created_by_user_id: str = Field(..., description="The user who originally created the entity.")


class ModelTemplateRequest(BaseModel):
    name: str
    endpoint_type: ModelEndpointType
    model_type: ModelType
    vendor_configuration: ModelVendorConfiguration
    model_creation_parameters_schema: Optional[ParameterSchema] = Field(
        None,
        description="The field names and types of available parameter fields which may be "
        "specified during model creation",
    )
    model_request_parameters_schema: Optional[ParameterSchema] = Field(
        None,
        description="The field names and types of available parameter fields which may be "
        "specified in a model execution API's `model_request_parameters` field.",
    )
    account_id: str = Field(..., description="The ID of the account that owns the given entity.")
