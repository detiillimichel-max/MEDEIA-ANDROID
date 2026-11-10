#!/usr/bin/env python3
"""Shared Google Drive result normalization; network providers live in adapters."""
from __future__ import annotations
import re
import urllib.parse
from datetime import datetime, timezone
from typing import Any

DRIVE_HOST = "drive.google.com"

def extract_drive_id(url: str) -> str | None:
    try:
        parsed = urllib.parse.urlparse(url)
    except ValueError:
        return None
    if parsed.scheme != "https" or parsed.hostname != DRIVE_HOST:
        return None
    match = re.search(r"/file/d/([A-Za-z0-9_-]+)", parsed.path)
    return match.group(1) if match else None

def normalize_result(result: dict[str, Any], query: str) -> dict[str, Any] | None:
    url = str(result.get("url") or "").strip()
    file_id = extract_drive_id(url)
    if not file_id:
        return None
    return {
        "id": file_id, "title": str(result.get("title") or "").strip() or None,
        "source_url": url, "source_type": "google_drive_search",
        "search_query": query,
        "description": str(result.get("description") or "").strip() or None,
        "category": "A classificar", "format": "unknown", "poster": None,
        "metadata_status": "search_metadata_only", "availability": "not_checked",
        "read_status": "search_result_found", "playback_status": "not_tested",
    }

def build_catalog(query: str, results: list[dict[str, Any]]) -> dict[str, Any]:
    unique: dict[str, dict[str, Any]] = {}
    rejected = 0
    for result in results:
        item = normalize_result(result, query)
        if item is None:
            rejected += 1
            continue
        file_id = item["id"]
        if file_id in unique:
            unique[file_id]["occurrences"] += 1
            if not unique[file_id]["description"] and item["description"]:
                unique[file_id]["description"] = item["description"]
            continue
        item["occurrences"] = 1
        unique[file_id] = item
    items = list(unique.values())
    return {
        "schema_version": "medeia.drive-search.v1",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "search_provider": "external_adapter", "query": query,
        "search_operator": "site:drive.google.com",
        "policy": "Resultados indexados; acesso e reprodução não verificados. Nenhuma mídia foi baixada e nenhum controle de acesso foi contornado.",
        "summary": {
            "results_received": len(results), "unique_drive_files": len(items),
            "duplicate_results": sum(x["occurrences"] - 1 for x in items),
            "rejected_non_drive_or_non_file_urls": rejected,
            "with_title": sum(bool(x["title"]) for x in items),
            "without_title": sum(not x["title"] for x in items),
        }, "items": items,
    }
