from typing import Optional, Literal, Iterable, Union, List

from scale_egp.sdk.types.completions import (
    CompletionRequest,
    Completion,
    ModelParameters,
    ImageCompletionRequests,
)
from scale_egp.utils.api_utils import APIEngine


class CompletionCollection(APIEngine):
    _sub_path = "v2/completions"

    def create(
        self,
        model: Union[
            Literal[
                "gpt-4",
                "gpt-4-0613",
                "gpt-4-32k",
                "gpt-4-32k-0613",
                "gpt-4-vision-preview",
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
                "gemini-pro",
            ],
            str,
        ],
        prompt: str,
        images: Optional[List[ImageCompletionRequests]] = None,
        model_parameters: Optional[ModelParameters] = None,
    ) -> Completion:
        """
        Create a new LLM Completion.

        Args:
            model: The model to use for the completion.
            prompt: The prompt to use for the completion.
            model_parameters: The parameters to use for the model.

        Returns:
            The newly created Completion.
        """
        return Completion.from_dict(
            self._post(
                sub_path=self._sub_path,
                request=CompletionRequest(
                    model=model,
                    prompt=prompt,
                    images=images,
                    model_parameters=model_parameters,
                ),
            ).json()
        )

    def stream(
        self,
        model: Literal[
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
        prompt: str,
        images: Optional[List[ImageCompletionRequests]] = None,
        model_parameters: Optional[ModelParameters] = None,
    ) -> Iterable[Completion]:
        """
        Stream LLM Completions.

        Returns:
            The newly created Completion.
        """
        iterable_payloads = self._post_stream(
            sub_path=self._sub_path,
            request=CompletionRequest(
                model=model,
                prompt=prompt,
                images=images,
                model_parameters=model_parameters,
                stream=True,
            ),
        )
        if iterable_payloads:
            for response_dict in iterable_payloads:
                yield Completion.from_dict(response_dict)
        else:
            return []
