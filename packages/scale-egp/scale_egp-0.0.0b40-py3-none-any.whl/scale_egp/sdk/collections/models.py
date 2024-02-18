from typing import Any, List, Optional, Dict

import httpx
from scale_egp.sdk.enums import ModelType, ModelVendor

from scale_egp.sdk.types.models import (
    ModelInstance,
    ModelDeployment,
    ModelDeploymentRequest,
    ModelInstanceRequest,
    BaseModelRequest,
    BaseModelResponse,
)
from scale_egp.sdk.constants.model_schemas import MODEL_SCHEMAS
from scale_egp.utils.api_utils import APIEngine
from scale_egp.utils.model_utils import dict_without_none_values, make_partial_model
from scale_egp.sdk.models.model_vendor_configuration import DeploymentVendorConfiguration


PartialModelAliasRequest = make_partial_model(ModelInstanceRequest)


class ModelInstanceCollection(APIEngine):
    """
    Collections class for EGP Models.
    """

    _sub_path = "v3/models"

    # START sub collections
    def deployments(self) -> "ModelDeploymentCollection":
        """
        Returns a ModelDeploymentCollection for deployments associated with this model.
        """
        return ModelDeploymentCollection(self._api_client)

    # END sub collections

    def create(
        self,
        name: str,
        model_type: ModelType,
        model_group_id: Optional[str] = None,
        model_vendor: Optional[ModelVendor] = None,
        model_template_id: Optional[str] = None,
        base_model_id: Optional[str] = None,
        base_model_metadata: Optional[Dict[str, Any]] = None,
        account_id: Optional[str] = None,
    ) -> ModelInstance:
        """
        Create a new EGP Model.

        Returns:
            The created Model.
        """
        response = self._post(
            sub_path=self._sub_path,
            request=ModelInstanceRequest(
                name=name,
                model_type=model_type,
                model_vendor=model_vendor,
                model_template_id=model_template_id,
                base_model_id=base_model_id,
                base_model_metadata=base_model_metadata,
                account_id=account_id or self._api_client.account_id,
                model_group_id=model_group_id,
            ),
        )
        return ModelInstance.from_dict(response.json())

    def get(
        self,
        id: str,
    ) -> ModelInstance:
        """
        Get a Model by ID.

        Returns:
            The Model.
        """
        response = self._get(
            sub_path=f"{self._sub_path}/{id}",
        )
        return ModelInstance.from_dict(response.json())

    def update(
        self,
        id: str,
        *,
        name: Optional[str] = None,
        model_template_id: Optional[str] = None,
        base_model_id: Optional[str] = None,
        model_creation_parameters: Optional[Dict[str, Any]] = None,
    ) -> ModelInstance:
        """
        Update a Model by ID.

        Returns:
            The updated Model.
        """
        response = self._patch(
            sub_path=f"{self._sub_path}/{id}",
            request=PartialModelAliasRequest(
                **dict_without_none_values(
                    dict(
                        name=name,
                        model_template_id=model_template_id,
                        base_model_id=base_model_id,
                        model_creation_parameters=model_creation_parameters,
                    ),
                )
            ),
        )
        return ModelInstance.from_dict(response.json())

    def delete(
        self,
        id: str,
    ) -> bool:
        """
        Delete a model by ID.

        Returns:
            True if the model was successfully deleted.
        """
        response = self._delete(
            sub_path=f"{self._sub_path}/{id}",
        )
        return response.status_code == httpx.codes.ok

    def list(
        self,
    ) -> List[ModelInstance]:
        """
        List all models that the user has access to.

        Returns:
            A list of Studio Projects.
        """
        response = self._get(
            sub_path=self._sub_path,
        )
        return [ModelInstance.from_dict(model) for model in response.json()]


class ModelDeploymentCollection(APIEngine):
    _sub_path = "v3/models/{model_id}/deployments"

    def create(
        self,
        model: ModelInstance,
        name: str,
        model_creation_parameters: Optional[Dict[str, Any]] = None,
        vendor_configuration: Optional[DeploymentVendorConfiguration] = None,
        account_id: Optional[str] = None,
    ) -> ModelDeployment:
        """
        Create a new ModelDeployment.

        Args:
            model: The Model to associate the ModelDeployment with.

        Returns:
            The newly created ModelDeployment.
        """
        response = self._post(
            sub_path=self._sub_path.format(model_id=model.id),
            request=ModelDeploymentRequest(
                name=name,
                model_creation_parameters=model_creation_parameters,
                vendor_configuration=vendor_configuration,
                model_id=model.id,
                account_id=account_id or self._api_client.account_id,
            ),
        )
        return ModelDeployment.from_dict(response.json())

    def get(
        self,
        id: str,
        model: ModelInstance,
    ) -> ModelDeployment:
        """
        Get a ModelDeployment by ID.

        Args:
            id: The ID of the ModelDeployment.
            model: The Model to associate the ModelDeployment with.

        Returns:
            The ModelDeployment.
        """
        response = self._get(
            sub_path=f"{self._sub_path.format(model_id=model.id)}/{id}",
        )
        return ModelDeployment.from_dict(response.json())

    # TODO <cathy-scale>: update?

    def delete(
        self,
        id: str,
        model: ModelInstance,
    ) -> bool:
        """
        Delete a ModelDeployment.

        Args:
            id: The ID of the ModelDeployment.
            model: The Model to associate the ModelDeployment with.
        """
        response = self._delete(
            sub_path=f"{self._sub_path.format(model_id=model.id)}/{id}",
        )
        return response.status_code == httpx.codes.ok

    def list(
        self,
        model: ModelInstance,
    ) -> List[ModelDeployment]:
        """
        List ModelDeployment.

        Args:
            model: The Model to associate the ModelDeployment with.

        Returns:
            A list of ModelDeployment.
        """
        response = self._get(
            sub_path=self._sub_path.format(model_id=model.id),
        )
        return [ModelDeployment.from_dict(deployment) for deployment in response.json()]

    def execute(
        self, id: str, model: ModelInstance, request: BaseModelRequest
    ) -> BaseModelResponse:
        """
        Execute the specified model deployment with the given request.

        Returns:
            The model deployment's response.
        """
        # TODO: verify model_request_parameters matches model template's
        #  model_request_parameters_schema if set
        model_request_cls, model_response_cls = MODEL_SCHEMAS[model.model_type]
        assert isinstance(request, model_request_cls)
        response = self._post(
            sub_path=f"{self._sub_path.format(model_id=model.id)}/{id}/execute",
            request=request,
            timeout=10 * 60,  # 10 minutes
        )
        return model_response_cls(**response.json())
