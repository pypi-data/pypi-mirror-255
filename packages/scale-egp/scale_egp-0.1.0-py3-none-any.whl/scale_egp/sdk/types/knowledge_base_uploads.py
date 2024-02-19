from __future__ import annotations

from typing import Optional, Union, List, Literal, Dict, Any

from pydantic import Field

from scale_egp.sdk.enums import UploadJobStatus, DataSource, DeduplicationStrategy, ChunkingStrategy
from scale_egp.sdk.types.knowledge_base_artifacts import KnowledgeBaseArtifact
from scale_egp.utils.model_utils import Entity, RootModel, BaseModel



class KnowledgeBaseUploadResponse(BaseModel):
    upload_id: str = Field(..., description="ID of the created knowledge base upload job.")


class CancelKnowledgeBaseUploadResponse(BaseModel):
    upload_id: str = Field(
        ..., description="ID of the knowledge base upload job that was cancelled."
    )
    canceled: bool = Field(..., description="Whether cancellation was successful.")


class ArtifactsStatus(BaseModel):
    """
    A data model representing the status of the artifacts in a knowledge base.

    Attributes:
        artifacts_completed: Number of artifacts uploaded successfully.
        artifacts_pending: Number of artifacts awaiting upload.
        artifacts_uploading: Number of artifacts with upload in progress.
        artifacts_failed: Number of artifacts that failed upload.
    """

    artifacts_completed: int
    artifacts_pending: int
    artifacts_uploading: int
    artifacts_failed: int


class S3DataSourceConfig(BaseModel):
    """
    A data model representing the configuration of a S3 data source.

    Attributes:
        source: The data source type. Must be 's3'.
        s3_bucket: The name of the S3 bucket where the data is stored
        s3_prefix: The prefix of the S3 bucket where the data is stored
        aws_region: The AWS region where the S3 bucket is located
        aws_account_id: The AWS account ID that owns the S3 bucket
    """

    source: Literal[DataSource.S3] = DataSource.S3.value
    s3_bucket: str
    aws_region: str
    aws_account_id: str
    s3_prefix: Optional[str] = None


class SharePointDataSourceConfig(BaseModel):
    """
    A data model representing the configuration of a SharePoint data source.

    Attributes:
        source: The data source type. Must be 'sharepoint'.
        client_id: The client ID associated with this SharePoint site
        tenant_id: The tenant ID that the SharePoint site is within
        site_id: The site ID for this SharePoint site
        folder_path: The nested folder path to read files from the root of the site
        recursive: Whether to recurse through the folder contents
    """

    source: Literal[DataSource.SHAREPOINT] = DataSource.SHAREPOINT.value
    client_id: str
    tenant_id: str
    site_id: str
    folder_path: Optional[str] = ""
    recursive: Optional[bool] = True


class GoogleDriveDataSourceConfig(BaseModel):
    """
    A data model representing the configuration of a Google Drive data source.

    Attributes:
        source: The data source type. Must be 'google_drive'.
        drive_id: The ID of the Google Drive to retrieve contents from
    """

    source: Literal[DataSource.GOOGLE_DRIVE] = DataSource.GOOGLE_DRIVE.value
    drive_id: str

class LocalChunksSourceConfig(BaseModel):
    """
    A data model representing the configuration of a local chunks data source.

    Attributes:
        source: The data source type. Must be 'local_chunks'.
        artifact_name: The file name assigned to the artifact, containing a file extension.
            Adding an extension is mandatory, to allow detecting file types for text extraction.
        artifact_uri: A unique identifier for an artifact within the knowledge base, such as full
            path in a directory or file system.
        deduplication_strategy: Action to take if an artifact with the same name already exists
            in the knowledge base. Can be either Overwrite (default) or Fail.
    """

    source: Literal[DataSource.LOCAL_CHUNKS] = DataSource.LOCAL_CHUNKS.value
    artifact_name: str
    artifact_uri: str
    deduplication_strategy: Optional[DeduplicationStrategy] = DeduplicationStrategy.OVERWRITE

    
class GoogleDriveDataSourceAuthConfig(BaseModel):
    """
    A data model representing the configuration of a Google Drive service account.

    Attributes:
        source: The data source type. Must be 'GoogleDrive'.
        client_email: The service account's client email
        private_key: The service account's private_key
        token_uri: The service account's token_uri
        client_id: The service account's client_id
    """
    source: Literal[DataSource.GOOGLE_DRIVE] = DataSource.GOOGLE_DRIVE.value
    client_email: Optional[str]
    private_key: Optional[str]
    token_uri: Optional[str]
    client_id: Optional[str]

class SharePointDataSourceAuthConfig(BaseModel):
    """
    A data model representing the configuration of a SharePoint data source.

    Attributes:
        source: The data source type. Must be 'sharepoint'.
        client_secret: The secret for the app registration associated with this SharePoint site
    """

    source: Literal[DataSource.SHAREPOINT] = DataSource.SHAREPOINT.value
    client_secret: str

class S3DataSourceAuthConfig(BaseModel):
    """
    A data model representing the configuration of a S3 data source.

    Attributes:
        source: The data source type. Must be 'S3'.
        s3_role: Name of the role that a client will be initialized via AssumeRole of AWS sts
        user_id: External ID of the user to be appended by the upload
    """
    source: Literal["S3"]
    s3_role: str
    user_id: Optional[str]

    class Config(BaseModel.Config):
        title = "Azure DataSource Auth Config"

class CharacterChunkingStrategyConfig(BaseModel):
    """
    A data model representing the configuration of a character chunking strategy.

    Attributes:
        strategy: The chunking strategy type. Must be 'character'.
        separator: Character designating breaks in input data. Text data will first be split
            into sections by this separator, then each section will be split into chunks
            of size `chunk_size`.
        chunk_size: Maximum number of characters in each chunk. If not specified, a chunk size
            of 1000 will be used.
        chunk_overlap: Number of characters to overlap between chunks. If not specified, an overlap
            of 200 will be used. For example if the chunk size is 3 and the overlap size
            is 1, and the text to chunk is 'abcde', the chunks will be 'abc', 'cde'.
    """

    strategy: Literal[ChunkingStrategy.CHARACTER] = ChunkingStrategy.CHARACTER.value
    separator: Optional[str] = "\n\n"
    chunk_size: Optional[int] = 1000
    chunk_overlap: Optional[int] = 200


class ChunkToUpload(BaseModel):
    """
    A data model representing a local chunk.

    Attributes:
        text: The text associated with the chunk
        chunk_position: The position of the chunk in the artifact
        metadata: Any additional key value pairs of information stored with the chunk
    """

    text: str
    chunk_position: int
    metadata: Dict[str, Any] = Field(default_factory=dict)


class DataSourceConfig(RootModel):
    """
    A type alias for a Union of all data source types.

    Attributes:
        __root__: Instead of directly using this class, please use the appropriate data source type
            for your use case.
    """
    __root__: Union[
            S3DataSourceConfig,
            SharePointDataSourceConfig,
            GoogleDriveDataSourceConfig,
            LocalChunksSourceConfig,
        ] = Field(
        ...,
        discriminator="source",
    )


class KnowledgeBaseUpload(Entity):
    """
    A data model representing a knowledge base upload.

    Attributes:
        upload_id: Unique ID of the upload job
        data_source_config: Configuration for downloading data from source
        chunking_strategy_config: Configuration for chunking the text content of each artifact
        created_at: The timestamp at which the upload job started
        updated_at: The timestamp at which the upload job was last updated
        status: Sync status
        status_reason: Reason for the upload job's status
        artifacts_status: Number of artifacts pending, completed, and failed
        artifacts: List of info for each artifacts
    """

    upload_id: str
    data_source_config: DataSourceConfig
    chunking_strategy_config: Optional[Union[CharacterChunkingStrategyConfig]]
    created_at: str
    updated_at: str
    status: UploadJobStatus
    status_reason: Optional[str] = None
    artifacts_status: Optional[ArtifactsStatus]
    artifacts: Optional[List[KnowledgeBaseArtifact]]


class KnowledgeBaseRemoteUploadRequest(BaseModel):
    upload_type: Literal["remote"] = "remote"
    data_source_config: DataSourceConfig
    data_source_auth_config: Optional[DataSourceAuthConfig] = Field(
        None,
        description="Configuration for the data source which describes how to "
                    "authenticate to the data source.",
    )
    chunking_strategy_config: CharacterChunkingStrategyConfig = Field(
        None,
        description="Configuration for the chunking strategy which describes how to chunk the "
                    "data.",
    )

class DataSourceAuthConfig(RootModel):
    __root__: Union[
        GoogleDriveDataSourceAuthConfig,
        SharePointDataSourceAuthConfig,
        S3DataSourceAuthConfig,
    ] = Field(..., discriminator="source")

class ListKnowledgeBaseUploadsResponse(BaseModel):
    uploads: List[KnowledgeBaseUpload] = Field(..., description="List of knowledge base uploads.")


class KnowledgeBaseLocalChunkUploadRequest(BaseModel):
    upload_type: Literal["local_chunks"] = "local_chunks"
    data_source_config: LocalChunksSourceConfig = Field(
        ...,
        description="Configuration for the data source which describes where to find the data.",
    )
    chunks: List[ChunkToUpload] = Field(..., description="List of chunks.")


class KnowledgeBaseUploadRequest(RootModel):
    __root__: Union[
        KnowledgeBaseRemoteUploadRequest,
        KnowledgeBaseLocalChunkUploadRequest,
    ] = Field(
        ...,
        discriminator="upload_type",
    )
