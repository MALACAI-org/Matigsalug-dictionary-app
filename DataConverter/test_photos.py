from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from PIL import Image

from MakeIndexesForDictionaries import normalize
from photos import match_photo, prepare_photos, publish_photo_report


class PhotoTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.photos = self.root / "Dictionary photos"
        self.photos.mkdir()
        self.output = self.root / "assets/dictionary.json"

    def data(self):
        return {
            "entries": [
                {"id": "main:abaka:1", "source": "main", "headword": "abaka"},
                {"id": "student:abaca:1", "source": "student", "headword": "abaca"},
            ],
            "indexes": {"matigsalug": [["abaka", [0, 1]]]},
            "attribution": {"changes": "Converted."},
        }

    def write_photo(self, name, color="green"):
        path = self.photos / name
        path.parent.mkdir(parents=True, exist_ok=True)
        with Image.new("RGB", (1600, 1000), color) as picture:
            exif = Image.Exif()
            exif[274] = 6  # Rotate 90 degrees; resized output must stay upright.
            exif[315] = "Original metadata"
            picture.save(path, exif=exif)
        return path

    def prepare(self, data=None, **kwargs):
        return prepare_photos(data or self.data(), self.root, self.output, normalize, **kwargs)

    def test_resize_orientation_metadata_and_both_dictionary_links(self):
        original = self.write_photo("abaka.1.JPG")
        before = original.read_bytes()
        data = self.data()
        report = self.prepare(data)
        item = report["files"][0]
        output = self.output.parent / "photos" / Path(item["asset"]).name
        with Image.open(output) as picture:
            self.assertEqual(picture.format, "WEBP")
            self.assertEqual(picture.size, (600, 960))
            self.assertFalse(picture.getexif())
        self.assertEqual(original.read_bytes(), before)
        self.assertEqual(data["entries"][0]["photos"], data["entries"][1]["photos"])
        self.assertLess(item["bytes"], len(before))

    def test_cache_check_and_source_changes(self):
        original = self.write_photo("abaka.jpg")
        report = self.prepare()
        publish_photo_report(report, self.output)
        output = self.output.parent / "photos" / Path(report["files"][0]["asset"]).name
        old_stat = output.stat().st_mtime_ns
        with patch("PIL.Image.open", side_effect=AssertionError("should reuse unchanged photo")):
            checked = self.prepare(check=True)
            publish_photo_report(checked, self.output, check=True)
        self.assertEqual(output.stat().st_mtime_ns, old_stat)
        self.write_photo(original.name, "red")
        with self.assertRaisesRegex(ValueError, "missing or stale"):
            self.prepare(check=True)
        # Failed verification does not touch the previous good assets.
        self.assertEqual(output.stat().st_mtime_ns, old_stat)
        refreshed = self.prepare()
        note = output.parent / "keep.txt"
        note.write_text("user file")
        publish_photo_report(refreshed, self.output)
        self.assertFalse(output.exists())
        self.assertTrue(note.exists())

    def test_duplicate_images_are_stored_once_and_unknown_names_reported(self):
        first = self.write_photo("abaka.jpg")
        other = self.photos / "New/abaka.2.JPG"
        other.parent.mkdir()
        other.write_bytes(first.read_bytes())
        self.write_photo("unknown.jpg")
        data = self.data()
        report = self.prepare(data)
        self.assertEqual(report["matchedFiles"], 2)
        self.assertEqual(report["images"], 1)
        self.assertEqual(len(data["entries"][0]["photos"]), 1)
        self.assertEqual(report["skipped"][0]["source"], "unknown.jpg")

    def test_missing_collection_is_an_error_but_empty_collection_retires_photos(self):
        original = self.write_photo("abaka.jpg")
        report = self.prepare()
        publish_photo_report(report, self.output)
        output = self.output.parent / "photos" / Path(report["files"][0]["asset"]).name
        moved = self.root / "temporarily unavailable"
        self.photos.rename(moved)
        with self.assertRaisesRegex(ValueError, "photo folder is missing"):
            self.prepare()
        self.assertTrue(output.exists())
        moved.rename(self.photos)
        original.unlink()
        empty = self.prepare()
        self.assertEqual(empty["images"], 0)
        publish_photo_report(empty, self.output)
        self.assertFalse(output.exists())

    def test_homonyms_require_an_unambiguous_name(self):
        entries = [
            {"source": "main", "headword": "baley₁"},
            {"source": "main", "headword": "baley₂"},
            {"source": "student", "headword": "house"},
        ]
        index = {"baley": [0, 1, 2]}
        headwords = {"baley₁": [0], "baley₂": [1]}
        matches, _, reason = match_photo("baley", entries, index, headwords, normalize)
        self.assertEqual(matches, [])
        self.assertIn("ambiguous", reason)
        matches, _, reason = match_photo("baley1.1", entries, index, headwords, normalize)
        self.assertEqual(matches, [0])
        self.assertIsNone(reason)


if __name__ == "__main__":
    unittest.main()
