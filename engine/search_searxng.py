#!/usr/bin/env python3
"""Search Drive-indexed pages through a configurable SearXNG instance."""
from __future__ import annotations
import json
import urllib.error
import urllib.parse
import urllib.request
from typing import Any

from engine.search_google_drive import normalize_result

def search_searxng(query: str, base_url: str, limit: int = 10) -> list[dict[str, Any]]:
    if not base_url.strip():
        raise ValueError("SEARXNG_BASE_URL não foi configurada.")
    parsed = urllib.parse.urlparse(base_url.strip())
    if parsed.scheme != "https" or not parsed.netloc:
        raise ValueError("SEARXNG_BASE_URL precisa ser uma URL HTTPS válida.")
    full_query = f"site:drive.google.com {query}".strip()
    params = urllib.parse.urlencode({"q": full_query, "format": "json", "pageno": "1"})
    request = urllib.request.Request(base_url.rstrip("/") + "/search?" + params,
        headers={"Accept": "application/json", "User-Agent": "MEDEIA-Android-DriveCatalog/0.1"})
    try:
        with urllib.request.urlopen(request, timeout=25) as response:
            body = response.read(2_000_000)
    except urllib.error.HTTPError as exc:
        detail = exc.read(800).decode("utf-8", errors="replace")
        raise RuntimeError(f"SearXNG respondeu HTTP {exc.code}: {detail}") from exc
    except (urllib.error.URLError, TimeoutError) as exc:
        raise RuntimeError(f"Falha ao consultar SearXNG: {exc}") from exc
    try:
        payload = json.loads(body.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise RuntimeError("SearXNG não retornou JSON válido; a instância pode não habilitar format=json.") from exc
    results = payload.get("results")
    if not isinstance(results, list):
        raise RuntimeError("Resposta SearXNG sem a lista 'results'.")
    normalized = []
    for result in results:
        if not isinstance(result, dict):
            continue
        item = normalize_result({"url": result.get("url"), "title": result.get("title"),
                                 "description": result.get("content")}, query)
        if item:
            item["source_type"] = "google_drive_searxng"
            normalized.append(item)
        if len(normalized) >= max(1, min(limit, 20)):
            break
    return normalized
