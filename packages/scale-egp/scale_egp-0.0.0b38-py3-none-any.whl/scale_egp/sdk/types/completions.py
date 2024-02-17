from __future__ import annotations

from typing import Literal, Optional, List, Union

from pydantic import Field

from scale_egp.utils.model_utils import BaseModel


class CompletionContent(BaseModel):
    """
    A data model representing the completion text and the finish reason.

    Attributes:
        text: Completion text. If streaming, this field will contain each packet of text.
        finish_reason: Reason the LLM finished generating text.
    """

    text: str
    finish_reason: Optional[str] = None


class TokenUsage(BaseModel):
    """
    A data model representing LLM token usage numbers.

    Attributes:
        prompt: Number of tokens in the prompt.
        completion: Number of tokens in the completion.
        total: Total number of tokens in both the prompt and the completion.
    """

    prompt: Optional[int] = None
    completion: Optional[int] = None
    total: int


class Completion(BaseModel):
    """
    A data model representing a completion.

    Attributes:
        completion: The actual completion text and the finish reason.
        token_usage: Token usage numbers. If streaming, this field is null until the stream
            completes, at which point it will be populated (if supported).
    """

    completion: CompletionContent
    token_usage: Optional[TokenUsage] = None


class ModelParameters(BaseModel):
    """
    A data model representing the configuration parameters for the completion model.

    Attributes:
        temperature: What sampling temperature to use, between [0, 1]. Higher values like 0.8
            will make the output more random, while lower values like 0.2 will make it more
            focused and deterministic. Setting temperature=0.0 will enable fully deterministic
            (greedy) sampling.
        stop_sequences: List of up to 4 sequences where the API will stop generating further
            tokens. The returned text will not contain the stop sequence.
        max_tokens: The maximum number of tokens to generate in the completion. The token count
            of your prompt plus max_tokens cannot exceed the model's context length. If not,
            specified, max_tokens will be determined based on the model used:

            | Model API family | Model API default | EGP applied default |
            | --- | --- | --- |
            | OpenAI Completions | [`16`](https://platform.openai.com/docs/api-reference/completions/create#max_tokens) | `context window - prompt size` |
            | OpenAI Chat Completions | [`context window - prompt size`](https://platform.openai.com/docs/api-reference/chat/create#max_tokens) | `context window - prompt size` |
    """

    temperature: float = Field(default=0.2, ge=0.0, le=1.0)
    stop_sequences: Optional[List[str]] = Field(default=None, max_items=4)
    max_tokens: Optional[int] = Field(default=None)

class ImageCompletionRequests(BaseModel):
    image_url: str = Field(
        ...,
        description="Image URL to run image completion on.",
    )
    detail: Optional[str] = Field(
        "auto", description="Detail to run image completion with. Defaults to auto"
    )

class CompletionRequest(BaseModel):
    model: Union[
        Literal[
            "gpt-4",
            "gpt-4-0613",
            "gpt-4-32k",
            "gpt-4-32k-0613",
            "gpt-3.5-turbo",
            "gpt-3.5-turbo-0613",
            "gpt-3.5-turbo-16k",
            "gpt-3.5-turbo-16k-0613",
            "text-davinci-003",
            "text-davinci-002",
            "text-curie-001",
            "text-babbage-001",
            "text-ada-001",
            "claude-instant-1",
            "claude-instant-1.1",
            "claude-2",
            "claude-2.0",
            "llama-7b",
            "llama-2-7b",
            "llama-2-7b-chat",
            "llama-2-13b",
            "llama-2-13b-chat",
            "llama-2-70b",
            "llama-2-70b-chat",
            "falcon-7b",
            "falcon-7b-instruct",
            "falcon-40b",
            "falcon-40b-instruct",
            "mpt-7b",
            "mpt-7b-instruct",
            "flan-t5-xxl",
            "mistral-7b",
            "mistral-7b-instruct",
            "mixtral-8x7b",
            "mixtral-8x7b-instruct",
            "llm-jp-13b-instruct-full",
            "llm-jp-13b-instruct-full-dolly",
            "zephyr-7b-alpha",
            "zephyr-7b-beta",
            "codellama-7b",
            "codellama-7b-instruct",
            "codellama-13b",
            "codellama-13b-instruct",
            "codellama-34b",
            "codellama-34b-instruct",
        ],
        str,
    ] = Field(
        ...,
        description="The ID of the model to use for completions.\n\n"
                    "Users have two options:\n"
                    "- Option 1: Use one of the supported models from the dropdown.\n"
                    "- Option 2: Enter the ID of a custom model.\n\n"
                    "Note: For custom models we currently only support models finetuned using "
                    "using the Scale-hosted LLM-Engine API.",
    )
    prompt: str = Field(
        ...,
        description="Prompt for which to generate the completion.\n\n"
                    "Good prompt engineering is crucial to getting performant results from the "
                    "model. If you are having trouble getting the model to perform well, "
                    "try writing a more specific prompt here before trying more expensive "
                    "techniques such as swapping in other models or finetuning the underlying LLM.",
    )
    images: Optional[List[ImageCompletionRequests]] = Field(
        default=None,
        description="List of image urls to be used for image based completions. Leave empty for text based completions.",
    )
    model_parameters: Optional[ModelParameters] = Field(
        default=ModelParameters(temperature=0.2),
        description="Configuration parameters for the completion model, such as temperature, "
                    "max_tokens, and stop_sequences.\n\n"
                    "If not specified, the default value are:\n"
                    "- temperature: 0.2\n"
                    "- max_tokens: None (limited by the model's max tokens)\n"
                    "- stop_sequences: None",
    )
    stream: bool = Field(
        default=False,
        description="Whether or not to stream the response.\n\n"
                    "Setting this to True will stream the completion in real-time.",
    )
