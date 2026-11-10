#!/usr/bin/env python3
"""Normalize existing Google Drive links from the MEDEIA inbox without opening media."""
from __future__ import annotations
import re
import urllib.parse
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_INBOX = ROOT / "data" / "drive-inbox" / "links-drive.txt"
DRIVE_HOST = "drive.google.com"

def parse_drive_url(url: str) -> dict[str, Any] | None:
    try:
        parsed = urllib.parse.urlparse(url.strip())
    except ValueError:
        return None
    if parsed.scheme != "https" or parsed.hostname != DRIVE_HOST:
        return None
    match = re.fullmatch(r"/file/d/([A-Za-z0-9_-]+)/?(?:view)?/?", parsed.path)
    if not match:
        return None
    values = urllib.parse.parse_qs(parsed.query, keep_blank_values=True).get("resourcekey", [])
    return {"id": match.group(1), "source_url": url.strip(),
            "resourcekey_present": bool(values and values[0]),
            "resourcekey": values[0] if values and values[0] else None}

def read_inbox(path: Path = DEFAULT_INBOX) -> dict[str, Any]:
    if not path.exists():
        raise FileNotFoundError(f"Arquivo de entrada não encontrado: {path}")
    items: dict[str, dict[str, Any]] = {}
    pending_title = None
    url_occurrences = rejected = 0
    for raw in path.read_text(encoding="utf-8-sig").splitlines():
        line = raw.strip()
        if not line or line.lower().startswith("site:"):
            continue
        if line.startswith(("https://", "http://")):
            url_occurrences += 1
            parsed = parse_drive_url(line)
            if parsed is None:
                rejected += 1
                pending_title = None
                continue
            file_id = parsed["id"]
            if file_id in items:
                item = items[file_id]
                item["occurrences"] += 1
                if not item["title"] and pending_title:
                    item["title"] = pending_title
                if not item["resourcekey_present"] and parsed["resourcekey_present"]:
                    item.update(parsed)
                pending_title = None
                continue
            items[file_id] = {**parsed, "title": pending_title,
                "source_type": "google_drive_inbox",
                "metadata_status": "inbox_link_parsed",
                "availability": "not_checked",
                "read_status": "url_parsed_not_fetched",
                "playback_status": "not_tested", "occurrences": 1}
            pending_title = None
        else:
            pending_title = line
    records = list(items.values())
    try:
        source_file = str(path.relative_to(ROOT))
    except ValueError:
        source_file = path.name
    return {"source_file": source_file, "summary": {
        "url_occurrences": url_occurrences, "unique_drive_files": len(records),
        "duplicate_occurrences": sum(x["occurrences"] - 1 for x in records),
        "rejected_urls": rejected, "with_title": sum(bool(x["title"]) for x in records),
        "without_title": sum(not x["title"] for x in records),
        "with_resourcekey": sum(x["resourcekey_present"] for x in records)},
        "items": records}
