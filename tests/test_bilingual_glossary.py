"""Unit tests for the bilingual glossary helper."""
from __future__ import annotations

import json
from pathlib import Path

import pytest

from core.bilingual_glossary import BilingualGlossary, GlossaryEntry


def test_register_and_lookup_round_trip():
    glossary = BilingualGlossary()
    glossary.register("posterior mean", {"zh": "后验均值"}, source="manual")

    assert glossary.lookup("posterior mean", "zh") == "后验均值"
    assert glossary.lookup("Posterior Mean", "zh") == "后验均值"  # case-insensitive
    assert glossary.lookup("posterior mean", "en") is None  # no en translation registered


def test_register_with_invalid_lang_raises():
    glossary = BilingualGlossary()
    with pytest.raises(ValueError, match="unsupported lang"):
        glossary.register("term", {"fr": "terme"})


def test_lookup_with_invalid_lang_raises():
    glossary = BilingualGlossary()
    glossary.register("term", {"zh": "术语"})
    with pytest.raises(ValueError, match="unsupported lang"):
        glossary.lookup("term", "fr")


def test_lookup_returns_none_for_missing_term():
    glossary = BilingualGlossary()
    assert glossary.lookup("never registered", "zh") is None


def test_load_and_dump_round_trip(tmp_path: Path):
    path = tmp_path / "glossary.json"
    g1 = BilingualGlossary(path=path)
    g1.register("anchor", {"zh": "锚点"}, source="tier-definitions.md")
    g1.register(
        "moment-matched Beta posterior",
        {"zh": "矩匹配 Beta 后验"},
        source="methodology.md",
        notes="never use 'conjugate'",
    )
    g1.dump()

    g2 = BilingualGlossary.load(path)
    assert g2.lookup("anchor", "zh") == "锚点"
    assert g2.lookup("MOMENT-MATCHED BETA POSTERIOR", "zh") == "矩匹配 Beta 后验"
    assert "never use 'conjugate'" in g2.entries["moment-matched beta posterior"].notes
    assert len(g2) == 2


def test_dump_without_path_raises():
    glossary = BilingualGlossary()  # no path
    glossary.register("anchor", {"zh": "锚点"})
    with pytest.raises(ValueError, match="dump\\(\\) requires a path"):
        glossary.dump()


def test_load_missing_file_returns_empty_glossary(tmp_path: Path):
    path = tmp_path / "nonexistent.json"
    glossary = BilingualGlossary.load(path)
    assert len(glossary) == 0
    assert glossary.path == path


def test_dump_creates_parent_directories(tmp_path: Path):
    path = tmp_path / "deep" / "nested" / "glossary.json"
    glossary = BilingualGlossary(path=path)
    glossary.register("anchor", {"zh": "锚点"})
    glossary.dump()
    assert path.exists()
    payload = json.loads(path.read_text(encoding="utf-8"))
    assert payload["entries"][0]["term"] == "anchor"


def test_register_replaces_existing_entry():
    glossary = BilingualGlossary()
    glossary.register("anchor", {"zh": "锚点"}, source="v1")
    glossary.register("anchor", {"zh": "锚点-revised"}, source="v2")
    assert glossary.lookup("anchor", "zh") == "锚点-revised"
    assert glossary.entries["anchor"].source == "v2"


def test_merge_multiple_entries():
    glossary = BilingualGlossary()
    glossary.register("anchor", {"zh": "锚点"})
    extras = [
        GlossaryEntry(term="core", translations={"zh": "核心"}),
        GlossaryEntry(term="anchor", translations={"zh": "锚点-overridden"}),  # collision
    ]
    n = glossary.merge(extras)
    assert n == 2
    assert glossary.lookup("anchor", "zh") == "锚点-overridden"
    assert glossary.lookup("core", "zh") == "核心"


def test_dump_is_deterministic(tmp_path: Path):
    path1 = tmp_path / "g1.json"
    path2 = tmp_path / "g2.json"
    g1 = BilingualGlossary(path=path1)
    g2 = BilingualGlossary(path=path2)
    g1.register("zebra", {"zh": "斑马"})
    g1.register("anchor", {"zh": "锚点"})
    g2.register("anchor", {"zh": "锚点"})
    g2.register("zebra", {"zh": "斑马"})
    g1.dump()
    g2.dump()
    assert path1.read_text(encoding="utf-8") == path2.read_text(encoding="utf-8")


def test_contains_operator():
    glossary = BilingualGlossary()
    glossary.register("anchor", {"zh": "锚点"})
    assert "anchor" in glossary
    assert "ANCHOR" in glossary
    assert "core" not in glossary
    assert 42 not in glossary  # type: ignore[operator]
