from typing import List, Optional, Union

from scale_egp.sdk.types.chunks import (
    ChunkRankRequest, ChunkRankResponse,
    ChunkSynthesisRequest, ChunkSynthesisResponse, Chunk, CrossEncoderRankStrategy,
    RougeRankStrategy, ModelRankStrategy,
)
from scale_egp.utils.api_utils import APIEngine


class ChunkCollection(APIEngine):

    _sub_path = "v2/chunks"

    def rank(
        self,
        query: str,
        relevant_chunks: List[Chunk],
        rank_strategy: Union[CrossEncoderRankStrategy, RougeRankStrategy, ModelRankStrategy],
        top_k: Optional[int] = None,
        account_id: Optional[str] = None,
    ) -> List[Chunk]:
        """
        Re-rank a list of chunks against a query.

        Args:
            query: Natural language query to re-rank chunks against. If a vector store query
                was originally used to retrieve these chunks, please use the same query for
                this ranking.
            relevant_chunks: List of chunks to rank.
            rank_strategy: The ranking strategy to use.
                Rank strategies determine how the ranking is done, They consist of the
                ranking method name and additional params needed to compute the ranking.
                So far, only the `cross_encoder` rank strategy is supported. We plan to
                support more rank strategies soon.
            top_k: Number of chunks to return. Must be greater than 0 if specified. If not
                specified, all chunks will be returned.

        Returns:
            An ordered list of the re-ranked chunks.
        """
        if isinstance(rank_strategy, ModelRankStrategy):
            if "query" not in rank_strategy.params.model_params:
                rank_strategy.params.model_params["query"] = query
            if "relevant_chunks" not in rank_strategy.params:
                rank_strategy.params.model_params["chunks"] = relevant_chunks
        response = self._post(
            sub_path=f"{self._sub_path}/rank",
            request=ChunkRankRequest(
                query=query,
                relevant_chunks=relevant_chunks,
                rank_strategy=rank_strategy,
                top_k=top_k,
                account_id=account_id,
            ),
        )
        response_model = ChunkRankResponse.from_dict(response.json())
        return [Chunk.from_dict(chunk) for chunk in response_model.relevant_chunks]

    def synthesize(
        self,
        query: str,
        chunks: List[Chunk],
    ) -> str:
        """
        Synthesize a natural language response from a list of chunks.

        Args:
            query: Natural language query to synthesize response from.
            chunks: List of chunks to synthesize response from.

        Returns:
            A natural language response synthesized from the list of chunks.
        """
        response = self._post(
            sub_path=f"{self._sub_path}/synthesis",
            request=ChunkSynthesisRequest(
                query=query,
                chunks=chunks,
            ),
        )
        response_model = ChunkSynthesisResponse.from_dict(response.json())
        return response_model.response
