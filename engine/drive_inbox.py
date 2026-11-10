#!/usr/bin/env python3
"""Normalize the manually collected Google Drive links without changing the raw inbox.

Usage:
  python engine/drive_inbox.py

Input:
  data/drive-inbox/links-drive.txt

Output:
  data/processed/drive-inbox.normalized.json

This script does not access Google Drive, test permissions, download media,
or bypass authentication/DRM. It only parses and organizes supplied links.
"""
from __future__ import annotations

import json
import re
from pathlib import Path
from urllib.parse import urlsplit
from datetime import datetime, timezone

ROOT = Path(__file__).resolve().parents[1]
INPUT = ROOT / "data" / "drive-inbox" / "links-drive.txt"
OUTPUT = ROOT / "data" / "processed" / "drive-inbox.normalized.json"

URL_RE = re.compile(r"https?://[^\s<>\"']+", re.IGNORECASE)
DRIVE_ID_RE = re.compile(r"/file/d/([^/?#]+)", re.IGNORECASE)
SEARCH_DIRECTIVE_RE = re.compile(r"^(?:site:|inurl:|intitle:)", re.IGNORECASE)
TRAILING_PUNCTUATION = ".,;)"


def clean_url(value: str) -> str:
    return value.strip().rstrip(TRAILING_PUNCTUATION)


def title_before(lines: list[str], index: int) -> str | None:
    """Use the nearest preceding non-empty plain-text line as a possible title."""
    for previous in range(index - 1, -1, -1):
        candidate = lines[previous].strip()
        if not candidate:
            continue
        if URL_RE.fullmatch(candidate):
            return None
        if candidate.startswith("#") or SEARCH_DIRECTIVE_RE.match(candidate):
            return None
        if len(candidate) > 140:
            return None
        return candidate
    return None


def main() -> None:
    if not INPUT.exists():
        raise SystemExit(f"Arquivo de entrada não encontrado: {INPUT}")

    lines = INPUT.read_text(encoding="utf-8-sig").splitlines()
    records: dict[str, dict] = {}
    total_urls = 0
    invalid_urls = 0
    ignored_lines = 0

    for index, line in enumerate(lines):
        for match in URL_RE.findall(line):
            total_urls += 1
            url = clean_url(match)
            parts = urlsplit(url)
            if parts.scheme not in {"http", "https"} or parts.hostname not in {
                "drive.google.com", "docs.google.com"
            }:
                invalid_urls += 1
                continue

            id_match = DRIVE_ID_RE.search(parts.path)
            file_id = id_match.group(1) if id_match else None
            if not file_id:
                query_id = re.search(r"(?:^|&)id=([^&]+)", parts.query)
                file_id = query_id.group(1) if query_id else None
            if not file_id:
                invalid_urls += 1
                continue

            key = file_id
            candidate_title = title_before(lines, index)
            if key in records:
                records[key]["duplicate_occurrences"] += 1
                if not records[key]["title"] and candidate_title:
                    records[key]["title"] = candidate_title
                    records[key]["title_source"] = "adjacent_text"
                continue

            records[key] = {
                "id": f"drive:{file_id}",
                "title": candidate_title or "Arquivo do Google Drive",
                "title_source": "adjacent_text" if candidate_title else "placeholder",
                "source_type": "google_drive",
                "source_url": url,
                "drive_file_id": file_id,
                "format": "unknown",
                "category": "unclassified",
                "poster": None,
                "availability": "not_checked",
                "playback_status": "not_tested",
                "permission_status": "unknown",
                "duplicate_occurrences": 1,
                "source_line": index + 1,
            }

    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "schema_version": "1.0",
        "catalog": "MEDEIA",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "input_file": "data/drive-inbox/links-drive.txt",
        "policy": "links_supplied_by_user_only; no_external_access_check",
        "summary": {
            "input_lines": len(lines),
            "urls_found": total_urls,
            "unique_drive_files": len(records),
            "duplicate_occurrences_removed": total_urls - len(records) - invalid_urls,
            "invalid_or_unsupported_urls": invalid_urls,
            "not_checked": len(records),
        },
        "items": list(records.values()),
    }
    OUTPUT.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(payload["summary"], ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
