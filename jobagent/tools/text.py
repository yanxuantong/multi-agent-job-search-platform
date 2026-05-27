from __future__ import annotations

import re


def normalize_lines(text: str) -> list[str]:
    return [line.strip(" -*\t") for line in text.splitlines() if line.strip(" -*\t")]


def extract_bullets(text: str, keywords: tuple[str, ...], limit: int = 6) -> list[str]:
    lines = normalize_lines(text)
    hits = [line for line in lines if any(word.lower() in line.lower() for word in keywords)]
    return hits[:limit]


def keyword_score(text: str, keywords: list[str]) -> int:
    lowered = text.lower()
    return sum(1 for keyword in keywords if re.search(rf"\b{re.escape(keyword.lower())}\b", lowered))

