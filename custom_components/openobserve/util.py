"""Pure helpers (no Home Assistant imports) for tests and handlers."""

from __future__ import annotations

from typing import Any

from .const import SECRET_KEYS


def redact_secrets(data: Any) -> Any:
    """Recursively redact known secret keys."""
    if isinstance(data, dict):
        return {
            k: "[REDACTED]" if k.lower() in SECRET_KEYS else redact_secrets(v)
            for k, v in data.items()
        }
    if isinstance(data, list):
        return [redact_secrets(item) for item in data]
    return data


def entity_matches_exclude(entity_id: str | None, patterns: list[str]) -> bool:
    """Return True if entity_id matches any glob-style exclude pattern."""
    if not entity_id or not patterns:
        return False
    for pattern in patterns:
        pattern = pattern.strip()
        if not pattern:
            continue
        if pattern.endswith("*") and entity_id.startswith(pattern[:-1]):
            return True
        if pattern == entity_id:
            return True
    return False
