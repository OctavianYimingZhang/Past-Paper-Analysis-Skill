"""Bilingual glossary helper for the past-paper-analysis suite.

Stores a JSON-backed map of canonical English ↔ Chinese translations for
domain-specific terminology (statistical jargon, exam-board terms, KP
labels). Spokes that emit bilingual prose look up terms here so the same
term always renders the same way across the report. Pattern is adapted
from `deusyu/translate-book` (MIT, verified).

Provenance: see `references/external-borrowings.md` for license check
and what was actually copied. Only the *pattern* (JSON term map +
case-insensitive lookup + provenance metadata) was lifted; no code was
copied verbatim.

Usage::

    from core.bilingual_glossary import BilingualGlossary

    glossary = BilingualGlossary.load("references/glossary.json")
    zh = glossary.lookup("posterior mean", "zh")
    if zh is None:
        glossary.register("posterior mean", {"zh": "后验均值"}, source="manual")
        glossary.dump("references/glossary.json")

The lookup is intentionally strict — partial / fuzzy matching is out of
scope. Spokes that need fuzzy matching should normalise terms before
calling ``lookup``.
"""
from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Iterable


_SUPPORTED_LANGS: tuple[str, ...] = ("en", "zh")


@dataclass(frozen=True)
class GlossaryEntry:
    """One row of the glossary."""

    term: str
    translations: dict[str, str]
    source: str = "manual"
    notes: str = ""

    def to_jsonable(self) -> dict:
        return {
            "term": self.term,
            "translations": dict(self.translations),
            "source": self.source,
            "notes": self.notes,
        }

    @classmethod
    def from_jsonable(cls, payload: dict) -> "GlossaryEntry":
        return cls(
            term=str(payload["term"]),
            translations={
                str(k): str(v) for k, v in payload.get("translations", {}).items()
            },
            source=str(payload.get("source", "manual")),
            notes=str(payload.get("notes", "")),
        )


@dataclass
class BilingualGlossary:
    """Mutable glossary store keyed by lower-cased English term.

    Designed for in-memory use during a single suite run plus persisted to
    disk so subsequent runs reuse the same translations.
    """

    entries: dict[str, GlossaryEntry] = field(default_factory=dict)
    path: Path | None = None

    @classmethod
    def load(cls, path: str | Path) -> "BilingualGlossary":
        p = Path(path)
        if not p.exists():
            return cls(entries={}, path=p)
        raw = json.loads(p.read_text(encoding="utf-8"))
        entries = {
            cls._key(row["term"]): GlossaryEntry.from_jsonable(row)
            for row in raw.get("entries", [])
        }
        return cls(entries=entries, path=p)

    def dump(self, path: str | Path | None = None) -> Path:
        target = Path(path) if path is not None else self.path
        if target is None:
            raise ValueError("dump() requires a path or a glossary loaded with one")
        payload = {
            "entries": [
                self.entries[key].to_jsonable()
                for key in sorted(self.entries)
            ],
        }
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
        self.path = target
        return target

    def lookup(self, term: str, target_lang: str) -> str | None:
        """Return the translation in ``target_lang`` or ``None`` when missing."""
        if target_lang not in _SUPPORTED_LANGS:
            raise ValueError(f"unsupported lang: {target_lang!r}; expected one of {_SUPPORTED_LANGS}")
        entry = self.entries.get(self._key(term))
        if entry is None:
            return None
        return entry.translations.get(target_lang)

    def register(
        self,
        term: str,
        translations: dict[str, str],
        *,
        source: str = "manual",
        notes: str = "",
    ) -> GlossaryEntry:
        """Insert or replace a glossary entry; returns the stored entry."""
        for lang in translations:
            if lang not in _SUPPORTED_LANGS:
                raise ValueError(f"unsupported lang: {lang!r}; expected one of {_SUPPORTED_LANGS}")
        entry = GlossaryEntry(
            term=term,
            translations=dict(translations),
            source=source,
            notes=notes,
        )
        self.entries[self._key(term)] = entry
        return entry

    def merge(self, other: Iterable[GlossaryEntry]) -> int:
        """Merge another iterable of entries; later entries win on conflict."""
        n = 0
        for entry in other:
            self.entries[self._key(entry.term)] = entry
            n += 1
        return n

    def __len__(self) -> int:  # pragma: no cover — trivial
        return len(self.entries)

    def __contains__(self, term: object) -> bool:
        if not isinstance(term, str):
            return False
        return self._key(term) in self.entries

    @staticmethod
    def _key(term: str) -> str:
        return term.strip().lower()


__all__ = ("BilingualGlossary", "GlossaryEntry")
