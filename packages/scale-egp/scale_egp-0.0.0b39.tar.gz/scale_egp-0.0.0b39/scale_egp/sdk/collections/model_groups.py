from typing import List, Optional
import httpx

from scale_egp.sdk.types.models_group import ModelGroup, ModelGroupRequest
from scale_egp.utils.api_utils import APIEngine
from scale_egp.utils.model_utils import dict_without_none_values, make_partial_model


PartialModelGroupRequest = make_partial_model(ModelGroupRequest)


class ModelGroupCollection(APIEngine):
    """
    Collections class for EGP Model Groups.
    """

    _sub_path = "v3/model-groups"

    def create(
        self,
        name: str,
        description: Optional[str] = None,
        account_id: Optional[str] = None,
    ) -> str:
        """
        Create a new EGP Model Group.

        Returns:
            The created Model Group ID.
        """
        response = self._post(
            sub_path=self._sub_path,
            request=ModelGroupRequest(
                name=name,
                description=description,
                account_id=account_id or self._api_client.account_id,
            ),
        )
        return ModelGroup.from_dict(response.json())

    def get(
        self,
        id: str,
    ) -> ModelGroup:
        """
        Get a Model Group by ID.

        Returns:
            The Model Group.
        """
        response = self._get(
            sub_path=f"{self._sub_path}/{id}",
        )
        return ModelGroup.from_dict(response.json())

    def update(
        self,
        id: str,
        name: Optional[str] = None,
        description: Optional[str] = None,
    ) -> ModelGroup:
        """
        Update a Model Group by ID.

        Returns:
            The updated Model Group.
        """
        response = self._patch(
            sub_path=f"{self._sub_path}/{id}",
            request=PartialModelGroupRequest(
                **dict_without_none_values(
                    dict(
                        name=name,
                        description=description,
                    ),
                )
            ),
        )
        return ModelGroup.from_dict(response.json())

    def delete(
        self,
        id: str,
    ) -> bool:
        """
        Delete a Model Group by ID.

        Returns:
            True if the Model Group was successfully deleted.
        """
        response = self._delete(
            sub_path=f"{self._sub_path}/{id}",
        )
        return response.status_code == httpx.codes.ok

    def list(
        self,
    ) -> List[ModelGroup]:
        """
        List all models that the user has access to.

        Returns:
            A list of Studio Projects.
        """
        response = self._get(
            sub_path=self._sub_path,
        )
        return [ModelGroup.from_dict(model) for model in response.json()]
