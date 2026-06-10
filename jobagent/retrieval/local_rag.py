from __future__ import annotations

from datetime import datetime, timezone

from jobagent.models import RetrievalCitation, RetrievalContext, RetrievedChunk, SourceDocument
from jobagent.tools import keyword_score


def chunk_text(
    text: str,
    *,
    source: str,
    max_words: int = 120,
    overlap_words: int = 20,
    source_id: str = "",
    title: str = "",
    source_type: str = "",
    url: str = "",
    captured_at: str = "",
    published_at: str = "",
    expires_at: str = "",
    trust_level: str = "user_owned",
    refresh_policy: str = "manual",
    freshness_status: str = "unknown",
) -> list[RetrievedChunk]:
    """Small deterministic chunker for learning RAG before adding embeddings."""

    words = text.split()
    if not words:
        return []
    chunks = []
    step = max(1, max_words - overlap_words)
    for index, start in enumerate(range(0, len(words), step)):
        piece = words[start : start + max_words]
        if not piece:
            continue
        chunks.append(
            RetrievedChunk(
                chunk_id=f"{source}:{index}",
                text=" ".join(piece),
                score=0,
                source=source,
                source_id=source_id or source,
                title=title or source,
                source_type=source_type,
                url=url,
                captured_at=captured_at,
                published_at=published_at,
                expires_at=expires_at,
                trust_level=trust_level,
                refresh_policy=refresh_policy,
                freshness_status=freshness_status,
            )
        )
        if start + max_words >= len(words):
            break
    return chunks


def rank_chunks(chunks: list[RetrievedChunk], query_terms: list[str], *, limit: int = 5) -> list[RetrievedChunk]:
    ranked = [
        RetrievedChunk(
            chunk_id=chunk.chunk_id,
            text=chunk.text,
            score=keyword_score(chunk.text, query_terms),
            source=chunk.source,
            source_id=chunk.source_id,
            title=chunk.title,
            source_type=chunk.source_type,
            url=chunk.url,
            captured_at=chunk.captured_at,
            published_at=chunk.published_at,
            expires_at=chunk.expires_at,
            trust_level=chunk.trust_level,
            refresh_policy=chunk.refresh_policy,
            freshness_status=chunk.freshness_status,
        )
        for chunk in chunks
    ]
    ranked.sort(key=lambda chunk: (chunk.score, chunk.chunk_id), reverse=True)
    return [chunk for chunk in ranked if chunk.score > 0][:limit]


def chunk_documents(
    documents: list[SourceDocument],
    *,
    max_words: int = 120,
    overlap_words: int = 20,
    now: datetime | None = None,
) -> list[RetrievedChunk]:
    chunks: list[RetrievedChunk] = []
    for document in documents:
        freshness_status = freshness_for(document, now=now)
        chunks.extend(
            chunk_text(
                document.text,
                source=document.source_id,
                max_words=max_words,
                overlap_words=overlap_words,
                source_id=document.source_id,
                title=document.title,
                source_type=document.source_type,
                url=document.url,
                captured_at=document.captured_at,
                published_at=document.published_at,
                expires_at=document.expires_at,
                trust_level=document.trust_level,
                refresh_policy=document.refresh_policy,
                freshness_status=freshness_status,
            )
        )
    return chunks


def retrieve_context(
    documents: list[SourceDocument],
    query_terms: list[str],
    *,
    query: str = "",
    limit: int = 5,
    retriever: str = "local_keyword",
    semantic_scores: dict[str, float] | None = None,
    now: datetime | None = None,
) -> RetrievalContext:
    chunks = chunk_documents(documents, now=now)
    if semantic_scores:
        selected = hybrid_rank_chunks(chunks, query_terms, semantic_scores=semantic_scores, limit=limit)
        retriever = "hybrid_keyword_semantic"
    else:
        selected = rank_chunks(chunks, query_terms, limit=limit)
    citations = _citations_for(selected)
    freshness_warnings = [
        f"{chunk.title or chunk.source} is {chunk.freshness_status}; refresh policy: {chunk.refresh_policy}"
        for chunk in selected
        if chunk.freshness_status == "stale"
    ]
    return RetrievalContext(
        query=query or " ".join(query_terms),
        query_terms=query_terms,
        selected_chunks=selected,
        citations=citations,
        freshness_warnings=freshness_warnings,
        candidate_count=len(chunks),
        returned_count=len(selected),
        retriever=retriever,
        assembly_reason="Top ranked chunks are assembled before generation so downstream agents can cite concrete evidence.",
    )


def hybrid_rank_chunks(
    chunks: list[RetrievedChunk],
    query_terms: list[str],
    *,
    semantic_scores: dict[str, float],
    limit: int = 5,
) -> list[RetrievedChunk]:
    ranked = []
    for chunk in chunks:
        keyword_component = keyword_score(chunk.text, query_terms) * 10
        semantic_component = int(max(0.0, semantic_scores.get(chunk.chunk_id, 0.0)) * 100)
        ranked.append(
            RetrievedChunk(
                chunk_id=chunk.chunk_id,
                text=chunk.text,
                score=keyword_component + semantic_component,
                source=chunk.source,
                source_id=chunk.source_id,
                title=chunk.title,
                source_type=chunk.source_type,
                url=chunk.url,
                captured_at=chunk.captured_at,
                published_at=chunk.published_at,
                expires_at=chunk.expires_at,
                trust_level=chunk.trust_level,
                refresh_policy=chunk.refresh_policy,
                freshness_status=chunk.freshness_status,
            )
        )
    ranked.sort(key=lambda chunk: (chunk.score, chunk.chunk_id), reverse=True)
    return [chunk for chunk in ranked if chunk.score > 0][:limit]


def freshness_for(document: SourceDocument, *, now: datetime | None = None) -> str:
    if document.expires_at:
        parsed = _parse_datetime(document.expires_at)
        if parsed and parsed < (now or datetime.now(timezone.utc)):
            return "stale"
    if document.captured_at or document.published_at or document.refresh_policy == "manual":
        return "fresh"
    return "unknown"


def _citations_for(chunks: list[RetrievedChunk]) -> list[RetrievalCitation]:
    seen: set[str] = set()
    citations: list[RetrievalCitation] = []
    for chunk in chunks:
        source_id = chunk.source_id or chunk.source
        if source_id in seen:
            continue
        seen.add(source_id)
        citations.append(
            RetrievalCitation(
                source_id=source_id,
                title=chunk.title or chunk.source,
                source_type=chunk.source_type,
                url=chunk.url,
                captured_at=chunk.captured_at,
                published_at=chunk.published_at,
                expires_at=chunk.expires_at,
                freshness_status=chunk.freshness_status,
            )
        )
    return citations


def _parse_datetime(value: str) -> datetime | None:
    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return None
