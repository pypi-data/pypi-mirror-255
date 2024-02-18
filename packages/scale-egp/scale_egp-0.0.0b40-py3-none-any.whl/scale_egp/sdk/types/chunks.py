from __future__ import annotations

from typing import Optional, List, Dict, Any, Union, Literal

from pydantic import Field

from scale_egp.sdk.enums import CrossEncoderModelName
from scale_egp.utils.model_utils import Entity, BaseModel


class Chunk(Entity):
    """
    A data model representing a chunk.

    Attributes:
        chunk_id: The unique ID of the chunk
        text: The text associated with the chunk
        score: A number between 0 and 1 representing how similar a chunk's embedding is to the
            query embedding. Higher numbers mean that this chunk is more similar.
        embedding: The vector embedding of the text associated with the chunk
        metadata: Any additional key value pairs of information stored with the chunk
    """

    chunk_id: str
    text: str
    score: Optional[float]
    embedding: Optional[List[float]]
    metadata: Optional[Dict[str, Any]] = Field(default_factory=dict)


class CrossEncoderRankParams(BaseModel):
    """
    A data model representing the parameters needed for cross encoder ranking.

    Attributes:
        cross_encoder_model: The cross encoder model to use for ranking.
    """
    cross_encoder_model: Literal[
        "cross-encoder/ms-marco-MiniLM-L-12-v2",
        "cross-encoder/mmarco-mMiniLMv2-L12-H384-v1",
    ] = Field(
        default=CrossEncoderModelName.CROSS_ENCODER_MS_MARCO_MINILM_L12_V2,
        description="Cross encoder model to use when ranking.",
    )


class CrossEncoderRankStrategy(BaseModel):
    """
    A data model representing the cross encoder ranking strategy.

    Attributes:
        method: The name of the rank strategy. Must be `cross_encoder`.
        params: The parameters needed for ranking.
    """
    method: Literal["cross_encoder"] = Field(
        default="cross_encoder",
        const=True,
        description="The name of the rank strategy. Must be `cross_encoder`.",
    )
    params: CrossEncoderRankParams = Field(
        default=CrossEncoderRankParams(),
        description="The parameters needed for ranking.",
    )


class RougeRankParams(BaseModel):
    """
    A data model representing the parameters needed for Rouge ranking.

    Attributes:
        metric: Rouge type, can be n-gram based (e.g. rouge1, rouge2) or longest common
            subsequence (rougeL or rougeLsum)
        score: Metric to use from Rouge score
    """
    metric: str = Field(
        default="rouge2",
        description="Rouge type, can be n-gram based (e.g. rouge1, rouge2) or longest common "
        "subsequence (rougeL or rougeLsum)",
    )
    score: Literal["precision", "recall", "fmeasure"] = Field(
        default="recall", description="Metric to use from Rouge score"
    )


class RougeRankStrategy(BaseModel):
    """
    A data model representing the Rouge ranking strategy.

    Attributes:
        method: The name of the rank strategy. Must be `rouge`.
        params: The parameters needed for ranking.
    """
    method: Literal["rouge"] = Field(
        default="rouge",
        const=True,
        description="The name of the rank strategy.",
    )
    params: RougeRankParams = Field(
        default=RougeRankParams(),
        description="The parameters needed for ranking.",
    )


class ModelRankParams(BaseModel):
    """
    A data model representing the parameters needed for ranking.

    Attributes:
        model_id: The ID of the model to use for ranking.
        base_model_name: The name of the base model to be used
        model_params: The parameters needed for the model.
    """
    model_id: Optional[str] = None
    base_model_name: Optional[str] = None
    model_params: Optional[Dict[str, Any]] = Field(default_factory=dict)


class ModelRankStrategy(BaseModel):
    """
    A data model representing the model ranking strategy.

    Attributes:
        method: The name of the rank strategy. Must be `model`.
        params: The parameters needed for ranking.
    """
    method: Literal["model"] = Field(
        default="model",
        const=True,
        description="Use a model from Models API for ranking.",
    )
    params: ModelRankParams = Field(
        ...,
        description="The parameters needed for ranking.",
    )


class ChunkRankRequest(BaseModel):
    query: str = Field(
        ...,
        description="Natural language query to re-rank chunks against. If a vector store query "
                    "was originally used to retrieve these chunks, please use the same query for "
                    "this ranking",
    )
    relevant_chunks: List[Chunk] = Field(..., description="List of chunks to rank")
    rank_strategy: Union[CrossEncoderRankStrategy, RougeRankStrategy, ModelRankStrategy] = Field(
        ...,
        discriminator="method",
        description="The ranking strategy to use.\n\n"
                    "Rank strategies determine how the ranking is done, They consist of the "
                    "ranking method name and additional params needed to compute the ranking.",
    )
    top_k: Optional[int] = Field(
        gt=0,
        description="Number of chunks to return. Must be greater than 0 if specified. If not "
                    "specified, all chunks will be returned.",
    )
    account_id: Optional[str] = Field(
        default=None,
        description="Account to rank chunks with. If you have access to more than one account, you must specify an account_id",
    )


class ChunkRankResponse(BaseModel):
    relevant_chunks: List[Chunk] = Field(
        ..., description="List of chunks ranked by the requested rank strategy"
    )


class ChunkSynthesisRequest(BaseModel):
    query: str = Field(
        ...,
        description="Natural language query to resolve using the supplied chunks.",
    )
    chunks: List[Chunk] = Field(
        ..., description="List of chunks to use to synthesize the response."
    )


class ChunkSynthesisResponse(BaseModel):
    response: str = Field(..., description="Natural language response addressing the query.")
    metadata: Optional[Dict[str, Dict]] = Field(
        None, description="Optional metadata present on each chunk."
    )
