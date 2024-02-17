from typing import Any, Optional, List, Dict, Union

import httpx

from scale_egp.sdk.types.application_specs import ApplicationSpec
from scale_egp.sdk.types.evaluation_configs import StudioEvaluationConfig
from scale_egp.sdk.types.evaluation_dataset_test_cases import TestCase
from scale_egp.sdk.types.evaluation_datasets import EvaluationDataset
from scale_egp.sdk.types.evaluation_test_case_results import \
    (
    TestCaseResult, TestCaseResultRequest, GenerationTestCaseResultData,
)
from scale_egp.sdk.types.evaluations import Evaluation, EvaluationRequest
from scale_egp.utils.api_utils import (
    APIEngine,
)


class EvaluationCollection(APIEngine):
    _sub_path = "v2/evaluations"

    # START sub collections
    def test_case_results(self) -> "TestCaseResultCollection":
        """
        Returns a TestCaseResultCollection for test case results associated with this evaluation.
        """
        return TestCaseResultCollection(self._api_client)

    def create(
        self,
        name: str,
        description: str,
        application_spec: ApplicationSpec,
        evaluation_config: Union[StudioEvaluationConfig],
        tags: Optional[Dict[str, Any]] = None,
        account_id: Optional[str] = None,
    ) -> Evaluation:
        """
        Create a new Evaluation.

        Args:
            name: The name of the Evaluation.
            description: The description of the Evaluation.
            application_spec: The Application Spec to associate the Evaluation with.
            evaluation_config: The configuration for the Evaluation.
            tags: Optional key, value pairs to associate with the Evaluation.
            account_id: The ID of the account to create this Evaluation for.

        Returns:
            The newly created Evaluation.
        """
        response = self._post(
            sub_path=self._sub_path,
            request=EvaluationRequest(
                name=name,
                description=description,
                application_spec_id=application_spec.id,
                evaluation_config=evaluation_config,
                tags=tags,
                account_id=account_id or self._api_client.account_id,
            ),
        )
        return Evaluation.from_dict(response.json())

    def get(
        self,
        id: str,
    ) -> Evaluation:
        """
        Get an Evaluation by ID.

        Args:
            id: The ID of the Evaluation.

        Returns:
            The Evaluation.
        """
        response = self._get(
            sub_path=f"{self._sub_path}/{id}",
        )
        return Evaluation.from_dict(response.json())

    def update(
        self,
        id: str,
        name: Optional[str] = None,
        description: Optional[str] = None,
        evaluation_config: Optional[Union[StudioEvaluationConfig]] = None,
        tags: Optional[Dict[str, Any]] = None,
    ) -> Evaluation:
        """
        Update an Evaluation.

        Args:
            id: The ID of the Evaluation.
            name: The name of the Evaluation.
            description: The description of the Evaluation.
            evaluation_config: The configuration for the Evaluation.
            tags: Optional key, value pairs to associate with the Evaluation.

        Returns:
            The updated Evaluation.
        """
        response = self._patch(
            sub_path=f"{self._sub_path}/{id}",
            request=EvaluationRequest.partial(
                name=name,
                description=description,
                evaluation_config=evaluation_config,
                tags=tags,
            ),
        )
        return Evaluation.from_dict(response.json())

    def delete(
        self,
        id: str,
    ) -> bool:
        """
        Delete an Evaluation.

        Args:
            id: The ID of the Evaluation.
        """
        response = self._delete(
            sub_path=f"{self._sub_path}/{id}",
        )
        return response.status_code == httpx.codes.ok

    def list(
        self,
    ) -> List[Evaluation]:
        """
        List Evaluations.

        Returns:
            A list of Evaluations.
        """
        response = self._get(
            sub_path=self._sub_path,
        )
        return [Evaluation.from_dict(evaluation) for evaluation in response.json()]


class TestCaseResultCollection(APIEngine):
    _sub_path = "v2/evaluations/{evaluation_id}/test-case-results"

    def create(
        self,
        evaluation: Evaluation,
        evaluation_dataset: EvaluationDataset,
        test_case: TestCase,
        test_case_evaluation_data: Union[GenerationTestCaseResultData],
    ) -> TestCaseResult:
        """
        Create a new TestCaseResult.

        Args:
            evaluation: The Evaluation to associate the TestCaseResult with.
            evaluation_dataset: The EvaluationDataset to associate the TestCaseResult with.
            test_case: The TestCase to associate the TestCaseResult with.
            test_case_evaluation_data: The data generated by the application that needs to be
                evaluated.

        Returns:
            The newly created TestCaseResult.
        """
        response = self._post(
            sub_path=self._sub_path.format(evaluation_id=evaluation.id),
            request=TestCaseResultRequest(
                application_spec_id=evaluation.application_spec_id,
                evaluation_dataset_version_num=evaluation_dataset.version_num,
                test_case_id=test_case.id,
                test_case_evaluation_data_schema=test_case.schema_type,
                test_case_evaluation_data=test_case_evaluation_data,
                account_id=self._api_client.account_id,
            ),
        )
        return TestCaseResult.from_dict(response.json())

    def get(
        self,
        id: str,
        evaluation: Evaluation,
    ) -> TestCaseResult:
        """
        Get a TestCaseResult by ID.

        Args:
            id: The ID of the TestCaseResult.
            evaluation: The Evaluation to associate the TestCaseResult with.

        Returns:
            The TestCaseResult.
        """
        response = self._get(
            sub_path=f"{self._sub_path.format(evaluation_id=evaluation.id)}/{id}",
        )
        return TestCaseResult.from_dict(response.json())

    def update(
        self,
        id: str,
        evaluation: Evaluation,
        result: Optional[Dict[str, Any]] = None,
    ) -> TestCaseResult:
        """
        Update a TestCaseResult.

        Args:
            id: The ID of the TestCaseResult.
            evaluation: The Evaluation to associate the TestCaseResult with.
            result: Optional result to associate with the TestCaseResult.

        Returns:
            The updated TestCaseResult.
        """
        response = self._patch(
            sub_path=f"{self._sub_path.format(evaluation_id=evaluation.id)}/{id}",
            request=TestCaseResultRequest.partial(
                result=result,
            ),
        )
        return TestCaseResult.from_dict(response.json())

    def delete(
        self,
        id: str,
        evaluation: Evaluation,
    ) -> bool:
        """
        Delete a TestCaseResult.

        Args:
            id: The ID of the TestCaseResult.
            evaluation: The Evaluation to associate the TestCaseResult with.
        """
        response = self._delete(
            sub_path=f"{self._sub_path.format(evaluation_id=evaluation.id)}/{id}",
        )
        return response.status_code == httpx.codes.ok

    def list(
        self,
        evaluation: Evaluation,
    ) -> List[TestCaseResult]:
        """
        List TestCaseResults.

        Args:
            evaluation: The Evaluation to associate the TestCaseResults with.

        Returns:
            A list of TestCaseResults.
        """
        response = self._get(
            sub_path=self._sub_path.format(evaluation_id=evaluation.id),
        )
        return [TestCaseResult.from_dict(test_case_result) for test_case_result in response.json()]
