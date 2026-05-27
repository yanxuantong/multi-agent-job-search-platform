from __future__ import annotations

from dataclasses import dataclass

from jobagent.tools import keyword_score


@dataclass(frozen=True)
class RetrievedChunk:
    chunk_id: str
    text: str
    score: int
    source: str


def chunk_text(text: str, *, source: str, max_words: int = 120, overlap_words: int = 20) -> list[RetrievedChunk]:
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
        )
        for chunk in chunks
    ]
    ranked.sort(key=lambda chunk: (chunk.score, chunk.chunk_id), reverse=True)
    return [chunk for chunk in ranked if chunk.score > 0][:limit]
