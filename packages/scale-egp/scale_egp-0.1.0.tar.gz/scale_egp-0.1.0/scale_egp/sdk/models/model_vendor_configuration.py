from enum import Enum
from typing import Dict, List, Literal, Optional

from pydantic import Field

try:
    from egp_api_backend.server.api.utils.model_utils import BaseModel
except Exception:
    from pydantic import BaseModel

from .model_enums import ModelEndpointType, ModelVendor


class GPUType(str, Enum):
    # Supported GPU models according to
    # https://github.com/scaleapi/launch-python-client/blob/794089b9ed58330a7ecac02eb5060bcc4ae3d409/launch/client.py#L1470-L1471
    NVIDIA_TESLA_T4 = "nvidia-tesla-t4"
    NVIDIA_AMPERE_A10 = "nvidia-ampere-a10"
    NVIDIA_AMPERE_A100 = "nvidia-ampere-a100"
    NVIDIA_AMPERE_A100e = "nvidia-ampere-a100e"


# The fields in CreateModelBundleConfiguration(BaseModel) are based on the arguments to
# create_model_bundle_from_streaming_enhanced_runnable_image_v2() in the Launch python client:
# https://github.com/scaleapi/launch-python-client/blob/794089b9ed58330a7ecac02eb5060bcc4ae3d409/launch/client.py#L752
# Differences between this class and the function arguments:
# * Separate fields for docker repository and image name.
# * Omitted fields: tag, healthcheck_route, predict_route, metadata - for these fields EGP user will need to
#   use the defaults provided by Launch.
#
class ModelBundleConfiguration(BaseModel):
    registry: str
    image: str
    tag: str
    # Note that the command field is mandatory since we're using create_model_bundle_from_streaming_enhanced_runnable_image_v2()
    # Omitting "command" triggers this error:
    # https://github.com/scaleapi/llm-engine/blob/53a1918ef3568b674b59a4e4e772501a7e1a1d69/model-engine/model_engine_server/domain/use_cases/model_endpoint_use_cases.py#L240
    command: List[str] = Field(default_factory=list)
    streaming_command: Optional[List[str]] = Field(None)
    env: Dict[str, str] = Field(default_factory=dict)
    readiness_initial_delay_seconds: int = Field(120)
    healthcheck_route: str = Field("/readyz")
    predict_route: str = Field("/predict")
    streaming_predict_route: Optional[str] = Field("/generate_streaming")

    @property
    def full_repository_name(self):
        return "/".join([self.registry, self.image])


# Autoscaling options which can be updated on a per-deployment basis, overriding the model configuration
# in the model template.
class LaunchAutoscalingConfiguration(BaseModel):
    # By default, we create model endpoints with min_workers = 0 so unused model endpoints can be autoscaled down to
    # 0 workers, costing nothing.
    min_workers: int = Field(0)
    max_workers: int = Field(1)
    per_worker: int = Field(
        10,
        # from: https://github.com/scaleapi/launch-python-client/blob/794089b9ed58330a7ecac02eb5060bcc4ae3d409/launch/client.py#L1444-L1465
        description="""
The maximum number of concurrent requests that an individual worker can
service. Launch automatically scales the number of workers for the endpoint so that
each worker is processing ``per_worker`` requests, subject to the limits defined by
``min_workers`` and ``max_workers``.

- If the average number of concurrent requests per worker is lower than
``per_worker``, then the number of workers will be reduced. - Otherwise,
if the average number of concurrent requests per worker is higher than
``per_worker``, then the number of workers will be increased to meet the elevated
traffic.

Here is our recommendation for computing ``per_worker``:

1. Compute ``min_workers`` and ``max_workers`` per your minimum and maximum
throughput requirements. 2. Determine a value for the maximum number of
concurrent requests in the workload. Divide this number by ``max_workers``. Doing
this ensures that the number of workers will "climb" to ``max_workers``.
""".strip(),
    )


# The fields in CreateModelEndpointConfig are copied from the arguments of the Launch client's create_model_endpoint()
# https://github.com/scaleapi/launch-python-client/blob/794089b9ed58330a7ecac02eb5060bcc4ae3d409/launch/client.py#L1391
class CreateModelEndpointConfig(LaunchAutoscalingConfiguration):
    cpus: int = Field(3)
    memory: str = Field("8Gi")
    storage: str = Field("16Gi")
    gpus: int = Field(0)
    gpu_type: Optional[GPUType] = Field(None)
    endpoint_type: ModelEndpointType = Field(ModelEndpointType.ASYNC)
    high_priority: Optional[bool] = Field(False)


class LaunchVendorConfiguration(BaseModel):
    """
    Configuration for launching a model using the Launch service which is an internal and
    self-hosted service developed by Scale that deploys models on Kubernetes.

    Attributes:
        vendor: The vendor of the model template
        bundle_config: The bundle configuration of the model template
        endpoint_config: The endpoint configuration of the model template
    """

    # this field is required for forward compatibility (other providers will have different "vendor" fields)
    vendor: Literal[ModelVendor.LAUNCH] = Field(ModelVendor.LAUNCH)
    bundle_config: ModelBundleConfiguration
    endpoint_config: Optional[CreateModelEndpointConfig] = CreateModelEndpointConfig()


class DeploymentVendorConfiguration(LaunchAutoscalingConfiguration):
    # this field is required for forward compatibility (other providers will have different "vendor" fields)
    vendor: Literal[ModelVendor.LAUNCH] = Field(ModelVendor.LAUNCH)


# Model vendor configuration only necessary for Launch models currently
ModelVendorConfiguration = LaunchVendorConfiguration
