from __future__ import annotations

from enum import Enum
from scale_egp.sdk.models.model_enums import ModelEndpointType, ModelState, ModelType, ModelVendor


class TestCaseSchemaType(str, Enum):
    """
    An enum representing the different test case schema types.

    Attributes:
        GENERATION: If a TestCase specifies this schema type, it must have the following fields:

            - `input` [Required] The input to the generation model.
            - `expected_output` [Optional] The expected output of the generation model.
            - `expected_extra_info` [Optional] The expected extra info of the generation model.

            If a TestCaseResult specifies this schema type, it must have the following fields:

            - `generation_output` [Required] The output of the generation model.
            - `generation_extra_info` [Required] The extra info of the generation model.
    """

    GENERATION: str = "GENERATION"


class EvaluationStatus(str, Enum):
    """
    An enum representing the different possible statuses of an Evaluation.

    Attributes:
        PENDING: Denotes that an evaluation is pending.
        COMPLETED: Denotes that an evaluation is completed.
        FAILED: Denotes that an evaluation has failed.
    """

    PENDING: str = "PENDING"
    COMPLETED: str = "COMPLETED"
    FAILED: str = "FAILED"


class AuditStatus(str, Enum):
    """
    An enum representing the different possible audit statuses of a test case result.

    Attributes:
        UNAUDITED: Denotes that the test case result has not been aduited yet.
        FIXED: Denotes the test case result has been audited, and the mistakes have been corrected.
        APPROVED: Denotes the test case has been audited and approved.
    """

    UNAUDITED = "UNAUDITED"
    FIXED = "FIXED"
    APPROVED = "APPROVED"


class EvaluationType(str, Enum):
    """
    An enum representing the different types of evaluations.

    Currently only studio evaluations are supported.

    Attributes:
        STUDIO: Denotes that an evaluation is a studio evaluation.
    """

    STUDIO: str = "studio"


class QuestionType(str, Enum):
    """
    An enum representing the different types of questions.

    This is only used in a StudioEvaluationConfig to specify the type of a question.

    Attributes:
        CATEGORICAL: Denotes that a question is a categorical question.
        DROPDOWN: Denotes that a question is a dropdown question.
        FREE_TEXT: Denotes that a question is a free text question.
    """

    CATEGORICAL: str = "categorical"
    DROPDOWN: str = "dropdown"
    FREE_TEXT: str = "free_text"


class ExtraInfoSchema(str, Enum):
    """
    An enum representing the different types of extra info schemas.

    Denotes the type of the "info" field in the ExtraInfo model.

    Attributes:
        STRING: Denotes that the "info" field is a string.
    """

    STRING: str = "STRING"


class EmbeddingModelName(str, Enum):
    """
    An enum representing the different types of embedding models supported.

    Attributes:
        SENTENCE_TRANSFORMERS_ALL_MINILM_L12_V2:
            Denotes that the model is a sentence transformer model.
        SENTENCE_TRANSFORMERS_MULTI_QA_DISTILBERT_COS_V1:
            Denotes that the model is a sentence transformer model.
        SENTENCE_TRANSFORMERS_PARAPHRASE_MULTILINGUAL_MPBET_BASE_V2:
            Denotes that the model is a sentence transformer model.
        OPENAI_TEXT_EMBEDDING_ADA_002:
            Denotes that the model is an openai text embedding model.
        OPENAI_TEXT_EMBEDDING_3_SMALL:
            Denotes that the model is an openai text embedding model.
        OPENAI_TEXT_EMBEDDING_3_LARGE:
            Denotes that the model is an openai text embedding model.
        COHERE_TEXT_EMBEDDING_ENGLISH_3:
             Denotes that the model is a cohere text embedding model.
        COHERE_TEXT_EMBEDDING_ENGLISH_LIGHT_3:
             Denotes that the model is a cohere text embedding model.
        COHERE_TEXT_EMBEDDING_MULTILINGUAL_3:
             Denotes that the model is a cohere text embedding model.
    """

    SENTENCE_TRANSFORMERS_ALL_MINILM_L12_V2 = "sentence-transformers/all-MiniLM-L12-v2"
    SENTENCE_TRANSFORMERS_MULTI_QA_DISTILBERT_COS_V1 = (
        "sentence-transformers/multi-qa-distilbert-cos-v1"
    )
    SENTENCE_TRANSFORMERS_PARAPHRASE_MULTILINGUAL_MPBET_BASE_V2 = (
        "sentence-transformers/paraphrase-multilingual-mpnet-base-v2"
    )
    OPENAI_TEXT_EMBEDDING_ADA_002 = "openai/text-embedding-ada-002"
    OPENAI_TEXT_EMBEDDING_3_SMALL = "openai/text-embedding-3-small"
    OPENAI_TEXT_EMBEDDING_3_LARGE = "openai/text-embedding-3-large"
    SENTENCE_TRANSFORMERS_MULTI_QA_FINETUNE = "finetuned/multi-qa-mpnet-base-dot-v1"
    COHERE_TEXT_EMBEDDING_ENGLISH_3 = "embed-english-v3.0"
    COHERE_TEXT_EMBEDDING_ENGLISH_LIGHT_3 = "embed-english-light-v3.0"
    COHERE_TEXT_EMBEDDING_MULTILINGUAL_3 = "embed-multilingual-v3.0"

class DataSource(str, Enum):
    """
    An enum representing the different types of data sources supported.

    Attributes:
        S3: Denotes that the data source is S3.
    """

    S3: str = "S3"
    SHAREPOINT: str = "SharePoint"
    GOOGLE_DRIVE: str = "GoogleDrive"
    LOCAL_CHUNKS: str = "LocalChunks"


class DeduplicationStrategy(str, Enum):
    """
    An enum representing the different types of deduplication strategies supported.

    Attributes:
        OVERWRITE: Denotes that the deduplication strategy is to overwrite.
        FAIL: Denotes that the deduplication strategy is to fail.
    """

    OVERWRITE = "Overwrite"
    FAIL = "Fail"


class ChunkingStrategy(str, Enum):
    """
    An enum representing the different types of chunking strategies supported.

    Attributes:
        CHARACTER: Denotes that the chunking strategy is to chunk by character.
    """

    CHARACTER = "character"


class ArtifactSource(str, Enum):
    """
    An enum representing the different types of artifact sources supported.

    Attributes:
        S3: Denotes that the artifact source is S3.
        CONFLUENCE: Denotes that the artifact source is Confluence.
        SHAREPOINT: Denotes that the artifact source is SharePoint.
        GOOGLE_DRIVE: Denotes that the artifact source is Google Drive.
        LOCAL_CHUNKS: Denotes that the artifact source comes from chunks directly uploaded via the
            API.
    """

    S3 = "S3"
    CONFLUENCE = "Confluence"
    SHAREPOINT = "SharePoint"
    GOOGLE_DRIVE = "GoogleDrive"
    LOCAL_CHUNKS = "LocalChunks"


class StatusType(str, Enum):
    PENDING = "Pending"
    RUNNING = "Running"
    COMPLETED = "Completed"
    FAILED = "Failed"
    CANCELED = "Canceled"
    CHUNKING = "Chunking"
    DELETING = "Deleting"
    UPLOADING = "Uploading"


class UploadJobStatus(str, Enum):
    """
    An enum representing the different types of upload job statuses supported.

    Attributes:
        RUNNING: Denotes that the upload job is running.
        COMPLETED: Denotes that the upload job is completed.
        FAILED: Denotes that the upload job has failed.
        CANCELED: Denotes that the upload job has been canceled.
    """

    RUNNING = StatusType.RUNNING.value
    COMPLETED = StatusType.COMPLETED.value
    FAILED = StatusType.FAILED.value
    CANCELED = StatusType.CANCELED.value


class ChunkUploadStatus(str, Enum):
    """
    An enum representing the different types of chunk upload statuses supported.

    Attributes:
        PENDING: Denotes that the chunk upload is pending.
        COMPLETED: Denotes that the chunk upload is completed.
        FAILED: Denotes that the chunk upload has failed.
    """

    PENDING = StatusType.PENDING.value
    COMPLETED = StatusType.COMPLETED.value
    FAILED = StatusType.FAILED.value


class CrossEncoderModelName(str, Enum):
    """
    An enum representing the different types of cross encoder models supported.

    Attributes:
        CROSS_ENCODER_MS_MARCO_MINILM_L12_V2: Denotes that the model is a cross encoder model.
        CROSS_ENCODER_MMARCO_MMINILMV2_L12_H384_V1: Denotes that the model is a cross encoder model.
    """

    CROSS_ENCODER_MS_MARCO_MINILM_L12_V2 = "cross-encoder/ms-marco-MiniLM-L-12-v2"
    CROSS_ENCODER_MMARCO_MMINILMV2_L12_H384_V1 = "cross-encoder/mmarco-mMiniLMv2-L12-H384-v1"


class AgentAction(str, Enum):
    """
    An enum representing the different types of agent actions supported.

    Attributes:
        TOOL_REQUEST: Denotes that the agent output contains a request for the user to use a tool.
        CONTENT: Denotes that the agent output contains final content.
    """

    TOOL_REQUEST = "tool_request"
    CONTENT = "content"


class GPUType(str, Enum):
    # Supported GPU models according to
    # https://github.com/scaleapi/launch-python-client/blob
    # /794089b9ed58330a7ecac02eb5060bcc4ae3d409/launch/client.py#L1470-L1471
    NVIDIA_TESLA_T4 = "nvidia-tesla-t4"
    NVIDIA_AMPERE_A10 = "nvidia-ampere-a10"
    NVIDIA_AMPERE_A100 = "nvidia-ampere-a100"
    NVIDIA_AMPERE_A100e = "nvidia-ampere-a100e"


class EmbeddingConfigType(str, Enum):
    BASE = "base"
    MODELS_API = "models_api"

