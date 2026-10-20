import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from MakeIndexesForDictionaries import build_dictionary, main, normalize, parse_records, plain_text, update_source


class ConverterTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        (self.root / "Main dictionary").mkdir()
        (self.root / "Student dictionary").mkdir()
        self.main_path = self.root / "Main dictionary/MBT_Root.dic"
        self.student_path = self.root / "Student dictionary/Dictionary.txt"
        self.main_path.write_text(
            "\\_sh v3.0\n\\og ~todo\n\\gl secret\n\\og a\n\\lx a\n"
            "\\gl I; me\n\\ie I (focus)\n\\ie me\n\\oi ad\n"
            "\\ex Kenà +a\n eg-ulì.\n\\tr I go home.\n\\dq editorial note\n"
            "\\og a\n\\lx a|d2|u\n\\gl ah\n\\ie ah\n"
            "\\og z.hidden\n\\gl working entry\n", encoding="utf-8")
        self.student_path.write_text(
            "\\lx ~todo\n\\nt secret\n\\lx abandon\n\\lx1\n"
            "\\de eg-engkeran\n\\re eg-engkeran\n\\re1 peg-engked\n"
            "\\dv Leave someone.\n\\xv1 They abandoned it.\n"
            "\\xe1 Mig-engkeran.\n\\se abandonment\n", encoding="utf-8")

    def build(self):
        return build_dictionary(self.root)

    def test_bom_multiline_repeated_fields_and_final_record(self):
        records = parse_records("\ufeff\\_sh header\r\n\\lx word\r\n\\de first\r\nwrapped\r\n\r\n\\de second", "lx")
        self.assertEqual(records, [[("lx", "word"), ("de", "first wrapped"), ("de", "second")]])

    def test_direction_homonyms_and_inflected_forms(self):
        data = self.build()
        ms = dict(data["indexes"]["matigsalug"])
        en = dict(data["indexes"]["english"])
        self.assertEqual(ms["a"], [0, 1])
        self.assertEqual(ms["ad"], [0])
        self.assertEqual(en["abandon"], [2])
        self.assertEqual(en["abandonment"], [2])
        self.assertEqual(ms["engkeran"], [2])
        self.assertEqual(ms["peg-engked"], [2])
        self.assertNotIn("abandon", ms)
        self.assertEqual(data["entries"][1]["headword"], "a₂")
        self.assertNotEqual(data["entries"][0]["id"], data["entries"][1]["id"])

    def test_online_fields_and_order_are_preserved(self):
        fields = self.build()["entries"][2]["fields"]
        self.assertEqual([f["marker"] for f in fields], ["de", "dv", "xv", "xe", "se"])
        self.assertEqual(fields[2]["text"], "They abandoned it.")

    def test_unfinished_placeholder_entries_are_not_published(self):
        with self.student_path.open('a', encoding='utf-8') as handle:
            handle.write('\\lx baley\n\\ph æ ə\n\\de à è ì ù\n\\re à è ì ù\n\\st\n')
        data = self.build()
        self.assertEqual(len(data['entries']), 3)
        self.assertNotIn('baley', dict(data['indexes']['english']))
        self.assertNotIn('a e i u', dict(data['indexes']['matigsalug']))

    def test_editorial_records_and_fields_are_excluded(self):
        data = self.build()
        serialized = json.dumps(data)
        self.assertNotIn("secret", serialized)
        self.assertNotIn("editorial note", serialized)
        self.assertEqual(data["sources"][0]["excludedRecords"], 2)
        self.assertEqual(data["sources"][0]["omittedFields"]["dq"], 1)

    def test_markup_unicode_and_search_normalization(self):
        self.assertEqual(plain_text("|fb{balèy} |vword|r +example |{emdash} fb:hello"), "balèy word example — hello")
        self.assertEqual(normalize("  BALE\u0300Y  "), "baley")
        self.assertEqual(normalize("æ ’"), "ae '")
        self.assertEqual(plain_text("a|d2|u"), "a₂")
        self.assertEqual(plain_text("|fb{|fb{thoh}} eg-ulì|"), "thoh eg-ulì")

    def test_indexes_are_sorted_and_references_valid(self):
        data = self.build()
        for index in data["indexes"].values():
            self.assertEqual([row[0] for row in index], sorted(row[0] for row in index))
            for _, ids in index:
                self.assertTrue(ids)
                self.assertEqual(ids, sorted(set(ids)))
                self.assertTrue(all(0 <= i < len(data["entries"]) for i in ids))

    def test_reproducible_output_and_check_mode(self):
        output = self.root / "assets/data.json"
        args = ["--source-repo", str(self.root), "--output", str(output)]
        main(args)
        first = output.read_bytes()
        main(args)
        self.assertEqual(first, output.read_bytes())
        self.assertEqual(main(args + ["--check"]), 0)
        self.main_path.write_text(self.main_path.read_text() + "\\og new\n\\gl new\n")
        with self.assertRaises(SystemExit) as error:
            main(args + ["--check"])
        self.assertEqual(error.exception.code, 1)
        self.assertEqual(first, output.read_bytes())

    def test_missing_source_does_not_replace_existing_output(self):
        output = self.root / "data.json"
        output.write_text("previous good data")
        self.student_path.unlink()
        with self.assertRaises(SystemExit):
            main(["--source-repo", str(self.root), "--output", str(output)])
        self.assertEqual(output.read_text(), "previous good data")

    def test_fetch_refuses_to_modify_dirty_source(self):
        with patch("MakeIndexesForDictionaries.subprocess.run") as run:
            run.return_value.stdout = " M Main dictionary/MBT_Root.dic\n"
            with self.assertRaisesRegex(ValueError, "local changes"):
                update_source(self.root)
            run.assert_called_once()


if __name__ == "__main__":
    unittest.main()
