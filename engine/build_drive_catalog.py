#!/usr/bin/env python3
"""Build a catalog from the existing inbox and optional SearXNG search."""
from __future__ import annotations
import argparse
import json
import os
from datetime import datetime, timezone
from pathlib import Path

from engine.drive_inbox_reader import read_inbox
from engine.search_searxng import search_searxng

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUTPUT = ROOT / "data" / "drive-search" / "catalog.json"

def merge_items(*groups):
    merged = {}
    for group in groups:
        for item in group:
            file_id = item["id"]
            if file_id not in merged:
                merged[file_id] = item.copy()
                continue
            current = merged[file_id]
            current["occurrences"] = current.get("occurrences", 1) + item.get("occurrences", 1)
            for key in ("title", "description"):
                if not current.get(key) and item.get(key):
                    current[key] = item[key]
            if current.get("source_type") != "google_drive_inbox" and item.get("source_type") == "google_drive_inbox":
                for key in ("source_url", "resourcekey", "resourcekey_present", "source_type"):
                    if key in item:
                        current[key] = item[key]
    return list(merged.values())

def main():
    parser = argparse.ArgumentParser(description="Gera catálogo MEDEIA a partir do inbox e SearXNG.")
    parser.add_argument("--query", default="", help="Busca adicional por título usando site:drive.google.com.")
    parser.add_argument("--limit", type=int, default=10)
    parser.add_argument("--inbox", type=Path, default=ROOT / "data" / "drive-inbox" / "links-drive.txt")
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    inbox = read_inbox(args.inbox)
    discovered = []
    provider = "inbox_only"
    if args.query.strip():
        base_url = os.environ.get("SEARXNG_BASE_URL", "").strip()
        if not base_url:
            parser.error("Defina SEARXNG_BASE_URL para executar a busca SearXNG.")
        discovered = search_searxng(args.query.strip(), base_url, args.limit)
        provider = "searxng_plus_inbox"
    items = merge_items(inbox["items"], discovered)
    catalog = {
        "schema_version": "medeia.drive-catalog.v1",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "search_provider": provider, "search_operator": "site:drive.google.com",
        "source_file": inbox["source_file"],
        "policy": "Links do inbox são analisados localmente. Nenhum link foi aberto, mídia baixada ou permissão verificada. A abertura final usa a conta e as permissões do usuário no Android/Google Drive.",
        "summary": {**inbox["summary"], "new_search_results": len(discovered),
            "unique_catalog_items": len(items), "access_status": "not_checked",
            "playback_status": "not_tested"},
        "items": items}
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(catalog, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(catalog["summary"], ensure_ascii=False, indent=2))
    print(f"Catálogo gerado: {args.output}")

if __name__ == "__main__":
    main()
