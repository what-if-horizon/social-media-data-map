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
                'OUTPUT_PATTERN="$1";'
                'eval "$src"; output_name facebook ' + self.FILE
            )
            out = subprocess.run(["bash", "-c", script, "_", pattern], capture_output=True, text=True, check=True).stdout.strip()
            self.assertEqual(out, output_name(pattern, "facebook", self.FILE))


class TestRunBucketLayout(unittest.TestCase):
    def test_platform_subfolders(self):
        """A job over several platforms (INPUT_GLOB='*/*.csv') writes <output>/<platform>/<name>."""
        import tempfile
        from src.inference.parallel import run_bucket

        with tempfile.TemporaryDirectory() as out:
            run_bucket(["facebook/facebook_smoke_5.csv", "x/x_smoke_5.csv"], "/src/smoke", out, "gpu0",
                       lambda src, dst: open(dst, "w").write("[]"), "{platform}_{n}_out.json")
            self.assertTrue(os.path.exists(os.path.join(out, "facebook", "facebook_5_out.json")))
            self.assertTrue(os.path.exists(os.path.join(out, "x", "x_5_out.json")))

    def test_flat_folder_uses_source_folder_name(self):
        import tempfile
        from src.inference.parallel import run_bucket

        with tempfile.TemporaryDirectory() as out:
            run_bucket(["facebook_merged_structures_3.csv"], "/src/facebook", out, "gpu0",
                       lambda src, dst: open(dst, "w").write("[]"), "{platform}_{n}_out.json")
            self.assertTrue(os.path.exists(os.path.join(out, "facebook_3_out.json")))


if __name__ == "__main__":
    unittest.main()


class TestSimplePrompt(unittest.TestCase):
    """kmetty2026_simple differs from kmetty2026 in the topology (the definitions), the decision rules and in asking for five labels."""

    def setUp(self):
        from src.inference.taxonomy import label_list
        self.base, self.simple = prompts.kmetty2026(), prompts.kmetty2026_simple()
        self.label_list = label_list

    @staticmethod
    def around_topology(text):
        """Role and steps (with 'five' read as 'three'), and the part from the path on."""
        head = text[:text.index("# DDP topology")].replace("five", "three")
        return head, text[text.index("# Path to classify"):]

    def test_same_labels_in_the_same_order(self):
        self.assertEqual(self.label_list(self.base), self.label_list(self.simple))
        self.assertEqual(len(self.label_list(self.simple)), 15)
        self.assertEqual(valid_labels(self.base), valid_labels(self.simple))

    def test_everything_but_topology_and_decision_rules_is_identical(self):
        self.assertEqual(self.around_topology(self.base), self.around_topology(self.simple))

    def test_asks_for_five_valid_examples(self):
        import json, re
        from src.inference.taxonomy import validate_record
        self.assertIn("exactly five different labels", self.simple)
        examples = [json.loads(m.group(1)) for m in re.finditer(r"^Output: (.*)$", self.simple, re.M)]
        self.assertEqual(len(examples), 5)
        for rec in examples:
            self.assertEqual(validate_record(rec, valid_labels(self.simple), n=5), [])

    def test_definitions_differ(self):
        self.assertNotEqual(self.base, self.simple)
        self.assertIn("the platform itself concludes", self.simple)
        self.assertNotIn("the platform itself concludes", self.base)

    def test_decision_rules_are_the_simplified_ones(self):
        rules = lambda t: t[t.index("# Decision rules"):t.index("# Confidence scoring")]
        self.assertIn("mention the other option in your rationale", rules(self.simple))
        self.assertIn("give the other as the second option", rules(self.base))
        self.assertNotIn("give the other as the second option", rules(self.simple))
        for pair in ("Network (ego ties) vs. Ratings and interests", "Passive consumption and exposure vs. Human-machine dialogue",
                     "Semantically specified vs. semantically unspecified"):
            self.assertIn(pair, rules(self.simple))

    def test_path_placeholder_and_parent_headings_kept(self):
        self.assertTrue(build_prompt(self.simple, "a/b.json").rstrip().endswith("a/b.json"))
        for heading in ("## Service-provider-related data", "## User-related data: Semantically specified",
                        "## User-related data: Semantically unspecified"):
            self.assertIn(heading, self.simple)
