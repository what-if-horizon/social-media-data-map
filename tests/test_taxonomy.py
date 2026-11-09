"""Run with: python -m unittest discover -s tests -v   (from the repo root)"""
import os
import subprocess
import unittest

from src.inference import prompts
from src.inference.parallel import output_name
from src.inference.taxonomy import build_prompt, extract_json_dict, parse_prediction, valid_labels

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TEMPLATE = prompts.kmetty2026()
LABELS = valid_labels(TEMPLATE)


class TestPrompt(unittest.TestCase):
    def test_fifteen_labels(self):
        self.assertEqual(len(LABELS), 15)
        self.assertIn("Login data", LABELS)

    def test_build_prompt_keeps_json_braces(self):
        out = build_prompt(TEMPLATE, "a/b.json")
        self.assertTrue(out.rstrip().endswith("a/b.json"))
        self.assertNotIn("{PATH}", out.split("# Path to classify")[1])


class TestParse(unittest.TestCase):
    GOOD = '{"path": "a", "predictions": [{"label": "Login data", "confidence": 90}], "rationale": "r"}'

    def test_plain(self):
        self.assertIsNotNone(parse_prediction(self.GOOD, LABELS))

    def test_text_and_think_around(self):
        self.assertIsNotNone(parse_prediction("reasoning {x} </think> sure: " + self.GOOD + " bye", LABELS))

    def test_unknown_label(self):
        self.assertIsNone(parse_prediction('{"predictions": [{"label": "Foo"}]}', LABELS))

    def test_not_json_or_not_str(self):
        self.assertIsNone(parse_prediction("nothing", LABELS))
        self.assertIsNone(parse_prediction(None, LABELS))
        self.assertIsNone(parse_prediction('{"predictions": []}', LABELS))


class TestExtract(unittest.TestCase):
    def test_object_inside_array(self):
        raw = 'think </think> [\n{"estimated_path": "a/b"}\n]'
        self.assertEqual(extract_json_dict(raw), {"estimated_path": "a/b"})

    def test_none(self):
        self.assertIsNone(extract_json_dict("no json"))
        self.assertIsNone(extract_json_dict(None))


class TestOutputName(unittest.TestCase):
    PATTERNS = [
        "{platform}_{n}_class_ids_kmetty2026_ES_NL_gpt-oss-20b_tp1x4tp.json",
        "{platform}_{n}_std_ids_ES_NL_gpt-oss-20b_tp1x4tp.json",
        "{stem}_out.json",
    ]
    FILE = "facebook_merged_structures_12.csv"

    def test_python(self):
        self.assertEqual(output_name(self.PATTERNS[0], "facebook", self.FILE),
                         "facebook_12_class_ids_kmetty2026_ES_NL_gpt-oss-20b_tp1x4tp.json")
        self.assertEqual(output_name(self.PATTERNS[2], "facebook", self.FILE), "facebook_merged_structures_12_out.json")

    def test_launcher_matches_python(self):
        """Extract output_name() from parallel_llm.sh and run it, so the two cannot drift apart."""
        launcher = os.path.join(ROOT, "launchers", "parallel_llm.sh")
        for pattern in self.PATTERNS:
            script = (
                'src=$(sed -n "/^output_name() {/,/^}/p" ' + launcher + ');'
                'PLATFORM=facebook; OUTPUT_PATTERN="$1";'
                'eval "$src"; output_name ' + self.FILE
            )
            out = subprocess.run(["bash", "-c", script, "_", pattern], capture_output=True, text=True, check=True).stdout.strip()
            self.assertEqual(out, output_name(pattern, "facebook", self.FILE))


if __name__ == "__main__":
    unittest.main()
