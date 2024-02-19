import os
from abc import ABC, abstractmethod
from typing import Dict, Optional

import httpx

from scale_egp.sdk.collections.application_specs import ApplicationSpecCollection
from scale_egp.sdk.collections.chunks import ChunkCollection
from scale_egp.sdk.collections.completions import CompletionCollection
from scale_egp.sdk.collections.evaluation_datasets import EvaluationDatasetCollection
from scale_egp.sdk.collections.evaluations import EvaluationCollection
from scale_egp.sdk.collections.knowledge_bases import KnowledgeBaseCollection
from scale_egp.sdk.collections.model_groups import ModelGroupCollection
from scale_egp.sdk.collections.model_templates import ModelTemplateCollection
from scale_egp.sdk.collections.models import ModelInstanceCollection
from scale_egp.sdk.collections.studio_projects import StudioProjectCollection
from scale_egp.sdk.types.user_info import UserInfoResponse
from scale_egp.utils.api_utils import APIEngine
from scale_egp.utils.model_utils import BaseModel

DEFAULT_ENDPOINT_URL = "https://api.egp.scale.com"


class EGPClientConfig(BaseModel):
    proxies: Optional[Dict[str, httpx.Proxy]] = None
    timeout: Optional[float] = None


class EGPClientConfigGenerator(ABC):

    @abstractmethod
    def generate(self, *args, **kwargs) -> EGPClientConfig:
        pass


class EGPClient:
    """
    The EGP client object. This is the main entry point for interacting with EGP.

    From this client you can access "collections" which interact with various EGP components.
    Each collection will have various methods that interact with the API. Some collections may
    have sub-collections to signify a hierarchical relationship between the entities they represent.

    For users within strict firewall environments, the client can be configured to use a proxy via the config_generator
    argument. Here is an example of how to do Kerberos Authentication through a proxy.

    ```python
    import httpx
    from requests_kerberos import HTTPKerberosAuth

    from scale_egp.sdk.client import EGPClient, EGPClientConfig, EGPClientConfigGenerator

    class KerberosProxyConfigGenerator(EGPClientConfigGenerator):

        def __init__(self, proxy_url: str):
            self._proxy_url = proxy_url

        def generate(self) -> EGPClientConfig:
            return EGPClientConfig(proxies={
                "http://": httpx.Proxy(url=self._proxy_url, headers=self._get_proxy_headers()),
                "https://": httpx.Proxy(url=self._proxy_url, headers=self._get_proxy_headers()),
            })

        def _get_proxy_headers(self) -> httpx.Headers:
            auth = HTTPKerberosAuth()
            negotiate_details = auth.generate_request_header(None, parse_url(self._proxy_url).host, is_preemptive=True)
            return httpx.Headers({"Proxy-Authorization": negotiate_details}, encoding="utf-8")

    client = EGPClient(
        api_key="<API_KEY>",
        config_generator=KerberosProxyConfigGenerator("http://proxy.example.com:3128")
    )
    ```
    """

    def __init__(
        self,
        api_key: str = None,
        account_id: str = None,
        endpoint_url: str = None,
        config_generator: Optional[EGPClientConfigGenerator] = None,
        log_curl_commands: Optional[bool] = None,
    ):
        """
        Args:
            api_key: The EGP API key to use. If not provided, the `EGP_API_KEY` environment
                variable will be used. Enterprise customers of EGP should use the API key provided
                to them by their Scale account manager.
            account_id: The EGP account ID to use. If not provided, the `ACCOUNT_ID` environment
                variable will be used.
            endpoint_url: The EGP endpoint URL to use. If not provided, the `EGP_ENDPOINT_URL`
                environment variable will be used. If that is not set, the default EGP endpoint
                URL `https://api.egp.scale.com` will be used. Enterprise customers of EGP should
                use the endpoint URL provided by their Scale account manager.
            config_generator: An instance of EGPClientConfigGenerator, which must implement a generate function that
                returns an EGPClientConfig object. The client config will be used to inject httpx.Client arguments on
                demand per request. This is useful for dynamically setting proxies, timeouts, etc.
        """
        api_key = api_key or os.environ.get("EGP_API_KEY")
        endpoint_url = endpoint_url or os.environ.get("EGP_ENDPOINT_URL", DEFAULT_ENDPOINT_URL)
        self.log_curl_commands = (
            log_curl_commands
            if log_curl_commands is not None
            else os.environ.get("EGP_LOG_CURL_COMMAND", "").upper() == "TRUE"
        )
        self.api_key = api_key
        self.endpoint_url = endpoint_url if endpoint_url.endswith("/") else endpoint_url + "/"
        self.config_generator = config_generator

        if not self.api_key:
            raise ValueError("No API key provided. Please provide an API key.")
        if not self.endpoint_url:
            raise ValueError("No endpoint URL provided. Please provide an endpoint URL.")

        self.account_id = account_id
        if self.account_id is None:
            self.account_id = os.environ.get("EGP_ACCOUNT_ID")
        if self.account_id is None:
            # TODO: if there are more accounts, taking the first one might not be the most
            #  intuitive logic
            self.account_id = self.user_info().accounts[0].account.id

    def user_info(self) -> UserInfoResponse:
        # TODO: this is an exception, should use collections instead
        api_engine = APIEngine(self)
        response = api_engine._get(sub_path="user-info") # noqa
        return UserInfoResponse.from_dict(response.json())

    def knowledge_bases(self) -> KnowledgeBaseCollection:
        """
        Returns the Knowledge Base Collection.

        Use this collection to create and manage Knowledge Bases.

        Returns:
            The Knowledge Base Collection.
        """
        return KnowledgeBaseCollection(self)

    def chunks(self) -> ChunkCollection:
        """
        Returns the Chunk Collection.

        Use this collection to create and manage Chunks.

        Returns:
            The Chunk Collection.
        """
        return ChunkCollection(self)

    def completions(self) -> CompletionCollection:
        """
        Returns the Completion Collection.

        Use this collection if you want to make request to an LLM to generate a completion.

        Returns:
            The Completion Collection.
        """
        return CompletionCollection(self)

    def model_templates(self) -> ModelTemplateCollection:
        """
        Returns the Model Template Collection.

        Use this collection to create and manage Model Templates.

        In order to prevent any user from creating any arbitrary model, users with more advanced
        permissions can create Model Templates. Models can only be created from Model Templates.
        This allows power users to create a set of approved models that other users can derive
        from.

        When the model is instantiated from a model template, the settings from the template
        are referenced to reserve the required computing resources, pull the correct docker image,
        etc.

        Returns:
            The Model Template Collection.
        """
        return ModelTemplateCollection(self)

    def models(self) -> ModelInstanceCollection:
        """
        Returns the Model Collection.

        Use this collection to create and manage Models.

        in generative AI applications, there are many types of models that are useful. For
        example, embedding models are useful for translating natural language
        into query-able vector representations, reranking models are useful when a vector
        database's query results need to be re-ranked based on some other criteria, and LLMs
        are useful for generating text from a prompt.

        This collection allows you to create, deploy, and manage any custom model you choose if
        none of the built-in models fit your use case.

        Returns:
            The Model Collection.
        """
        return ModelInstanceCollection(self)

    def model_groups(self) -> ModelGroupCollection:
        """
        Returns the Model Group Collection.

        Use this collection to create and manage Model Groups.

        TODO: Write extensive documentation on Model Groups

        Returns:
            The Model Group Collection.
        """
        return ModelGroupCollection(self)

    def evaluation_datasets(self) -> EvaluationDatasetCollection:
        """
        Returns the Evaluation Dataset Collection.

        Use this collection to create and manage Evaluation Datasets or Test Cases within them.

        Returns:
            The Evaluation Dataset Collection.
        """
        return EvaluationDatasetCollection(self)

    def studio_projects(self) -> StudioProjectCollection:
        """
        Returns the Studio Project Collection.

        Use this collection to create and manage Studio Projects. These are projects that will be
        used to annotate data in the Scale [Studio](https://scale.com/studio) platform.

        Returns:
            The Studio Project Collection.
        """
        return StudioProjectCollection(self)

    def application_specs(self) -> ApplicationSpecCollection:
        """
        Returns the Application Spec Collection.

        Use this collection to create and manage Application Specs. These are specifications for
        the AI application you are building. They contain information about the AI application
        such as its name and description. They are useful to associate your Evaluations with so
        evaluations can be grouped by application.

        Returns:
            The Application Spec Collection.
        """
        return ApplicationSpecCollection(self)

    def evaluations(self) -> EvaluationCollection:
        """
        Returns the Evaluation Collection.

        Use this collection to create and manage Evaluations and Test Case Results.

        Evaluations are used to evaluate the performance of AI applications. Users are
        expected to follow the following procedure to perform an evaluation:

        1. Select an Evaluation Dataset
        2. Iterate through the dataset's Test Cases:
          - For each of these test cases, the user use their AI application to generate output
          data on each test case input prompt.
        3. The user then submits this data as as batch of Test Case Results associated
        with an Evaluation.
        4. Annotators will asynchronously log into the Scale [Studio](https://scale.com/studio)
        platform to annotate the submitted Test Case Results. The annotations will be used to
        evaluate the performance of the AI application.
        5. The submitting user will check back on their Test Case Results to see if the `result`
        field was populated. If so, the evaluation is complete and the user can use the annotation
        data to evaluate the performance of their AI application.

        Returns:
            The Evaluation Collection.
        """
        return EvaluationCollection(self)
