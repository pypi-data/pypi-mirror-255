from typing import List, Optional

import httpx

from scale_egp.sdk.types.studio_projects import StudioProject, StudioProjectRequest
from scale_egp.utils.api_utils import APIEngine


class StudioProjectCollection(APIEngine):
    """
    Collections class for Scale Studio projects used for LLM application evaluation.
    """

    _sub_path = "v2/studio-projects"

    def create(
        self,
        name: str,
        description: str,
        studio_api_key: str,
        account_id: Optional[str] = None,
    ) -> StudioProject:
        """
        Create a new Studio Project.

        Args:
            name: The name of the Studio Project.
            description: The description of the Studio Project.
            studio_api_key: The API key for the Studio Project. This can be found in the user's
                [Studio settings](https://dashboard.scale.com/studio/settings){:target="_blank"}.
            account_id: The ID of the account to create this Studio Project for.

        Returns:
            The newly created Studio Project.
        """
        response = self._post(
            sub_path=self._sub_path,
            request=StudioProjectRequest(
                name=name,
                description=description,
                studio_api_key=studio_api_key,
                account_id=account_id or self._api_client.account_id,
            ),
        )
        return StudioProject.from_dict(response.json())

    def get(
        self,
        id: str,
    ) -> StudioProject:
        """
        Get a Studio Project by ID.

        Args:
            id: The ID of the Studio Project.

        Returns:
            The Studio Project.
        """
        response = self._get(
            sub_path=f"{self._sub_path}/{id}",
        )
        return StudioProject.from_dict(response.json())

    def update(
        self,
        id: str,
        name: Optional[str] = None,
        description: Optional[str] = None,
        studio_api_key: Optional[str] = None,
    ) -> StudioProject:
        """
        Update a Studio Project by ID.

        Args:
            id: The ID of the Studio Project.
            name: The name of the Studio Project.
            description: The description of the Studio Project.
            studio_api_key: The API key for the Studio Project. This can be found in the user's \
            [Studio settings](https://dashboard.scale.com/studio/settings){:target="_blank"}.

        Returns:
            The updated Studio Project.
        """
        response = self._patch(
            sub_path=f"{self._sub_path}/{id}",
            request=StudioProjectRequest.partial(
                name=name,
                description=description,
                studio_api_key=studio_api_key,
            ),
        )
        return StudioProject.from_dict(response.json())

    def delete(
        self,
        id: str,
    ) -> bool:
        """
        Delete a Studio Project by ID.

        Args:
            id: The ID of the Studio Project.

        Returns:
            The deleted Studio Project.
        """
        response = self._delete(
            sub_path=f"{self._sub_path}/{id}",
        )
        return response.status_code == httpx.codes.ok

    def list(
        self,
    ) -> List[StudioProject]:
        """
        List all Studio Projects.

        Returns:
            A list of Studio Projects.
        """
        response = self._get(
            sub_path=self._sub_path,
        )
        return [StudioProject.from_dict(project) for project in response.json()]
