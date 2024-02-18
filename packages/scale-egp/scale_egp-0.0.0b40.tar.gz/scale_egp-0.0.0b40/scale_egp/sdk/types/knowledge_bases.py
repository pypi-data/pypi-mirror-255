from __future__ import annotations

from typing import Optional, Dict, Any, List

from pydantic import Field

from scale_egp.sdk.types.embeddings import EmbeddingConfig
from scale_egp.utils.model_utils import Entity, BaseModel


class KnowledgeBase(Entity):
    """
    A data model representing a knowledge base.

    Attributes:
        knowledge_base_id: The unique ID of the knowledge base
        knowledge_base_name: The name of the knowledge base
        embedding_config: The embedding configuration
        metadata: Metadata associated with the knowledge base
        created_at: The timestamp at which the knowledge base was created
        updated_at: The timestamp at which the knowledge base was last updated
    """

    knowledge_base_id: str
    knowledge_base_name: str
    embedding_config: EmbeddingConfig
    metadata: Optional[Dict[str, Any]]
    created_at: str
    updated_at: Optional[str]


class KnowledgeBaseRequest(BaseModel):
    knowledge_base_name: str = Field(..., description="A unique name for the knowledge base")
    embedding_config: EmbeddingConfig = Field(description="The configuration of the embedding")
    account_id: Optional[str] = Field(
        description="Account to create knowledge base in. If you have access to more than one "
                    "account, you must specify an account_id"
    )
    metadata: Optional[Dict[str, Any]] = Field(
        description="Metadata associated with the knowledge base"
    )


class KnowledgeBaseResponse(BaseModel):
    knowledge_base_id: str = Field(..., description="The unique ID of the created knowledge base")


class ListKnowledgeBasesResponse(BaseModel):
    items: List[KnowledgeBase] = Field(
        description="A list of the names and IDs, embedding configurations, metadata, created and "
                    "updated dates of your knowledge bases"
    )
