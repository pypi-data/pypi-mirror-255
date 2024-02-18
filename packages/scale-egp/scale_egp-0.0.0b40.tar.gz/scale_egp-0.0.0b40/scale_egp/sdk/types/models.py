import random
import string

from datetime import datetime
from typing import Optional, Any, Dict, List, Tuple, Union, Literal, TypeVar, Type

from pydantic import Field, Extra, BaseConfig, create_model

from scale_egp.sdk.enums import ModelVendor, AgentAction, ModelType
from scale_egp.sdk.types.agents import ActionContext, Tool
from scale_egp.sdk.types.memory_strategy import MemoryStrategy
from scale_egp.sdk.types.message import Message
from scale_egp.utils.model_utils import Entity, BaseModel
from scale_egp.sdk.models.model_vendor_configuration import DeploymentVendorConfiguration


ParameterValueType = Union[str, int, float, bool]


class ParameterBindings(BaseModel):
    bindings: Dict[str, ParameterValueType]

    class Config:
        extra = Extra.forbid


class ModelInstance(Entity):
    """
    Entity for all models, including both self-hosted and 3rd party, base, and fine-tuned models.

    Attributes:
        id: The unique identifier of the model.
        created_at: The date and time when the entity was created in ISO format.
        account_id: The ID of the account that owns the given entity.
        created_by_user_id: The user who originally created the entity.
        name: The name of the model
        description: The description of the model
        model_vendor: The vendor of the model
        base_model_id: The ID of the base model
        base_model_metadata: Metadata for the base model
        model_template_id: The ID of the model template
        model_group_id: Model group that the entity belongs to
    """

    name: str
    model_type: ModelType
    model_vendor: Optional[ModelVendor] = Field(None)
    model_creation_parameters: Optional[Dict[str, Any]] = Field(None)
    base_model_id: Optional[str] = Field(None)
    base_model_metadata: Optional[Dict[str, Any]] = Field(None)
    description: Optional[str] = Field(None)
    model_template_id: Optional[str] = Field(None)
    id: str = Field(..., description="The unique identifier of the entity.")
    created_at: datetime = Field(
        ..., description="The date and time when the entity was created in ISO format."
    )
    account_id: str = Field(..., description="The ID of the account that owns the given entity.")
    created_by_user_id: str = Field(..., description="The user who originally created the entity.")
    model_group_id: Optional[str] = Field(None)
    request_schema: Dict[str, Any]
    response_schema: Dict[str, Any]


class ModelInstanceRequest(BaseModel):
    name: str
    model_type: ModelType
    model_vendor: Optional[ModelVendor] = Field(None)
    model_creation_parameters: Optional[Dict[str, Any]] = Field(None)
    base_model_id: Optional[str] = Field(None)
    base_model_metadata: Optional[Dict[str, Any]] = Field(None)
    description: Optional[str] = Field(None)
    model_template_id: Optional[str] = Field(None)
    account_id: str = Field(..., description="The ID of the account that owns the given entity.")
    model_group_id: Optional[str] = Field(None)
    training_data_card: Optional[str] = Field(None)
    model_card: Optional[str] = Field(None)


class ModelDeployment(Entity):
    """
    Deployment of a model

    Attributes:
        id: The unique identifier of the model deployment.
    """

    id: str
    name: str
    model_creation_parameters: Optional[Dict[str, Any]]
    vendor_configuration: Optional[DeploymentVendorConfiguration] = Field(None)
    model_instance_id: Optional[str]
    status: Optional[str]  # TODO <cathy-scale>: enum
    # TODO <cathy-scale>: put these repeated fields in a parent class
    created_at: datetime = Field(
        ..., description="The date and time when the entity was created in ISO format."
    )
    account_id: str = Field(..., description="The ID of the account that owns the given entity.")
    created_by_user_id: str = Field(..., description="The user who originally created the entity.")


class ModelDeploymentRequest(BaseModel):
    name: str
    vendor_configuration: Optional[DeploymentVendorConfiguration] = Field(None)
    model_creation_parameters: Optional[Dict[str, Any]] = Field(None)
    account_id: str = Field(..., description="The ID of the account that owns the given entity.")


class BaseModelResponse(BaseModel):
    class Config(BaseModel.Config):
        extra = Extra.forbid


class AgentResponse(BaseModelResponse):
    """
    Response schema for agents.

    See the [Execute Agent REST API](https://scale-egp.readme.io/reference/execute_agent) for more
    information.

    Attributes:
        action: The action that the agent performed.
        context: Context object containing the output payload. This will contain a key for all
            actions that the agent can perform. However, only the key corresponding to
            the action that the agent performed have a populated value. The rest of the
            values will be `null`.
    """

    action: AgentAction = Field(...)
    context: ActionContext = Field(...)


class BaseModelRequest(BaseModel):
    model_request_parameters: Optional["ParameterBindings"] = Field(None)

    class Config(BaseModel.Config):
        extra = Extra.forbid


class AgentRequest(BaseModelRequest):
    """
    Response schema for agents.
    See the [Execute Agent REST API](https://scale-egp.readme.io/reference/execute_agent) for more
    information.

    Attributes:
        memory_strategy: The memory strategy to use for the agent. A memory strategy
            is a way to prevent the underlying LLM's context limit from being exceeded.
            Each memory strategy uses a different technique to condense the input message
            list into a smaller payload for the underlying LLM.
        tools: The list of specs of tools that the agent can use. Each spec must contain
            a `name` key set to the name of the tool, a `description` key set to the
            description of the tool, and an `arguments` key set to a JSON Schema
            compliant object describing the tool arguments.

            The name and description of each tool is used by the agent to decide when to
            use certain tools. Because some queries are complex and may require multiple
            tools to complete, it is important to make these descriptions as
            informative as possible. If a tool is not being chosen when it should,
            it is common practice to tune the description of the tool to make it more
            apparent to the agent when the tool can be used effectively.
        messages: The list of messages in the conversation.
        instructions: The initial instructions to provide to the agent.

            Use this to guide the agent to act in more specific ways. For example, if you
            have specific rules you want to restrict the agent to follow you can specify them here.
            For example, if I want the agent to always use certain tools before others,
            I can write that rule in these instructions.

            Good prompt engineering is crucial to getting performant results from the
            agent. If you are having trouble getting the agent to perform well,
            try writing more specific instructions here before trying more expensive
            techniques such as swapping in other models or finetuning the underlying LLM.

    """

    memory_strategy: Optional[MemoryStrategy] = Field(default=None)
    tools: List[Tool] = Field(...)
    messages: List[Message] = Field(...)
    instructions: Optional[str] = Field(
        default="You are an AI assistant that helps users with their questions. You "
        "can answer questions directly or acquire information from any of the "
        "attached tools to assist you. Always answer the user's most recent query to the "
        "best of your knowledge.\n\n"
        "When asked about what tools are available, you must list each attached "
        "tool's name and description. When asked about what you can do, mention "
        "that in addition to your normal capabilities, you can also use the attached "
        "tools by listing their names and descriptions. You cannot use any other tools "
        "other than the ones provided to you explicitly.",
    )


class ChatCompletionRequest(BaseModelRequest):
    """
    Request schema for chat completion models.

    Attributes:
        temperature: What sampling temperature to use, between [0, 1]. Higher values like 0.8
            will make the output more random, while lower values like 0.2 will make it
            more focused and deterministic. Setting temperature=0.0 will enable fully
            deterministic
            (greedy) sampling.
        stop_sequences: List of up to 4 sequences where the API will stop generating further tokens.
            The returned text will not contain the stop sequence.
        max_tokens: The maximum number of tokens to generate in the completion. The token count
            of your prompt plus max_tokens cannot exceed the model's context length. If not,
            specified, max_tokens will be determined based on the model used.
        messages: List of messages for the chat completion to consider when generating a response.
    """

    temperature: float = Field(
        default=0.2,
        ge=0.0,
        le=1.0,
    )
    stop_sequences: Optional[List[str]] = Field(
        default=None,
        max_items=4,
    )
    max_tokens: Optional[int] = Field(
        default=None,
    )
    messages: List[Message]


class ChatCompletionResponse(BaseModelResponse):
    """
    Response schema for chat completion models.

    Attributes:
        message: The generated message from the chat completion model.
        finish_reason: The reason the chat completion finished.
    """

    message: Message
    finish_reason: Optional[str]


class CompletionRequest(BaseModelRequest):
    """
    Request schema for completion models.

    Attributes:
        temperature: What sampling temperature to use, between [0, 1]. Higher values like 0.8
            will make the output more random, while lower values like 0.2 will make it
            more focused and deterministic. Setting temperature=0.0 will enable fully
            deterministic
            (greedy) sampling.
        stop_sequences: List of up to 4 sequences where the API will stop generating further tokens.
            The returned text will not contain the stop sequence.
        max_tokens: The maximum number of tokens to generate in the completion. The token count
            of your prompt plus max_tokens cannot exceed the model's context length. If not,
            specified, max_tokens will be determined based on the model used.
        prompts: List of prompts to generate completions for.
    """

    temperature: float = Field(
        default=0.2,
        ge=0.0,
        le=1.0,
    )
    stop_sequences: Optional[List[str]] = Field(
        default=None,
        max_items=4,
    )
    max_tokens: Optional[int] = Field(
        default=None,
    )
    prompts: List[str]


class CompletionResponse(BaseModelResponse):
    """
    Response schema for completion models.

    Attributes:
        completions: List of prompt, completion pairs.
        finish_reason: The reason the completion finished.
    """

    # List of prompt, completion pairs, eg: [("prompt", ["completion1", "completion2", ...]), ...]
    completions: List[Tuple[str, List[str]]]
    finish_reason: Optional[str]


class EmbeddingRequest(BaseModelRequest):
    """
    Request schema for embedding models.

    Attributes:
        texts: List of texts to get embeddings for.
    """

    texts: List[str]


class EmbeddingResponse(BaseModelResponse):
    """
    Response schema for embedding models.

    Attributes:
        embeddings: List of text, embedding pairs.
    """

    # List of text, embedding pairs, eg: [("text to embed", [1.0, 1.05, 2.07, ...]), ...]
    embeddings: List[Tuple[str, List[float]]]


class RerankingRequest(BaseModelRequest):
    """
    Request schema for reranking models.

    Attributes:
        query: Query to rerank chunks against in order of relevance.
        chunks: List of chunks to rerank.
    """

    query: str
    chunks: List[str]


class RerankingResponse(BaseModelResponse):
    """
    Response schema for reranking models.

    Attributes:
        chunk_scores: List of scores for each chunk in the same order as the input chunks.
    """

    chunk_scores: List[float]


def get_random_string(length=8):
    # choose from all lowercase letter
    letters = string.ascii_lowercase
    return "".join(random.choice(letters) for i in range(length))


class ParameterSchemaField(BaseModel):
    """
    The schema used to specify the type and info about each parameter to be passed for model
    creation.

    Attributes:
        name: Name of the parameter.
        type: Type of the parameter.
        description: Description of the parameter.
        required: Whether the parameter is required or not.
    """

    name: str
    type: Union[Literal["str"], Literal["int"], Literal["float"], Literal["bool"]]
    description: str
    required: bool  # default is optional


class ParameterSchema(BaseModel):
    """
    The schema used to specify the parameters to be passed for model creation.

    Attributes:
        parameters: List of parameter schema fields.
    """

    parameters: List[ParameterSchemaField]


BaseModelT = TypeVar("BaseModelT", bound=BaseModel)


class ParameterSchemaModelConfig(BaseConfig):
    extra = Extra.forbid


def parameter_schema_to_model(
    model_name: str, parameter_schema: ParameterSchema
) -> Type[BaseModelT]:
    return create_model(
        model_name,
        __config__=ParameterSchemaModelConfig,
        **{
            field.name: (field.type, ...) if field.required else (field.type, None)
            for field in parameter_schema.parameters
        },
    )
