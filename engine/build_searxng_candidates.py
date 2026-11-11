#!/usr/bin/env python3
"""Experimental, cumulative SearXNG discovery; never overwrites the main catalog."""
from __future__ import annotations
import argparse
import json
import os
from datetime import datetime, timezone
from pathlib import Path
from engine.search_searxng import search_searxng

ROOT = Path(__file__).resolve().parents[1]
MAIN_CATALOG = ROOT / "data" / "drive-search" / "catalog.json"
CANDIDATES_FILE = ROOT / "data" / "drive-search" / "discovered-candidates.json"
MAX_EXPERIMENTAL_RESULTS = 10

def load_items(path: Path) -> list[dict]:
    if not path.exists():
        return []
    payload = json.loads(path.read_text(encoding="utf-8"))
    items = payload.get("items", [])
    if not isinstance(items, list):
        raise ValueError(f"Arquivo sem lista items: {path}")
    return items

def build_candidates(query: str, discovered: list[dict], main_items: list[dict],
                     previous_items: list[dict]) -> dict:
    protected_ids = {str(x.get("id")) for x in main_items if x.get("id")}
    merged = {str(x["id"]): dict(x) for x in previous_items if x.get("id")}
    new_count = duplicate_count = protected_count = 0
    for item in discovered:
        file_id = str(item.get("id") or "")
        if not file_id:
            continue
        if file_id in protected_ids:
            protected_count += 1
            continue
        if file_id in merged:
            duplicate_count += 1
            old = merged[file_id]
            old["occurrences"] = int(old.get("occurrences", 1)) + 1
            if not old.get("title") and item.get("title"):
                old["title"] = item["title"]
            continue
        candidate = dict(item)
        candidate["source_type"] = "google_drive_searxng_candidate"
        candidate["discovery_status"] = "candidate_not_verified"
        candidate["availability"] = "not_checked"
        candidate["playback_status"] = "not_tested"
        candidate["occurrences"] = 1
        merged[file_id] = candidate
        new_count += 1
    items = list(merged.values())
    return {
        "schema_version": "medeia.drive-discovery.v1",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "search_provider": "searxng_experimental",
        "last_query": query,
        "policy": "Candidatos encontrados em resultados publicamente indexados. Não significa acesso público confirmado nem reprodução testada. Nenhuma mídia foi baixada e nenhum controle de acesso foi contornado.",
        "summary": {
            "received_this_run": len(discovered),
            "new_candidates_this_run": new_count,
            "duplicates_this_run": duplicate_count,
            "already_in_main_catalog": protected_count,
            "cumulative_candidates": len(items),
            "access_status": "not_checked",
            "playback_status": "not_tested"
        },
        "items": items
    }

def main() -> None:
    parser = argparse.ArgumentParser(description="Busca experimental SearXNG para MEDEIA.")
    parser.add_argument("--query", required=True)
    parser.add_argument("--limit", type=int, default=10)
    parser.add_argument("--main-catalog", type=Path, default=MAIN_CATALOG)
    parser.add_argument("--candidates", type=Path, default=CANDIDATES_FILE)
    args = parser.parse_args()
    limit = max(1, min(args.limit, MAX_EXPERIMENTAL_RESULTS))
    base_url = os.environ.get("SEARXNG_BASE_URL", "").strip()
    if not base_url:
        parser.error("Configure a variável de repositório SEARXNG_BASE_URL com uma instância HTTPS que aceite format=json.")
    main_items = load_items(args.main_catalog)
    previous_items = load_items(args.candidates)
    discovered = search_searxng(args.query.strip(), base_url, limit)
    result = build_candidates(args.query.strip(), discovered, main_items, previous_items)
    result["summary"]["requested_limit"] = limit
    args.candidates.parent.mkdir(parents=True, exist_ok=True)
    args.candidates.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result["summary"], ensure_ascii=False, indent=2))
    print(f"Candidatos experimentais acumulados em: {args.candidates}")

if __name__ == "__main__":
    main()
