from typing import List, Optional

import httpx

from scale_egp.sdk.types.application_specs import (
    ApplicationSpecRequest,
    ApplicationSpec,
)
from scale_egp.utils.api_utils import APIEngine


class ApplicationSpecCollection(APIEngine):
    _sub_path = "v2/application-specs"

    def create(
        self,
        name: str,
        description: str,
        account_id: Optional[str] = None,
    ) -> ApplicationSpec:
        """
        Create a new Application Spec.

        Args:
            name: The name of the Application Spec.
            description: The description of the Application Spec.
            account_id: The ID of the account to create this Application Spec for.

        Returns:
            The newly created Application Spec.
        """

        response = self._post(
            sub_path=self._sub_path,
            request=ApplicationSpecRequest(
                name=name,
                description=description,
                account_id=account_id or self._api_client.account_id,
            ),
        )
        return ApplicationSpec.from_dict(response.json())

    def get(
        self,
        id: str,
    ) -> ApplicationSpec:
        """
        Get an Application Spec by ID.

        Args:
            id: The ID of the Application Spec.

        Returns:
            The Application Spec.
        """
        response = self._get(
            sub_path=f"{self._sub_path}/{id}",
        )
        return ApplicationSpec.from_dict(response.json())

    def update(
        self,
        id: str,
        name: Optional[str] = None,
        description: Optional[str] = None,
    ) -> ApplicationSpec:
        """
        Update an Application Spec by ID.

        Args:
            id: The ID of the Application Spec.
            name: The name of the Application Spec.
            description: The description of the Application Spec.

        Returns:
            The updated Application Spec.
        """
        response = self._patch(
            sub_path=f"{self._sub_path}/{id}",
            request=ApplicationSpecRequest.partial(
                name=name,
                description=description,
            ),
        )
        return ApplicationSpec.from_dict(response.json())

    def delete(
        self,
        id: str,
    ) -> bool:
        """
        Delete an Application Spec by ID.

        Args:
            id: The ID of the Application Spec.
        """
        response = self._delete(
            sub_path=f"{self._sub_path}/{id}",
        )
        return response.status_code == httpx.codes.ok

    def list(
        self,
    ) -> List[ApplicationSpec]:
        """
        List all Application Specs.

        Returns:
            A list of Application Specs.
        """
        response = self._get(
            sub_path=self._sub_path,
        )
        return [ApplicationSpec.from_dict(spec) for spec in response.json()]
