from typing import IO, List, Optional
import httpx
from httpx._types import FileTypes

from scale_egp.utils.api_utils import APIEngine
from scale_egp.sdk.models.fine_tuning_jobs import FineTuningJobVendorConfiguration
from scale_egp.sdk.types.fine_tuning import (
    FineTuningJob,
    FineTuningJobRequest,
    TrainingDataset,
    TrainingDatasetRequest,
    TrainingDatasetORMSchemaTypeEnum,
)
import os.path


class TrainingDatasetCollection(APIEngine):
    """
    Collections class for EGP Model fine tuning jobs.
    """

    _sub_path = "v3/training-datasets"

    def create(
        self,
        file_content: Optional[FileTypes] = None,
        file_name: Optional[str] = None,
        account_id: Optional[str] = None,
        name: Optional[str] = None,
        schema_type: TrainingDatasetORMSchemaTypeEnum = TrainingDatasetORMSchemaTypeEnum.GENERATION,
    ) -> FineTuningJob:
        """
        Create a new EGP Model.

        Returns:
            The created Model.
        """
        if bool(file_content is None) == bool(file_name is None):
            raise Exception("Please specify either file_content or file_name")
        file_handle: Optional[IO[bytes]] = None
        file = file_content
        if file_name:
            file_handle = open(file_name, "rb")
            file = (os.path.basename(file_name), file_handle)
        name = os.path.basename(file_name) if file_name is not None else (name or "unnamed dataset")
        response = self._post(
            sub_path=self._sub_path,
            request={
                "account_id": account_id or self._api_client.account_id,
                "name": name,
                "schema_type": schema_type,
            },
            file=file,
        )
        if file_handle:
            file_handle.close()
        return TrainingDataset.from_dict(response.json())

    def get(
        self,
        id: str,
    ) -> FineTuningJob:
        """
        Get a Model fine tuning job by ID.

        Returns:
            The finet tuning job.
        """
        response = self._get(
            sub_path=f"{self._sub_path}/{id}",
        )
        return FineTuningJob.from_dict(response.json())

    def delete(
        self,
        id: str,
    ) -> bool:
        """
        Cancels a fine-tuning job by ID.

        Returns:
            True if the model was successfully deleted.
        """
        response = self._delete(
            sub_path=f"{self._sub_path}/{id}",
        )
        return response.status_code == httpx.codes.ok

    def list(
        self,
    ) -> List[FineTuningJob]:
        """
        List all models that the user has access to.

        Returns:
            A list of Studio Projects.
        """
        response = self._get(
            sub_path=self._sub_path,
        )
        return [FineTuningJob.from_dict(fine_tuning_job) for fine_tuning_job in response.json()]


class FineTuningJobCollection(APIEngine):
    """
    Collections class for EGP Model fine tuning jobs.
    """

    _sub_path = "v3/fine-tuning-jobs"

    def create(
        self,
        base_model_id: str,
        vendor_configuration: Optional[FineTuningJobVendorConfiguration],
        training_dataset_id: str,
        validation_dataset_id: Optional[str],
        account_id: Optional[str],
    ) -> FineTuningJob:
        """
        Create a new EGP Model.

        Returns:
            The created Model.
        """
        response = self._post(
            sub_path=self._sub_path,
            request=FineTuningJobRequest(
                base_model_id=base_model_id,
                vendor_configuration=vendor_configuration,
                training_dataset_id=training_dataset_id,
                validation_dataset_id=validation_dataset_id,
                account_id=account_id or self._api_client.account_id,
            ),
        )
        return FineTuningJob.from_dict(response.json())

    def get(
        self,
        id: str,
    ) -> FineTuningJob:
        """
        Get a Model fine tuning job by ID.

        Returns:
            The finet tuning job.
        """
        response = self._get(
            sub_path=f"{self._sub_path}/{id}",
        )
        return FineTuningJob.from_dict(response.json())

    def delete(
        self,
        id: str,
    ) -> bool:
        """
        Cancels a fine-tuning job by ID.

        Returns:
            True if the model was successfully deleted.
        """
        response = self._delete(
            sub_path=f"{self._sub_path}/{id}",
        )
        return response.status_code == httpx.codes.ok

    def list(
        self,
    ) -> List[FineTuningJob]:
        """
        List all models that the user has access to.

        Returns:
            A list of Studio Projects.
        """
        response = self._get(
            sub_path=self._sub_path,
        )
        return [FineTuningJob.from_dict(fine_tuning_job) for fine_tuning_job in response.json()]
