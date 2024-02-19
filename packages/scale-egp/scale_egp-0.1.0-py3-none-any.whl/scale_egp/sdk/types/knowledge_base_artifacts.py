from __future__ import annotations

from datetime import datetime
from typing import Optional, List

from pydantic import Field

from scale_egp.sdk.enums import ArtifactSource
from scale_egp.sdk.types import Chunk
from scale_egp.utils.model_utils import BaseModel


class ChunksStatus(BaseModel):
    """
    A data model representing the status of the chunks in an artifact.

    Attributes:
        chunks_completed: Number of chunks uploaded successfully
        chunks_pending: Number of chunks awaiting upload
        chunks_failed: Number of chunks that failed upload
    """

    chunks_completed: int
    chunks_pending: int
    chunks_failed: int


class KnowledgeBaseArtifact(BaseModel):
    """
    A data model representing an artifact in a knowledge base.

    Attributes:
        artifact_id: Unique identifier for the artifact
        artifact_name: Friendly name for the artifact
        artifact_uri: Location (e.g. URI) of the artifact in the data source
        artifact_uri_public: Public Location (e.g. URI) of the artifact in the data source
        status: Status of the artifact
        status_reason: Reason for the artifact's status
        source: Data source of the artifact
        chunks_status: Number of chunks pending, completed, and failed
        updated_at: Timestamp at which the artifact was last updated
        chunks: List of chunks associated with the artifact
    """

    artifact_id: str
    artifact_name: str
    artifact_uri: str
    artifact_uri_public: Optional[str] = None
    status: str
    status_reason: Optional[str]
    source: ArtifactSource
    chunks_status: ChunksStatus
    updated_at: Optional[datetime] = None
    chunks: Optional[List[Chunk]] = None


class ListKnowledgeBaseArtifactsResponse(BaseModel):
    artifacts: List[KnowledgeBaseArtifact] = Field(..., description="List of artifacts.")
