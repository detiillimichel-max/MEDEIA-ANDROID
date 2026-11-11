import tempfile
import unittest
from pathlib import Path
from engine.drive_inbox_reader import parse_drive_url, read_inbox
from engine.search_searxng import search_searxng

class DriveInboxReaderTests(unittest.TestCase):
    def test_preserves_resourcekey_and_url(self):
        url = "https://drive.google.com/file/d/ABC_123/view?usp=drivesdk&resourcekey=key-123"
        item = parse_drive_url(url)
        self.assertEqual(item["id"], "ABC_123")
        self.assertEqual(item["resourcekey"], "key-123")
        self.assertEqual(item["source_url"], url)

    def test_rejects_non_drive_or_non_file_urls(self):
        self.assertIsNone(parse_drive_url("https://example.com/file/d/ABC/view"))
        self.assertIsNone(parse_drive_url("https://drive.google.com/drive/folders/ABC"))
        self.assertIsNone(parse_drive_url("http://drive.google.com/file/d/ABC/view"))

    def test_reads_labels_and_deduplicates_offline(self):
        content = """site:drive.google.com

Filme A
https://drive.google.com/file/d/ID1/view?resourcekey=first

https://drive.google.com/file/d/ID1/view

Filme B
https://drive.google.com/file/d/ID2/view
"""
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "links-drive.txt"
            path.write_text(content, encoding="utf-8")
            result = read_inbox(path)
        self.assertEqual(result["summary"]["url_occurrences"], 3)
        self.assertEqual(result["summary"]["unique_drive_files"], 2)
        self.assertEqual(result["summary"]["duplicate_occurrences"], 1)
        self.assertEqual(result["items"][0]["title"], "Filme A")
        self.assertTrue(result["items"][0]["resourcekey_present"])
        self.assertEqual(result["items"][0]["availability"], "not_checked")
        self.assertEqual(result["items"][0]["playback_status"], "not_tested")

    def test_searxng_requires_https_and_url(self):
        with self.assertRaises(ValueError):
            search_searxng("Filme", "http://example.org")
        with self.assertRaises(ValueError):
            search_searxng("Filme", "")

if __name__ == "__main__":
    unittest.main()
