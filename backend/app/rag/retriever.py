"""
Two-stage retrieval: Hybrid Ensemble (ChromaDB + BM25) + cross-encoder reranking.
"""
import logging
from typing import List, Dict, Any, Optional
from app.config import get_settings
from app.rag.embeddings import embed_query
from app.rag.tracing import trace_function
from app.rag.vectorstore import query_chunks

from langchain.retrievers import EnsembleRetriever
from langchain_core.retrievers import BaseRetriever
from langchain_core.documents import Document as LangchainDocument
from langchain_core.callbacks import CallbackManagerForRetrieverRun
from pydantic import Field

logger = logging.getLogger(__name__)
settings = get_settings()

# ── Singleton reranker ───────────────────────────────
_reranker = None


def get_reranker():
    """Load cross-encoder reranker model (singleton)."""
    global _reranker

    if _reranker is None:
        try:
            from sentence_transformers import CrossEncoder
            logger.info(f"Loading reranker: {settings.RERANKER_MODEL}")
            _reranker = CrossEncoder(settings.RERANKER_MODEL, max_length=512)
            logger.info("Reranker loaded successfully")
        except Exception as e:
            logger.warning(f"Failed to load reranker: {e}. Falling back to embedding-only retrieval.")
            _reranker = "disabled"

    return _reranker if _reranker != "disabled" else None


class CustomVectorRetriever(BaseRetriever):
    user_id: str = Field(description="User ID")
    document_id: Optional[str] = Field(default=None, description="Document ID")
    top_k: int = Field(default=10, description="Top K results")

    def _get_relevant_documents(
        self, query: str, *, run_manager: CallbackManagerForRetrieverRun
    ) -> List[LangchainDocument]:
        query_vector = embed_query(query)
        candidates = query_chunks(
            query_embedding=query_vector,
            user_id=self.user_id,
            document_id=self.document_id,
            top_k=self.top_k,
        )
        return [LangchainDocument(page_content=c["text"], metadata=c) for c in candidates]


class CustomBM25Retriever(BaseRetriever):
    user_id: str = Field(description="User ID")
    document_id: Optional[str] = Field(default=None, description="Document ID")
    top_k: int = Field(default=10, description="Top K results")

    def _get_relevant_documents(
        self, query: str, *, run_manager: CallbackManagerForRetrieverRun
    ) -> List[LangchainDocument]:
        from app.rag.bm25 import query_bm25
        candidates = query_bm25(
            query=query,
            user_id=self.user_id,
            document_id=self.document_id,
            top_k=self.top_k,
        )
        return [LangchainDocument(page_content=c["text"], metadata=c) for c in candidates]


@trace_function(
    "retrieve",
    metadata_factory=lambda query, user_id, document_id=None: {
        "user_id": user_id,
        "document_id": document_id,
        "embedding_model": settings.EMBEDDING_MODEL,
        "reranker_model": settings.RERANKER_MODEL,
        "top_k_retrieval": settings.TOP_K_RETRIEVAL,
        "top_k_rerank": settings.TOP_K_RERANK,
    },
)
def retrieve(
    query: str,
    user_id: str,
    document_id: Optional[str] = None,
) -> List[Dict[str, Any]]:
    """
    Two-stage retrieval pipeline:
    1. Hybrid Search (Vector + BM25 via EnsembleRetriever with RRF)
    2. Cross-encoder reranking (top-K refined)

    Returns chunks with confidence scores.
    """
    # ── Stage 1: Hybrid Search ───────────────────────
    vector_retriever = CustomVectorRetriever(
        user_id=user_id,
        document_id=document_id,
        top_k=settings.TOP_K_RETRIEVAL,
    )
    
    bm25_retriever = CustomBM25Retriever(
        user_id=user_id,
        document_id=document_id,
        top_k=settings.TOP_K_RETRIEVAL,
    )
    
    ensemble_retriever = EnsembleRetriever(
        retrievers=[vector_retriever, bm25_retriever],
        weights=[0.6, 0.4]
    )
    
    docs = ensemble_retriever.invoke(query)
    
    candidates = []
    for i, doc in enumerate(docs):
        chunk = doc.metadata.copy()
        # EnsembleRetriever doesn't expose the raw RRF score directly on the document,
        # but we preserve a mock score based on rank for fallback if reranker fails
        chunk["score"] = 1.0 / (i + 1)
        candidates.append(chunk)

    if not candidates:
        return []

    # ── Stage 2: Cross-encoder reranking ─────────────
    reranker = get_reranker()

    if reranker is not None and len(candidates) > 1:
        try:
            # Build query-document pairs for reranking
            pairs = [(query, chunk["text"]) for chunk in candidates]
            rerank_scores = reranker.predict(pairs)

            # Assign rerank scores
            for i, chunk in enumerate(candidates):
                chunk["rerank_score"] = float(rerank_scores[i])

            # Sort by rerank score (descending)
            candidates.sort(key=lambda x: x.get("rerank_score", 0), reverse=True)

        except Exception as e:
            logger.warning(f"Reranking failed, using hybrid scores: {e}")

    # ── Take top-K after reranking ───────────────────
    top_chunks = candidates[:settings.TOP_K_RERANK]

    # ── Calculate confidence percentages ─────────────
    if top_chunks:
        max_score = max(
            chunk.get("rerank_score", chunk.get("score", 0))
            for chunk in top_chunks
        )
        max_score = max(max_score, 0.001)  # Avoid division by zero

        for chunk in top_chunks:
            raw = chunk.get("rerank_score", chunk.get("score", 0))
            chunk["confidence"] = round((raw / max_score) * 100, 1)
            # Clean up internal score
            if "rerank_score" in chunk:
                chunk["score"] = round(chunk["rerank_score"], 4)
                del chunk["rerank_score"]

    return top_chunks
