#!/usr/bin/env python3
"""Search public Google Drive-indexed results and write a MEDEIA JSON catalog."""
from __future__ import annotations
import argparse, json, os, re, sys, urllib.error, urllib.parse, urllib.request
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUTPUT = ROOT / "data" / "drive-search" / "catalog.json"
SEARCH_ENDPOINT = "https://api.firecrawl.dev/v2/search"
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
    title = str(result.get("title") or "").strip() or None
    description = str(result.get("description") or "").strip() or None
    return {
        "id": file_id, "title": title, "source_url": url,
        "source_type": "google_drive", "search_query": query,
        "description": description, "category": "A classificar",
        "format": "unknown", "poster": None,
        "metadata_status": "search_metadata_only",
        "availability": "not_checked", "read_status": "search_result_found",
        "playback_status": "not_tested",
    }

def search_firecrawl(query: str, api_key: str, limit: int = 10) -> list[dict[str, Any]]:
    full_query = f"site:drive.google.com {query}".strip()
    payload = {
        "query": full_query, "limit": max(1, min(limit, 20)),
        "sources": [{"type": "web"}],
        "scrapeOptions": {"formats": [{"type": "markdown"}]},
    }
    request = urllib.request.Request(
        SEARCH_ENDPOINT, data=json.dumps(payload).encode("utf-8"),
        headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json",
                 "Accept": "application/json", "User-Agent": "MEDEIA-Drive-Search/0.1"},
        method="POST")
    try:
        with urllib.request.urlopen(request, timeout=45) as response:
            body = response.read()
    except urllib.error.HTTPError as exc:
        detail = exc.read(1200).decode("utf-8", errors="replace")
        raise RuntimeError(f"Firecrawl respondeu HTTP {exc.code}: {detail}") from exc
    except (urllib.error.URLError, TimeoutError) as exc:
        raise RuntimeError(f"Falha de conexão com Firecrawl: {exc}") from exc
    try:
        data = json.loads(body.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise RuntimeError("Firecrawl retornou uma resposta que não é JSON válido.") from exc
    if data.get("success") is False:
        raise RuntimeError(f"Firecrawl informou falha: {data.get('error') or 'erro não detalhado'}")
    web_results = (data.get("data") or {}).get("web") or []
    if not isinstance(web_results, list):
        raise RuntimeError("Formato inesperado na lista de resultados do Firecrawl.")
    return web_results

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
        "search_provider": "firecrawl_v2", "query": query,
        "search_operator": "site:drive.google.com",
        "policy": "Resultados indexados. Título e descrição vêm do índice; permissão, metadados completos e disponibilidade não foram verificados. Nenhuma mídia foi baixada e nenhum controle de acesso foi contornado.",
        "summary": {
            "results_received": len(results), "unique_drive_files": len(items),
            "duplicate_results": sum(x["occurrences"] - 1 for x in items),
            "rejected_non_drive_or_non_file_urls": rejected,
            "with_title": sum(bool(x["title"]) for x in items),
            "without_title": sum(not x["title"] for x in items),
        }, "items": items,
    }

def main() -> int:
    parser = argparse.ArgumentParser(description="Pesquisa conteúdos indexados no Google Drive.")
    parser.add_argument("--query", required=True, help="Nome do filme, série, desenho ou documentário.")
    parser.add_argument("--limit", type=int, default=10, help="Máximo de resultados (1 a 20).")
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT, help="Arquivo JSON de saída.")
    args = parser.parse_args()
    query = args.query.strip()
    if not query:
        parser.error("--query não pode ficar vazia.")
    api_key = os.environ.get("FIRECRAWL_API_KEY", "").strip()
    if not api_key:
        print("ERRO: configure FIRECRAWL_API_KEY no ambiente ou nos GitHub Secrets.", file=sys.stderr)
        return 2
    results = search_firecrawl(query, api_key, args.limit)
    catalog = build_catalog(query, results)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(catalog, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(catalog["summary"], ensure_ascii=False, indent=2))
    print(f"Catálogo gerado: {args.output}")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
