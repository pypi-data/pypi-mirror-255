import json
from typing import Any, Dict, Generator, Generic, Optional, Type, TypeVar
from scale_egp.cli.formatter import (
    FormattingOptions,
    get_formatting_options,
    set_formatting_options,
)
from scale_egp.cli.model_instance_description import ModelInstanceDescription
from scale_egp.sdk.client import EGPClient
from scale_egp.sdk.collections.model_templates import ModelTemplateCollection
from scale_egp.sdk.collections.models import ModelDeploymentCollection, ModelInstanceCollection
from scale_egp.sdk.collections.fine_tuning import FineTuningJobCollection, TrainingDatasetCollection
from scale_egp.sdk.enums import ModelVendor
from scale_egp.sdk.types.models_group import ModelGroup, ModelGroupRequest
from scale_egp.sdk.collections.model_groups import ModelGroupCollection
from scale_egp.sdk.types.user_info import UserInfoResponse, get_user_info
from scale_egp.sdk.types.models import (
    ModelDeployment,
    ModelDeploymentRequest,
    ModelInstance,
    ModelInstanceRequest,
)
from scale_egp.sdk.types.fine_tuning import (
    FineTuningJob,
    FineTuningJobRequest,
    TrainingDataset,
    TrainingDatasetRequest,
)
from scale_egp.sdk.types.model_templates import ModelTemplate, ModelTemplateRequest
from scale_egp.sdk.constants.model_schemas import MODEL_SCHEMAS
from scale_egp.utils.api_utils import APIEngine
from scale_egp.utils.model_utils import BaseModel
from argh import CommandError, arg
import fastjsonschema
from scale_egp.sdk.models.fine_tuning_jobs import FineTuningJobEvent


EntityT = TypeVar("EntityT", bound=BaseModel)
RequestT = TypeVar("RequestT", bound=BaseModel)


def read_json_file(filename: str, expected_type: Optional[Any] = dict) -> Any:
    with open(filename, "r", encoding="utf-8") as f:
        data = json.loads(f.read())
        if expected_type is not None:
            assert isinstance(data, expected_type)
        return data


class EGPClientFactory:
    def __init__(
        self,
    ):
        self.client: Optional[EGPClient] = None
        self._client_kwargs = None

    def set_client_kwargs(self, **kwargs):
        self._client_kwargs = kwargs

    def get_client(self) -> EGPClient:
        if self.client is None:
            self.client = EGPClient(**self._client_kwargs)
        return self.client


class CollectionCRUDCommandsForImmutable(Generic[EntityT, RequestT]):
    command_group_name = "CRUD"
    command_group_title: Optional[str] = None

    def __init__(
        self,
        client_factory: EGPClientFactory,
        entity_type: Type[EntityT],
        request_type: Type[RequestT],
        collection_type: Type[APIEngine],
    ):
        self._client_factory = client_factory
        self._entity_type = entity_type
        self._request_type = request_type
        self._collection_type = collection_type

    def _get_collection_instance(self) -> APIEngine:
        return self._collection_type(self._client_factory.get_client())

    def _transform_entity_json(self, entity_dict: Dict[str, Any]) -> Dict[str, Any]:
        return entity_dict

    def _get_api_subpath_prefix(self) -> str:
        collection = self._get_collection_instance()
        return getattr(collection, "_sub_path")

    def _create(self, request_dict: Any) -> EntityT:
        # add client account id if not set in file
        request_dict["account_id"] = request_dict.get(
            "account_id", self._client_factory.get_client().account_id
        )
        request_obj = self._request_type(**request_dict)
        collection = self._get_collection_instance()
        response = collection._post(self._get_api_subpath_prefix(), request_obj)
        assert response.status_code == 200
        response_dict = response.json()
        assert isinstance(response_dict, dict)
        return self._entity_type(**response_dict)

    @arg("filename", help="file to load")
    def create(self, filename: str) -> EntityT:
        request_dict = read_json_file(filename)
        return self._create(request_dict)

    def get(self, id: str) -> EntityT:
        collection = self._get_collection_instance()
        sub_path = f"{self._get_api_subpath_prefix()}/{id}"
        response = collection._get(sub_path)
        assert response.status_code == 200
        response_dict = response.json()
        assert isinstance(response_dict, dict)
        return self._entity_type(**response_dict)

    def delete(self, id: str) -> None:
        collection = self._get_collection_instance()
        sub_path = f"{self._get_api_subpath_prefix()}/{id}"
        response = collection._delete(sub_path)
        assert response.status_code == 200

    def list(self) -> Generator[EntityT, None, None]:
        formatting_options = get_formatting_options()
        formatting_options.force_list = True
        set_formatting_options(formatting_options)
        collection = self._get_collection_instance()
        response = collection._get(self._get_api_subpath_prefix())
        assert response.status_code == 200
        response_list = response.json()
        assert isinstance(response_list, list)
        # TODO: pagination
        for entity_dict in response_list:
            yield self._entity_type(**entity_dict)


class CollectionCRUDCommandsWithUpdate(
    Generic[EntityT, RequestT], CollectionCRUDCommandsForImmutable[EntityT, RequestT]
):
    def _update(self, id: str, request_dict: Any) -> EntityT:
        # add client account id if not set in file
        request_dict["account_id"] = request_dict.get(
            "account_id", self._client_factory.get_client().account_id
        )
        request_obj = self._request_type(**request_dict)
        collection = self._get_collection_instance()
        response = collection._patch(f"{self._get_api_subpath_prefix()}/{id}", request_obj)
        assert response.status_code == 200
        response_dict = response.json()
        assert isinstance(response_dict, dict)
        return self._entity_type(**response_dict)

    @arg("filename", help="file to load")
    def update(self, id: str, filename: str) -> EntityT:
        request_dict = read_json_file(filename)
        return self._update(id, request_dict)


class ModelInstanceCommands(CollectionCRUDCommandsWithUpdate[ModelInstance, ModelInstanceRequest]):
    command_group_name = "model-instance"

    def __init__(
        self,
        client_factory: EGPClientFactory,
    ):
        super().__init__(
            client_factory, ModelInstance, ModelInstanceRequest, ModelInstanceCollection
        )

    def list(self) -> Generator[EntityT, None, None]:
        set_formatting_options(
            FormattingOptions(table_columns=["id", "name", "model_template_id", "description"])
        )
        return super().list()

    def describe(self, model_id: str) -> ModelInstanceDescription:
        model_instance = self.get(model_id)
        model_template = ModelTemplateCommands(self._client_factory).get(
            model_instance.model_template_id
        )
        return ModelInstanceDescription(
            model_instance=model_instance, model_template=model_template
        )

    @arg("filename", help="file to load")
    @arg(
        "--model-template-id", help="id of the model template to use if not specified in JSON file"
    )
    def create(self, filename: str, model_template_id: Optional[str] = None) -> EntityT:
        request_dict = read_json_file(filename)
        if request_dict.get("model_vendor", ModelVendor.LAUNCH.value) == ModelVendor.LAUNCH.value:
            effective_model_template_id = request_dict.get("model_template_id", model_template_id)
            if effective_model_template_id is None:
                raise CommandError(
                    "No model template id specified in JSON file or --model-template-id option. Please provide the model template id for Launch models!"
                )
            request_dict["model_template_id"] = effective_model_template_id
            if request_dict.get("model_type") is None:
                # if no model_type is specified in model alias json, use model_type of template
                model_template = ModelTemplateCommands(self._client_factory).get(
                    effective_model_template_id
                )
                request_dict["model_type"] = model_template.model_type

        return self._create(request_dict)

    def _validate_request(self, model_instance: ModelInstance, request: Dict[str, Any]):
        validator = fastjsonschema.compile(model_instance.request_schema)
        return validator(request)

    @arg("filename", help="Model request")
    def validate_request(self, model_instance_id: str, filename: str) -> Optional[str]:
        model_instance = self.get(model_instance_id)
        execute_request_dict = read_json_file(filename)
        try:
            self._validate_request(model_instance, execute_request_dict)
        except fastjsonschema.JsonSchemaException as e:
            return f"Data failed validation: {e}"
        return None


class ModelDeploymentCommands(
    CollectionCRUDCommandsWithUpdate[ModelDeployment, ModelDeploymentRequest]
):
    command_group_name = "model-deployment"

    def __init__(
        self,
        client_factory: EGPClientFactory,
    ):
        super().__init__(
            client_factory, ModelDeployment, ModelDeploymentRequest, ModelDeploymentCollection
        )
        self.model_instance_id = None

    def _get_api_subpath_prefix(self) -> str:
        collection = self._get_collection_instance()
        return getattr(collection, "_sub_path").format(model_id=self.model_instance_id)

    def list(self, model_instance_id: str) -> Generator[EntityT, None, None]:
        self.model_instance_id = model_instance_id
        set_formatting_options(
            FormattingOptions(table_columns=["id", "name", "created_at", "description"])
        )
        return super().list()

    @arg("filename", nargs="?", help="JSON file specifying the deployment configuration")
    @arg("--model-deployment-name", help="Model deployment name")
    @arg("--model-instance-id", help="Model instance for which to create a deployment")
    def create(
        self,
        filename: Optional[str],
        model_instance_id: Optional[str] = None,
        model_deployment_name: Optional[str] = None,
    ) -> EntityT:
        request_dict = read_json_file(filename) if filename else {}
        if model_instance_id is not None:
            request_dict["model_instance_id"] = model_instance_id
        if request_dict.get("model_instance_id") is None:
            raise CommandError(
                "Please specify a model instance id, either using the --model-instance-id command line option or in the provided JSON file"
            )
        self.model_instance_id = request_dict["model_instance_id"]
        if model_deployment_name:
            request_dict["name"] = model_deployment_name
        if request_dict.get("name") is None:
            model_instance = ModelInstanceCommands(self._client_factory).get(
                request_dict["model_instance_id"]
            )
            # default to model instance name for the deployment name if its not set to something else
            request_dict["name"] = model_instance.name
        return self._create(request_dict)

    def get(self, model_instance_id: str, model_deployment_id: str) -> EntityT:
        self.model_instance_id = model_instance_id
        return super().get(model_deployment_id)

    def delete(self, model_instance_id: str, model_deployment_id: str) -> None:
        self.model_instance_id = model_instance_id
        return super().delete(model_deployment_id)

    @arg("filename", help="Model request")
    def execute(self, model_instance_id: str, model_deployment_id: str, filename: str) -> EntityT:
        self.model_instance_id = model_instance_id
        request_dict = read_json_file(filename)
        model_instance_commands = ModelInstanceCommands(self._client_factory)
        model_instance = model_instance_commands.get(model_instance_id)
        model_response_cls = MODEL_SCHEMAS[model_instance.model_type][1]
        parsed_request = model_instance_commands._validate_request(model_instance, request_dict)
        sub_path = f"{self._get_api_subpath_prefix()}/{model_deployment_id}/execute"
        collection = self._get_collection_instance()
        response = collection._post(
            sub_path=sub_path,
            request=parsed_request,
            timeout=10 * 60,  # 10 minutes
        )
        assert response.status_code == 200
        return model_response_cls(**response.json())


class ModelGroupCommands(CollectionCRUDCommandsWithUpdate[ModelGroup, ModelGroupRequest]):
    command_group_name = "model-group"

    def __init__(
        self,
        client_factory: EGPClientFactory,
    ):
        super().__init__(client_factory, ModelGroup, ModelGroupRequest, ModelGroupCollection)


class ModelTemplateCommands(
    CollectionCRUDCommandsForImmutable[ModelTemplate, ModelTemplateRequest]
):
    command_group_name = "model-template"

    def __init__(
        self,
        client_factory: EGPClientFactory,
    ):
        super().__init__(
            client_factory, ModelTemplate, ModelTemplateRequest, ModelTemplateCollection
        )

    def _transform_entity_json(self, entity_dict: Dict[str, Any]) -> Dict[str, Any]:
        if entity_dict.get("vendor_configuration") is not None:
            entity_dict["model_vendor"] = "LAUNCH"
        return entity_dict

    def list(self) -> Generator[EntityT, None, None]:
        set_formatting_options(
            FormattingOptions(table_columns=["id", "name", "model_type", "created_at"])
        )
        return super().list()

    def show_model_schemas(self):
        return [
            {
                "model_type": model_type.value,
                "request_schema": schemas[0].schema(),
                "response_schema": schemas[1].schema(),
            }
            for (model_type, schemas) in MODEL_SCHEMAS.items()
        ]


class UserCommands:
    command_group_name = "user"
    command_group_title = "User management and account information"

    def __init__(
        self,
        client_factory: EGPClientFactory,
    ):
        self.client_factory = client_factory

    def whoami(self) -> UserInfoResponse:
        client = self.client_factory.get_client()
        return get_user_info(client.httpx_client, client.endpoint_url, client.log_curl_commands)


class FineTuningJobCommands(
    CollectionCRUDCommandsForImmutable[FineTuningJob, FineTuningJobRequest]
):
    command_group_name = "fine-tuning-job"
    command_group_title = "Manage model fine tuning jobs"

    def __init__(
        self,
        client_factory: EGPClientFactory,
    ):
        super().__init__(
            client_factory, FineTuningJob, FineTuningJobRequest, FineTuningJobCollection
        )

    @arg("filename", nargs="?", help="file containing fine tuning job configuration")
    @arg("--base-model-id", help="Model instance id of base model to fine tune")
    @arg("--training-dataset-id", help="Training dataset")
    @arg("--validation-dataset-id", help="Validation dataset")
    def create(
        self,
        filename: str,
        base_model_id: Optional[str] = None,
        training_dataset_id: Optional[str] = None,
        validation_dataset_id: Optional[str] = None,
    ) -> EntityT:
        request_dict = read_json_file(filename) if filename else {}
        if base_model_id:
            request_dict["base_model_id"] = base_model_id
        if training_dataset_id:
            request_dict["training_dataset_id"] = training_dataset_id
        if validation_dataset_id:
            request_dict["validation_dataset_id"] = validation_dataset_id
        if request_dict.get("base_model_id") is None:
            raise CommandError("base_model_id must be set")
        if request_dict.get("training_dataset_id") is None:
            raise CommandError("training_dataset_id must be set")
        return self._create(request_dict)

    def events(self, fine_tuning_job_id: str) -> EntityT:
        sub_path = f"{self._get_api_subpath_prefix()}/{fine_tuning_job_id}/events"
        collection = self._get_collection_instance()
        response = collection._get(
            sub_path=sub_path,
            timeout=10 * 60,  # 10 minutes
        )
        assert response.status_code == 200
        for entity_dict in response.json():
            yield FineTuningJobEvent(**entity_dict)


class TrainingDatasetCommands(
    CollectionCRUDCommandsForImmutable[TrainingDataset, TrainingDatasetRequest]
):
    """
    Upload training and evaluation datasets to EGP for use in fine tuning model jobs.
    """

    command_group_name = "training-dataset"
    command_group_title = "Datasets for model fine tuning jobs"

    def __init__(
        self,
        client_factory: EGPClientFactory,
    ):
        super().__init__(
            client_factory, TrainingDataset, TrainingDatasetRequest, TrainingDatasetCollection
        )

    @arg("filename", help="training dataset file to upload")
    def create(self, filename: str) -> EntityT:
        return TrainingDatasetCollection(self._client_factory.get_client()).create(
            file_name=filename
        )

    def list(self) -> Generator[EntityT, None, None]:
        set_formatting_options(
            FormattingOptions(
                table_columns=["id", "data_source", "created_at", "created_by_user_id"]
            )
        )
        return super().list()
