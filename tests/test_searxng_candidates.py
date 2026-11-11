import tempfile
import unittest
from pathlib import Path
from engine.build_searxng_candidates import build_candidates, load_items

class ExperimentalCandidatesTests(unittest.TestCase):
    def test_preserves_main_catalog_and_filters_existing_ids(self):
        main = [{"id": "BASE1", "title": "Original"}]
        found = [
            {"id": "BASE1", "title": "Already in main"},
            {"id": "NEW1", "title": "New candidate"},
            {"id": "NEW1", "title": "Duplicate"},
        ]
        result = build_candidates("documentários", found, main, [])
        self.assertEqual(result["summary"]["new_candidates_this_run"], 1)
        self.assertEqual(result["summary"]["already_in_main_catalog"], 1)
        self.assertEqual(result["summary"]["duplicates_this_run"], 1)
        self.assertEqual([x["id"] for x in result["items"]], ["NEW1"])
        self.assertEqual(result["items"][0]["availability"], "not_checked")
        self.assertEqual(result["items"][0]["playback_status"], "not_tested")
        self.assertEqual(main, [{"id": "BASE1", "title": "Original"}])

    def test_accumulates_without_losing_previous_candidates(self):
        previous = [{"id": "OLD1", "title": "Old", "occurrences": 1}]
        result = build_candidates("filmes", [{"id": "NEW1", "title": "New"}], [], previous)
        self.assertEqual({x["id"] for x in result["items"]}, {"OLD1", "NEW1"})
        again = build_candidates("séries", [{"id": "OLD1", "title": "Old again"}], [], result["items"])
        self.assertEqual(again["summary"]["cumulative_candidates"], 1)
        self.assertEqual(again["items"][0]["occurrences"], 2)

    def test_load_items_empty_or_json(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "missing.json"
            self.assertEqual(load_items(path), [])
            path.write_text('{"items":[{"id":"A"}]}', encoding="utf-8")
            self.assertEqual(load_items(path), [{"id":"A"}])

if __name__ == "__main__":
    unittest.main()
