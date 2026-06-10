from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

from jobagent.models import RetrievalContext, SourceDocument
from jobagent.retrieval import retrieve_context
from jobagent.tools import keyword_score


def load_story_bank(path: str | Path) -> list[dict[str, Any]]:
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    if not isinstance(data, list):
        raise ValueError("Story bank must be a list of story objects")
    return data


def match_stories(stories: list[dict[str, Any]], skills: list[str], limit: int = 4) -> list[dict[str, Any]]:
    context = retrieve_story_context(stories, skills, limit=limit)
    story_by_source_id = {_story_source_id(story): story for story in stories}
    ordered = []
    seen: set[str] = set()
    for chunk in context.selected_chunks:
        if chunk.source_id in seen:
            continue
        seen.add(chunk.source_id)
        story = story_by_source_id.get(chunk.source_id)
        if story:
            ordered.append(story)
    if ordered:
        return ordered[:limit]
    return _legacy_match_stories(stories, skills, limit=limit)


def retrieve_story_context(
    stories: list[dict[str, Any]],
    skills: list[str],
    *,
    query: str = "",
    limit: int = 4,
) -> RetrievalContext:
    documents = story_documents(stories)
    terms = [skill for skill in skills if skill]
    return retrieve_context(
        documents,
        terms,
        query=query or f"story evidence for skills: {', '.join(terms)}",
        limit=limit,
    )


def story_documents(stories: list[dict[str, Any]]) -> list[SourceDocument]:
    return [_story_document(story) for story in stories]


def _story_document(story: dict[str, Any]) -> SourceDocument:
    title = str(story.get("title") or "Untitled story")
    fields = [
        title,
        str(story.get("summary", "")),
        str(story.get("impact", "")),
        " ".join(str(skill) for skill in story.get("skills", [])),
        " ".join(str(tag) for tag in story.get("tags", [])),
    ]
    return SourceDocument(
        source_id=_story_source_id(story),
        source_type="story_bank",
        title=title,
        text=" ".join(field for field in fields if field),
        url=str(story.get("url", "")),
        captured_at=str(story.get("captured_at", "2026-01-01T00:00:00+00:00")),
        published_at=str(story.get("published_at", "")),
        expires_at=str(story.get("expires_at", "")),
        trust_level=str(story.get("trust_level", "user_owned")),
        refresh_policy=str(story.get("refresh_policy", "manual")),
    )


def _story_source_id(story: dict[str, Any]) -> str:
    explicit_id = story.get("id")
    if explicit_id:
        return f"story:{explicit_id}"
    title = str(story.get("title") or "untitled-story").lower()
    slug = re.sub(r"[^a-z0-9]+", "-", title).strip("-") or "untitled-story"
    return f"story:{slug}"


def _legacy_match_stories(stories: list[dict[str, Any]], skills: list[str], limit: int = 4) -> list[dict[str, Any]]:
    ranked = []
    for story in stories:
        text = " ".join(
            str(story.get(field, ""))
            for field in ("title", "summary", "impact", "skills", "tags")
        )
        ranked.append((keyword_score(text, skills), story))
    ranked.sort(key=lambda item: item[0], reverse=True)
    return [story for score, story in ranked if score > 0][:limit]
