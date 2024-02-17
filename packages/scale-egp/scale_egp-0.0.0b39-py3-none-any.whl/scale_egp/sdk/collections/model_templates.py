from typing import List, Optional

import httpx

from scale_egp.sdk.types.model_templates import ModelTemplate, ModelTemplateRequest
from scale_egp.sdk.enums import ModelEndpointType, ModelType
from scale_egp.sdk.types.models import ParameterSchema
from scale_egp.sdk.types.model_templates import ModelVendorConfiguration
from scale_egp.utils.api_utils import APIEngine, long_timeout
from scale_egp.utils.model_utils import dict_without_none_values, make_partial_model

PartialModelTemplateRequest = make_partial_model(ModelTemplateRequest)


class ModelTemplateCollection(APIEngine):
    """
    Collections class for EGP Models.
    """

    _sub_path = "v3/model-templates"

    def create(
        self,
        name: str,
        endpoint_type: ModelEndpointType,
        model_type: ModelType,
        vendor_configuration: ModelVendorConfiguration,
        model_creation_parameters_schema: Optional[ParameterSchema] = None,
        model_request_parameters_schema: Optional[ParameterSchema] = None,
        account_id: Optional[str] = None,
    ) -> ModelTemplate:
        """
        Create a new EGP Model Template.

        Args:
            name: The name of the Model Template.
            endpoint_type: The type of model this template will create.
                See [Model Types and Schemas](/guides/custom_models/#model-types-and-schemas)
            model_type: The type of the Model Template.
            vendor_configuration: The vendor configuration of the Model Template.
            model_creation_parameters_schema: The model creation parameters schema of the Model Template.
            model_request_parameters_schema: The model request parameters schema of the Model Template.
            account_id: The account ID of the Model Template.

        Returns:
            The created Model Template.
        """
        response = self._post(
            sub_path=self._sub_path,
            request=ModelTemplateRequest(
                name=name,
                endpoint_type=endpoint_type,
                model_type=model_type,
                vendor_configuration=vendor_configuration,
                model_creation_parameters_schema=model_creation_parameters_schema,
                model_request_parameters_schema=model_request_parameters_schema,
                account_id=account_id or self._api_client.account_id,
            ),
            timeout=long_timeout,
        )
        return ModelTemplate.from_dict(response.json())

    def get(
        self,
        id: str,
    ) -> ModelTemplate:
        """
        Get a Model Template by ID.

        Returns:
            The Model Template.
        """
        response = self._get(
            sub_path=f"{self._sub_path}/{id}",
        )
        return ModelTemplate.from_dict(response.json())

    def update(
        self,
        id: str,
        *,
        name: str,
        endpoint_type: Optional[ModelEndpointType] = None,
        model_type: Optional[ModelType] = None,
        vendor_configuration: Optional[ModelVendorConfiguration] = None,
        model_creation_parameters_schema: Optional[ParameterSchema] = None,
        model_request_parameters_schema: Optional[ParameterSchema] = None,
    ) -> ModelTemplate:
        """
        Update a Model Template by ID.

        Returns:
            The updated Model Template.
        """
        response = self._patch(
            sub_path=f"{self._sub_path}/{id}",
            request=PartialModelTemplateRequest(
                **dict_without_none_values(
                    dict(
                        name=name,
                        endpoint_type=endpoint_type,
                        model_type=model_type,
                        vendor_configuration=vendor_configuration,
                        model_creation_parameters_schema=model_creation_parameters_schema,
                        model_request_parameters_schema=model_request_parameters_schema,
                    )
                )
            ),
        )
        return ModelTemplate.from_dict(response.json())

    def delete(
        self,
        id: str,
    ) -> bool:
        """
        Delete a Model Template by ID.

        Returns:
            True if the Model Template was successfully deleted.
        """
        response = self._delete(
            sub_path=f"{self._sub_path}/{id}",
        )
        return response.status_code == httpx.codes.ok

    def list(
        self,
    ) -> List[ModelTemplate]:
        """
        List all Model Templates that the user has access to.

        Returns:
            A list of Model Templates that the user has access to.
        """
        response = self._get(
            sub_path=self._sub_path,
        )
        return [ModelTemplate.from_dict(model_template) for model_template in response.json()]
