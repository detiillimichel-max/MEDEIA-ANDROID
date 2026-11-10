#!/usr/bin/env python3
"""Normalize the MEDEIA Drive inbox without changing the original input."""
from __future__ import annotations
import json, re
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "data" / "drive-inbox" / "links-drive.txt"
OUTPUT = ROOT / "data" / "drive-inbox" / "links-drive.normalized.json"

def drive_id(url: str) -> str | None:
    parsed = urlparse(url)
    if parsed.scheme not in {"http", "https"} or parsed.hostname != "drive.google.com":
        return None
    match = re.search(r"/file/d/([^/]+)", parsed.path)
    return match.group(1) if match else None

def main() -> None:
    lines = SOURCE.read_text(encoding="utf-8-sig").splitlines()
    items, seen = [], {}
    pending_title = None
    url_count = rejected = 0
    for raw in lines:
        line = raw.strip()
        if not line:
            continue
        if line.lower().startswith(("site:", "#")):
            pending_title = None
            continue
        if line.lower().startswith(("http://", "https://")):
            url_count += 1
            file_id = drive_id(line)
            if not file_id:
                rejected += 1
                pending_title = None
                continue
            if file_id in seen:
                item = seen[file_id]
                item["occurrences"] += 1
                if not item["title"] and pending_title:
                    item["title"] = pending_title
            else:
                item = {
                    "id": file_id, "title": pending_title, "source_url": line,
                    "source_type": "google_drive", "category": "Filmes",
                    "format": "unknown", "availability": "not_checked",
                    "playback_status": "not_tested", "poster": None,
                    "metadata_status": "pending", "occurrences": 1
                }
                seen[file_id] = item
                items.append(item)
            pending_title = None
        else:
            pending_title = line

    named = sum(bool(item["title"]) for item in items)
    result = {
        "schema_version": "medeia.drive-inbox.v1",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "source_file": "data/drive-inbox/links-drive.txt",
        "policy": "Links recebidos; acesso, metadados e reprodução não foram verificados.",
        "summary": {
            "source_lines": len(lines), "source_urls": url_count,
            "unique_files": len(items),
            "duplicate_occurrences": sum(x["occurrences"] - 1 for x in items),
            "records_with_title": named, "records_without_title": len(items) - named,
            "rejected_entries": rejected
        },
        "items": items
    }
    OUTPUT.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result["summary"], ensure_ascii=False, indent=2))
    print(f"Gerado: {OUTPUT.relative_to(ROOT)}")

if __name__ == "__main__":
    main()
