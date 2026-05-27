from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from jobagent.tools import keyword_score


def load_story_bank(path: str | Path) -> list[dict[str, Any]]:
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    if not isinstance(data, list):
        raise ValueError("Story bank must be a list of story objects")
    return data


def match_stories(stories: list[dict[str, Any]], skills: list[str], limit: int = 4) -> list[dict[str, Any]]:
    ranked = []
    for story in stories:
        text = " ".join(
            str(story.get(field, ""))
            for field in ("title", "summary", "impact", "skills", "tags")
        )
        ranked.append((keyword_score(text, skills), story))
    ranked.sort(key=lambda item: item[0], reverse=True)
    return [story for score, story in ranked if score > 0][:limit]

