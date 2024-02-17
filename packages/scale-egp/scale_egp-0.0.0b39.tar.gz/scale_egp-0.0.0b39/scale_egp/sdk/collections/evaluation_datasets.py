import io
import json
from typing import Optional, List, Iterable, Union

import httpx

from scale_egp.sdk.enums import TestCaseSchemaType
from scale_egp.sdk.types.evaluation_dataset_test_cases import (
    TestCase, TestCaseRequest, TestCaseSchemaValidator, GenerationTestCaseData,
)
from scale_egp.sdk.types.evaluation_datasets import (
    EvaluationDataset,
    EvaluationDatasetRequest, EvaluationDatasetVersionRequest, EvaluationDatasetVersion,
)
from scale_egp.utils.api_utils import APIEngine


class EvaluationDatasetCollection(APIEngine):
    _sub_path = "v2/evaluation-datasets"

    # START sub collections
    def test_cases(self) -> "TestCaseCollection":
        """
        Returns a TestCaseCollection object for test cases associated with the current Evaluation
        Dataset.
        """
        return TestCaseCollection(self._api_client)

    def _versions(self) -> "EvaluationDatasetVersionCollection":
        """
        Returns a EvaluationDatasetVersionCollection object for versions associated with the current
        Evaluation Dataset.
        """
        return EvaluationDatasetVersionCollection(self._api_client)

    def create(
        self,
        name: str,
        schema_type: TestCaseSchemaType,
        account_id: Optional[str] = None,
    ) -> EvaluationDataset:
        """
        Create a new empty dataset.

        Generally since most users will already have a list of test cases they want to create a
        dataset from, they should use the `create_from_file` method instead.

        Args:
            name: The name of the dataset.
            schema_type: The schema type of the dataset.
            account_id: The ID of the account to create this dataset for.

        Returns:
            The newly created dataset.
        """
        response = self._post(
            sub_path=self._sub_path,
            request=EvaluationDatasetRequest(
                name=name,
                schema_type=schema_type,
                account_id=account_id or self._api_client.account_id,
            ),
        )
        evaluation_dataset = EvaluationDataset.from_dict(response.json())
        evaluation_dataset = self.update_dataset_version(evaluation_dataset=evaluation_dataset)
        return evaluation_dataset

    def get(
        self,
        id: str,
    ) -> EvaluationDataset:
        """
        Get an existing dataset by ID.

        Args:
            id: The ID of the dataset.

        Returns:
            The dataset.
        """
        latest_dataset_version = self._versions().get_latest(evaluation_dataset_id=id)
        response = self._get(
            sub_path=f"{self._sub_path}/{id}",
        )
        evaluation_dataset = EvaluationDataset.from_dict(response.json())
        if latest_dataset_version:
            evaluation_dataset.version_num = latest_dataset_version.num
        return evaluation_dataset

    def update(
        self,
        id: str,
        name: Optional[str] = None,
        schema_type: Optional[TestCaseSchemaType] = None,
    ) -> EvaluationDataset:
        """
        Update the attributes of an existing dataset.

        **Important**: This method will NOT update the version of the dataset. It will only
        update the attributes of the dataset. If you want to snapshot the current state of the
        dataset under an incremented version number, you should use the `update_dataset_version`
        method instead.

        Args:
            id: The ID of the dataset.
            name: The name of the dataset.
            schema_type: The schema type of the dataset.

        Returns:
            The updated dataset.
        """
        response = self._patch(
            sub_path=f"{self._sub_path}/{id}",
            request=EvaluationDatasetRequest.partial(
                name=name,
                schema_type=schema_type,
            ),
        )
        return EvaluationDataset.from_dict(response.json())

    def delete(
        self,
        id: str,
    ) -> bool:
        """
        Delete an existing dataset.

        Args:
            id: The ID of the dataset.

        Returns:
            True if the dataset was deleted, False otherwise.
        """
        response = self._delete(
            sub_path=f"{self._sub_path}/{id}",
        )
        return response.status_code == httpx.codes.ok

    def list(self) -> List[EvaluationDataset]:
        """
        List all datasets.

        Returns:
            The datasets.
        """
        response = self._get(
            sub_path=self._sub_path,
        )
        return [
            EvaluationDataset.from_dict(evaluation_dataset)
            for evaluation_dataset in response.json()
        ]

    def create_from_file(
        self,
        name: str,
        schema_type: TestCaseSchemaType,
        filepath: str,
    ) -> EvaluationDataset:
        """
        Create a new dataset that is seeded with test cases from a JSONL file.

        The headers of the JSONL file must match the fields of the specified schema type.

        The `schema_types` currently supported and their corresponding fields are:

        **Schema Types:**

        `GENERATION`

        | Field                 | Type             | Default                           |
        | --------------------- | ---------------- | --------------------------------- |
        | `input`               | `str`            | _required_                        |
        | `expected_output`     | `str`            | `None`                            |
        | `expected_extra_info` | `Dict[str, Any]` | `None`                            |

        Args:
            name: The name of the dataset.
            schema_type: The schema type of the dataset.
            filepath: The path to the JSONL file.

        Returns:
            The newly created dataset.
        """
        self._validate_file_type(filepath)
        evaluation_dataset = self.create(
            name=name,
            schema_type=schema_type,
        )
        self._add_test_cases_to_dataset_from_file(
            filepath=filepath,
            evaluation_dataset=evaluation_dataset,
            schema_type=schema_type,
        )
        evaluation_dataset = self.update_dataset_version(evaluation_dataset)
        return evaluation_dataset

    def overwrite_from_file(
        self,
        evaluation_dataset: EvaluationDataset,
        schema_type: TestCaseSchemaType,
        filepath: str,
    ) -> EvaluationDataset:
        """
        Overwrite all test cases in existing dataset from a JSONL file.

        The headers of the JSONL file must match the fields of the specified schema type.

        The `schema_types` currently supported and their corresponding fields are:

        **Schema Types:**

        `GENERATION`

        | Field                 | Type             | Default                           |
        | --------------------- | ---------------- | --------------------------------- |
        | `input`               | `str`            | _required_                        |
        | `expected_output`     | `str`            | `None`                            |
        | `expected_extra_info` | `Dict[str, Any]` | `None`                            |

        Args:
            evaluation_dataset: The dataset to overwrite.
            schema_type: The schema type of the dataset.
            filepath: The path to the JSONL file.

        Returns:
            The updated dataset.
        """
        self._validate_file_type(filepath)
        # Delete all existing test cases
        test_cases_to_delete = self.test_cases().list(evaluation_dataset=evaluation_dataset)
        for test_case in test_cases_to_delete:
            self.test_cases().delete(
                id=test_case.id,
                evaluation_dataset=evaluation_dataset,
            )
        # Update the dataset schema type
        self.update(
            id=evaluation_dataset.id,
            schema_type=schema_type,
        )
        # Add new test cases
        self._add_test_cases_to_dataset_from_file(
            filepath=filepath,
            evaluation_dataset=evaluation_dataset,
            schema_type=schema_type,
        )
        evaluation_dataset = self.update_dataset_version(evaluation_dataset=evaluation_dataset)
        return evaluation_dataset

    def add_test_cases(
        self,
        evaluation_dataset: EvaluationDataset,
        test_cases_data: List[Union[GenerationTestCaseData]],
        update_dataset_version: bool = True,
    ) -> EvaluationDataset:
        """
        Add new test cases to an existing dataset.

        Unless you want to batch up multiple modifications to a dataset and snapshot them all at
        once, you should leave update_dataset_version=True. See the docs for the
        `update_dataset_version` method for more details.

        The `schema_types` currently supported and their corresponding fields are:

        **Schema Types:**

        `GENERATION`

        | Field                 | Type             | Default                           |
        | --------------------- | ---------------- | --------------------------------- |
        | `input`               | `str`            | _required_                        |
        | `expected_output`     | `str`            | `None`                            |
        | `expected_extra_info` | `Dict[str, Any]` | `None`                            |

        Args:
            evaluation_dataset: The dataset to add test cases to.
            test_cases_data: The test cases to add.
            update_dataset_version: Whether to update the dataset version after adding the test
                cases. Defaults to True.

        Returns:
            The updated dataset.
        """
        self.test_cases().create_batch(
            evaluation_dataset=evaluation_dataset,
            test_cases=[
                TestCaseRequest(
                    evaluation_dataset_id=evaluation_dataset.id,
                    schema_type=evaluation_dataset.schema_type,
                    test_case_data=test_case_data,
                    account_id=self._api_client.account_id,
                )
                for test_case_data in test_cases_data
            ],
        )
        if update_dataset_version:
            evaluation_dataset = self.update_dataset_version(evaluation_dataset=evaluation_dataset)
        return evaluation_dataset

    def add_test_cases_from_file(
        self,
        evaluation_dataset: EvaluationDataset,
        filepath: str,
        update_dataset_version: bool = True,
    ) -> EvaluationDataset:
        """
        Add new test cases to an existing dataset from a JSONL file.

        Unless you want to batch up multiple modifications to a dataset and snapshot them all at
        once, you should leave update_dataset_version=True. See the docs for the
        `update_dataset_version` method for more details.

        The `schema_types` currently supported and their corresponding fields are:

        **Schema Types:**

        `GENERATION`

        | Field                 | Type             | Default                           |
        | --------------------- | ---------------- | --------------------------------- |
        | `input`               | `str`            | _required_                        |
        | `expected_output`     | `str`            | `None`                            |
        | `expected_extra_info` | `Dict[str, Any]` | `None`                            |

        Args:
            evaluation_dataset: The dataset to add test cases to.
            filepath: The path to the JSONL file.
            update_dataset_version: Whether to update the dataset version after adding the test
                cases.

        Returns:
            The updated dataset.
        """
        self._validate_file_type(filepath)
        response = self._get(
            sub_path=f"{self._sub_path}/{evaluation_dataset.id}",
        )
        evaluation_dataset = EvaluationDataset.from_dict(response.json())
        self._add_test_cases_to_dataset_from_file(
            filepath=filepath,
            evaluation_dataset=evaluation_dataset,
            schema_type=evaluation_dataset.schema_type,
        )
        if update_dataset_version:
            evaluation_dataset = self.update_dataset_version(evaluation_dataset=evaluation_dataset)
        return evaluation_dataset

    def delete_test_cases(
        self,
        evaluation_dataset: EvaluationDataset,
        test_case_ids: List[str],
        update_dataset_version: bool = True,
    ) -> EvaluationDataset:
        """
        Delete test cases from an existing dataset.

        Unless you want to batch up multiple modifications to a dataset and snapshot them all at
        once, you should leave update_dataset_version=True. See the docs for the
        `update_dataset_version` method for more details.

        Args:
            evaluation_dataset: The dataset to delete test cases from.
            test_case_ids: The IDs of the test cases to delete.
            update_dataset_version: Whether to update the dataset version after deleting the test
                cases.

        Returns:
            The updated dataset.
        """
        for test_case_id in test_case_ids:
            self.test_cases().delete(
                id=test_case_id,
                evaluation_dataset=evaluation_dataset,
            )
        if update_dataset_version:
            evaluation_dataset = self.update_dataset_version(evaluation_dataset=evaluation_dataset)
        return evaluation_dataset

    def modify_test_cases(
        self,
        evaluation_dataset: EvaluationDataset,
        modified_test_cases: List[TestCase],
        update_dataset_version: bool = True,
    ) -> EvaluationDataset:
        """
        Modify test cases in an existing dataset.

        Unless you want to batch up multiple modifications to a dataset and snapshot them all at
        once, you should leave update_dataset_version=True. See the docs for the
        `update_dataset_version` method for more details.

        Args:
            evaluation_dataset: The dataset to modify test cases in.
            modified_test_cases: The modified test cases.
            update_dataset_version: Whether to update the dataset version after modifying the test
                cases.

        Returns:
            The updated dataset.
        """
        for test_case in modified_test_cases:
            self.test_cases().update(
                test_case_id=test_case.id,
                evaluation_dataset=evaluation_dataset,
                schema_type=test_case.schema_type,
                test_case_data=test_case.test_case_data,
            )
        if update_dataset_version:
            evaluation_dataset = self.update_dataset_version(evaluation_dataset=evaluation_dataset)
        return evaluation_dataset

    def update_dataset_version(self, evaluation_dataset: EvaluationDataset) -> EvaluationDataset:
        """
        Update the version of an existing dataset.

        This method will snapshot the current state of the dataset under an incremented version
        number.

        **Warning**: By default, the `add_test_cases`, `delete_test_cases`, and `modify_test_cases`
        methods will automatically update the dataset version for you. However,
        if you want to batch up multiple modifications to a dataset and snapshot them all at once,
        you can set `update_dataset_version=False` on those methods and then call this method
        manually afterward.

        Args:
            evaluation_dataset: The dataset to update the version of.

        Returns:
            The updated dataset.
        """
        evaluation_dataset_version = self._versions().create(evaluation_dataset=evaluation_dataset)
        evaluation_dataset.version_num = evaluation_dataset_version.num
        return evaluation_dataset

    def _add_test_cases_to_dataset_from_file(
        self, filepath: str, evaluation_dataset: EvaluationDataset, schema_type: TestCaseSchemaType
    ):
        self._validate_file_type(filepath)
        test_cases = []
        with io.open(filepath, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                json_data = json.loads(line)
                test_cases.append(
                    TestCaseRequest(
                        evaluation_dataset_id=evaluation_dataset.id,
                        schema_type=schema_type,
                        test_case_data=TestCaseSchemaValidator.dict_to_model(
                            schema_type=schema_type,
                            data=json_data.items(),
                        ),
                        account_id=self._api_client.account_id,
                    )
                )
        self.test_cases().create_batch(
            evaluation_dataset=evaluation_dataset,
            test_cases=test_cases,
        )

    @staticmethod
    def _validate_file_type(filepath: str):
        if not filepath.endswith(".jsonl"):
            raise ValueError(
                "The filepath provided must be a JSONL file. "
                "See https://jsonlines.org/ for more details."
            )


class EvaluationDatasetVersionCollection(APIEngine):
    _sub_path = "v2/evaluation-datasets/{evaluation_dataset_id}/evaluation-dataset-versions"

    def create(
        self,
        evaluation_dataset: EvaluationDataset,
    ) -> EvaluationDatasetVersion:
        """
        Create a new dataset version.

        Args:
            evaluation_dataset: The dataset to create a version for.

        Returns:
            The newly created dataset version.
        """
        response = self._post(
            sub_path=self._sub_path.format(evaluation_dataset_id=evaluation_dataset.id),
            request=EvaluationDatasetVersionRequest(
                evaluation_dataset_id=evaluation_dataset.id,
                account_id=evaluation_dataset.account_id or self._api_client.account_id,
            ),
        )
        return EvaluationDatasetVersion.from_dict(response.json())

    def get(
        self,
        id: str,
        evaluation_dataset: EvaluationDataset,
    ) -> EvaluationDatasetVersion:
        """
        Get an existing dataset version by ID.

        Args:
            id: The ID of the dataset version.
            evaluation_dataset: The dataset to get the version from.

        Returns:
            The dataset version.
        """
        response = self._get(
            sub_path=f"{self._sub_path.format(evaluation_dataset_id=evaluation_dataset.id)}/{id}",
        )
        return EvaluationDatasetVersion.from_dict(response.json())

    def list(
        self,
        evaluation_dataset: EvaluationDataset,
    ) -> List[EvaluationDatasetVersion]:
        """
        List all versions of a dataset.

        Args:
            evaluation_dataset: The dataset to list versions from.

        Returns:
            The dataset versions.
        """
        response = self._get(
            sub_path=self._sub_path.format(evaluation_dataset_id=evaluation_dataset.id),
        )
        return [
            EvaluationDatasetVersion.from_dict(evaluation_dataset_version)
            for evaluation_dataset_version in response.json()
        ]

    def get_latest(
        self,
        evaluation_dataset_id: str,
    ) -> Optional[EvaluationDatasetVersion]:
        """
        Get the latest version of a dataset.

        Args:
            evaluation_dataset_id: The ID of the dataset.

        Returns:
            The latest dataset version, or None if no versions exist.
        """
        response = self._get(
            sub_path=self._sub_path.format(evaluation_dataset_id=evaluation_dataset_id),
        )
        existing_dataset_versions = [
            EvaluationDatasetVersion.from_dict(evaluation_dataset_version)
            for evaluation_dataset_version in response.json()
        ]
        if existing_dataset_versions:
            return sorted(existing_dataset_versions, key=lambda x: x.num)[-1]
        return None


class TestCaseCollection(APIEngine):
    _sub_path = "v2/evaluation-datasets/{evaluation_dataset_id}/test-cases"

    def create(
        self,
        evaluation_dataset: EvaluationDataset,
        schema_type: TestCaseSchemaType,
        test_case_data: Union[GenerationTestCaseData],
    ) -> TestCase:
        """
        Create a new test case.

        Args:
            evaluation_dataset: The dataset to create the test case in.
            schema_type: The schema type of the test case.
            test_case_data: The test case data.

        Returns:
            The newly created test case.
        """
        response = self._post(
            sub_path=self._sub_path.format(evaluation_dataset_id=evaluation_dataset.id),
            request=TestCaseRequest(
                evaluation_dataset_id=evaluation_dataset.id,
                schema_type=schema_type,
                test_case_data=test_case_data,
                account_id=self._api_client.account_id,
            ),
        )
        return TestCase.from_dict(response.json())

    def create_batch(
        self,
        evaluation_dataset: EvaluationDataset,
        test_cases: List[TestCaseRequest],
    ) -> List[TestCase]:
        """
        Create multiple new test cases.

        Args:
            evaluation_dataset: The dataset to create the test cases in.
            test_cases: The test cases to create.

        Returns:
            The newly created test cases.
        """
        response = self._post_batch(
            sub_path=f"{self._sub_path.format(evaluation_dataset_id=evaluation_dataset.id)}/batch",
            request_batch=test_cases,
        )
        return [TestCase.from_dict(test_case) for test_case in response.json()]

    def get(
        self,
        id: str,
        evaluation_dataset: EvaluationDataset,
    ) -> TestCase:
        """
        Get an existing test case by ID.

        Args:
            id: The ID of the test case.
            evaluation_dataset: The dataset to get the test case from.

        Returns:
            The test case.
        """
        response = self._get(
            sub_path=f"{self._sub_path.format(evaluation_dataset_id=evaluation_dataset.id)}/{id}",
        )
        return TestCase.from_dict(response.json())

    def list(self, evaluation_dataset: EvaluationDataset) -> List[TestCase]:
        """
        List all test cases in a dataset.

        Args:
            evaluation_dataset: The dataset to list test cases from.

        Returns:
            The test cases.
        """
        response = self._get(
            sub_path=self._sub_path.format(evaluation_dataset_id=evaluation_dataset.id),
        )
        return [TestCase.from_dict(test_case) for test_case in response.json()]

    def update(
        self,
        test_case_id: str,
        evaluation_dataset: EvaluationDataset,
        schema_type: Optional[TestCaseSchemaType] = None,
        test_case_data: Optional[Union[GenerationTestCaseData]] = None,
    ) -> TestCase:
        """
        Update an existing test case.

        Args:
            test_case_id: The ID of the test case.
            evaluation_dataset: The dataset to update the test case in.
            schema_type: The schema type of the test case.
            test_case_data: The test case data.

        Returns:
            The updated test case.
        """
        response = self._patch(
            sub_path=f"{self._sub_path.format(evaluation_dataset_id=evaluation_dataset.id)}/"
            f"{test_case_id}",
            request=TestCaseRequest.partial(
                schema_type=schema_type,
                test_case_data=test_case_data,
            ),
        )
        return TestCase.from_dict(response.json())

    def iter(self, evaluation_dataset: EvaluationDataset) -> Iterable[TestCase]:
        """
        Iterate over all test cases in a dataset.

        Args:
            evaluation_dataset: The dataset to iterate over test cases from.

        Returns:
            The test cases.
        """
        response = self._get(
            sub_path=self._sub_path.format(evaluation_dataset_id=evaluation_dataset.id),
        )
        for test_case in response.json():
            yield TestCase.from_dict(test_case)

    def delete(
        self,
        id: str,
        evaluation_dataset: EvaluationDataset,
    ) -> bool:
        """
        Delete an existing test case.

        Args:
            id: The ID of the test case.
            evaluation_dataset: The dataset to delete the test case from.

        Returns:
            True if the test case was deleted successfully, False otherwise.
        """
        response = self._delete(
            sub_path=f"{self._sub_path.format(evaluation_dataset_id=evaluation_dataset.id)}/{id}",
        )
        return response.status_code == httpx.codes.ok
