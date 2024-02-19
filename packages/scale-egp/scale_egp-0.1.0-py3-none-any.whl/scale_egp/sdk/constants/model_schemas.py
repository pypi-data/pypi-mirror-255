from typing import Tuple, Type, Dict

from pydantic import BaseModel

from scale_egp.sdk.types.models import (
    AgentResponse, AgentRequest, ChatCompletionRequest,
    ChatCompletionResponse, CompletionRequest, CompletionResponse, EmbeddingRequest,
    EmbeddingResponse, RerankingRequest, RerankingResponse,
)
from scale_egp.sdk.enums import ModelType

MODEL_SCHEMAS: Dict[ModelType, Tuple[Type[BaseModel], Type[BaseModel]]] = {
    ModelType.COMPLETION: (CompletionRequest, CompletionResponse),
    ModelType.CHAT_COMPLETION: (ChatCompletionRequest, ChatCompletionResponse),
    ModelType.AGENT: (AgentRequest, AgentResponse),
    ModelType.RERANKING: (RerankingRequest, RerankingResponse),
    ModelType.EMBEDDING: (EmbeddingRequest, EmbeddingResponse),
}
