from __future__ import annotations

import importlib.util
import sys
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
ANALYZER_PATH = REPO_ROOT / "scripts" / "analyze_past_papers.py"


def load_analyzer():
    spec = importlib.util.spec_from_file_location("analyze_past_papers_public", ANALYZER_PATH)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


class PublicContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.analyzer = load_analyzer()

    def test_answer_parser_variants(self):
        cases = [
            (
                "Q1\nAnswer (English option text): d. protein is high\nExplanation (English): intracellular proteins are trapped inside cells.",
                "d. protein is high",
                "intracellular proteins are trapped inside cells.",
            ),
            (
                "Q1\nAnswer (English only): A. a change in allele frequencies in a population\nExplanation (English): evolution is defined at the population level.",
                "A. a change in allele frequencies in a population",
                "evolution is defined at the population level.",
            ),
            (
                "Q1\nAnswer (English option content only): Sigma\nExplanation (EN): sigma recognizes the bacterial promoter.",
                "Sigma",
                "sigma recognizes the bacterial promoter.",
            ),
        ]
        for block, expected_answer, expected_explanation in cases:
            answer, explanation, _answer_variant, _explanation_variant = self.analyzer.parse_answer_block(block)
            self.assertEqual(answer, expected_answer)
            self.assertEqual(explanation, expected_explanation)

    def test_retention_bands(self):
        self.assertEqual(self.analyzer.retention_band(4, 5), "Anchor")
        self.assertEqual(self.analyzer.retention_band(3, 5), "Core")
        self.assertEqual(self.analyzer.retention_band(2, 5), "Recurring")
        self.assertEqual(self.analyzer.retention_band(1, 5), "One-off")
        self.assertEqual(self.analyzer.retention_band(3, 4), "Anchor")

    def test_question_numbers_support(self):
        text = "\n".join(
            [
                "QUESTION 1",
                "A. alpha",
                "QUESTION 2",
                "A. beta",
                "QUESTION 4",
                "A. delta",
            ]
        )
        blocks = self.analyzer.build_question_blocks(text, [1, 2, 4], "paper")
        self.assertEqual([block["number"] for block in blocks], [1, 2, 4])

    def test_english_output_text_strips_cjk(self):
        value = self.analyzer.english_output_text("Cardiac Stimulation increase想")
        self.assertEqual(value, "Cardiac Stimulation increase")

    def test_auxiliary_papers_do_not_define_formal_years_when_explicit(self):
        spec = {
            "course_id": "demo",
            "course_name": "Demo",
            "output_language": "en",
            "slides_dir": "/tmp/slides",
            "formal_years": ["2021", "2022"],
            "papers": [
                {"year": "Revision", "role": "auxiliary", "pdf": "/tmp/revision.pdf", "expected_questions": 10},
                {"year": "2021", "role": "formal", "pdf": "/tmp/2021.pdf", "expected_questions": 10},
                {"year": "2022", "role": "formal", "pdf": "/tmp/2022.pdf", "expected_questions": 10},
            ],
            "answer_keys": [],
            "manual_overrides": {},
        }
        import json
        import tempfile

        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "spec.json"
            path.write_text(json.dumps(spec), encoding="utf-8")
            loaded = self.analyzer.load_course_spec(path)
            self.assertEqual(loaded.formal_years, ["2021", "2022"])


if __name__ == "__main__":
    unittest.main()
