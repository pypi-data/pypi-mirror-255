from __future__ import annotations

from typing import Optional, Dict, Any, List

from pydantic import Field

from scale_egp.sdk.types.chunks import Chunk
from scale_egp.utils.model_utils import BaseModel


class KnowledgeBaseChunksRequest(BaseModel):
    chunk_id: Optional[str] = Field(None, description="Optional search by chunk_id")
    metadata_filters: Optional[Dict[str, Any]] = Field(
        None, description="Optional search by metadata fields"
    )


class KnowledgeBaseChunksResponse(BaseModel):
    chunks: List[Chunk] = Field(
        ..., description="List of chunks that match the chunk_id and metadata filters"
    )


class KnowledgeBaseQueryRequest(BaseModel):
    query: str = Field(
        description="The natural language query to be answered by referencing the data ingested "
                    "into the knowledge base"
    )
    top_k: int = Field(
        gt=0,
        description="Number of chunks to return. Must be greater than 0 if specified. If not "
                    "specified, all chunks will be returned.",
    )
    include_embeddings: bool = Field(
        default=True,
        description="Whether or not to include the embeddings for each chunk",
    )
    metadata_filters: Optional[Dict[str, Any]] = Field(
        None, description="Optional filter by metadata fields"
    )


class KnowledgeBaseQueryResponse(BaseModel):
    chunks: List[Chunk] = Field(
        description="An ordered list of the k most similar chunks and their similarity scores "
                    "from most to least similar"
    )
