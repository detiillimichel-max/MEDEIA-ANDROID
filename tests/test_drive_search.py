import unittest
from engine.search_google_drive import build_catalog, extract_drive_id

class DriveSearchTests(unittest.TestCase):
    def test_extracts_drive_file_id(self):
        url = "https://drive.google.com/file/d/FILE_ID_123/view?usp=sharing&resourcekey=abc"
        self.assertEqual(extract_drive_id(url), "FILE_ID_123")

    def test_rejects_non_drive_and_non_file_urls(self):
        self.assertIsNone(extract_drive_id("https://example.com/file/d/123/view"))
        self.assertIsNone(extract_drive_id("https://drive.google.com/drive/folders/123"))
        self.assertIsNone(extract_drive_id("http://drive.google.com/file/d/123/view"))

    def test_deduplicates_without_claiming_availability(self):
        results = [
            {"url": "https://drive.google.com/file/d/ID1/view", "title": "Filme A", "description": "Descrição"},
            {"url": "https://drive.google.com/file/d/ID1/view?resourcekey=key", "title": "Filme A"},
            {"url": "https://example.com/not-drive", "title": "Ignorar"},
        ]
        catalog = build_catalog("Filme A", results)
        self.assertEqual(catalog["summary"]["results_received"], 3)
        self.assertEqual(catalog["summary"]["unique_drive_files"], 1)
        self.assertEqual(catalog["summary"]["duplicate_results"], 1)
        self.assertEqual(catalog["summary"]["rejected_non_drive_or_non_file_urls"], 1)
        self.assertEqual(catalog["items"][0]["availability"], "not_checked")
        self.assertEqual(catalog["items"][0]["playback_status"], "not_tested")
        self.assertEqual(catalog["items"][0]["title"], "Filme A")

if __name__ == "__main__":
    unittest.main()
