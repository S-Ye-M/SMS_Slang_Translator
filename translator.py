from __future__ import annotations

import csv
import re
from collections import Counter
from dataclasses import dataclass
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
DATA_CANDIDATES = (BASE_DIR / "data" / "slang_dict.csv", BASE_DIR / "slang_dict.csv")


def read_csv_rows(path):
    with open(path, encoding="utf-8", newline="") as f:
        return [(r["abbreviation"], r["meaning"], r["category"], r["kind"]) for r in csv.DictReader(f)]


def load_rows(path=None):
    if path:
        return read_csv_rows(path)
    for p in DATA_CANDIDATES:
        if p.is_file():
            return read_csv_rows(p)
    from slang_data import ROWS
    return ROWS


DATA_PATH = DATA_CANDIDATES[0]

TOKEN_RE = re.compile(r"[A-Za-z0-9'’]+|\s+|[^\sA-Za-z0-9'’]")
WORD_RE = re.compile(r"[A-Za-z0-9'’]+")
ELONGATION_RE = re.compile(r"(.)\1{2,}")
MAX_PHRASE = 6

KINDS = {"abbr", "strict", "lower", "letter", "word", "phrase", "informal"}
REVERSIBLE_KINDS = {"abbr", "strict", "lower"}

DETERMINERS = {"the", "a", "an", "my", "your", "his", "her", "our", "their",
               "some", "any", "of", "no", "every", "each"}
KEEP_CASE_CATEGORIES = {"Tech & AI", "Work & School"}
KEEP_CASE_KEYS = {"FB", "IG", "YT"}
SMALL_WORDS = {"a", "an", "and", "the", "of", "or", "to", "in", "on", "for", "at", "by", "from", "is", "are"}


@dataclass(frozen=True)
class Entry:
    key: str
    meaning: str
    category: str
    kind: str


@dataclass
class Match:
    start: int
    end: int
    original: str
    abbreviation: str
    meaning: str
    category: str
    kind: str


def _is_title_case(text: str) -> bool:
    words = [w for w in text.split() if w[0].isalpha() and w.lower() not in SMALL_WORDS]
    return bool(words) and all(w[0].isupper() for w in words)


class SlangTranslator:
    def __init__(self, path: Path | str | None = None):
        self.entries: dict[str, Entry] = {}
        for abbr, meaning, category, kind in load_rows(path):
            key = abbr.strip().upper().replace("’", "'")
            kind = kind.strip()
            if kind not in KINDS:
                raise ValueError(f"Unknown kind {kind!r} for {key}")
            self.entries.setdefault(key, Entry(key, meaning.strip(), category.strip(), kind))
        self.categories = sorted({e.category for e in self.entries.values()})
        self.reverse = self._build_reverse()
        self._max_rev = max((len(k) for k in self.reverse), default=2)

    @property
    def slang(self) -> dict[str, str]:
        return {k: e.meaning for k, e in self.entries.items()}

    def stats(self) -> dict:
        return {
            "total": len(self.entries),
            "by_category": dict(Counter(e.category for e in self.entries.values())),
            "by_kind": dict(Counter(e.kind for e in self.entries.values())),
        }

    @staticmethod
    def _word_run(toks, i, n):
        idx = [i]
        j = i
        for _ in range(n - 1):
            if j + 2 < len(toks) and toks[j + 1][0] == " " and WORD_RE.fullmatch(toks[j + 2][0]):
                j += 2
                idx.append(j)
            else:
                return None
        return idx

    def _build_reverse(self) -> dict[tuple[str, ...], str]:
        rev: dict[tuple[str, ...], str] = {}
        for key, e in self.entries.items():
            if e.kind in REVERSIBLE_KINDS:
                words = tuple(re.findall(r"[a-z0-9']+", e.meaning.lower()))
                if len(words) >= 2:
                    rev.setdefault(words, key)
        return rev

    @staticmethod
    def _allowed(e: Entry, categories, include_words: bool) -> bool:
        if categories is not None and e.category not in categories:
            return False
        if e.kind == "word" and not include_words:
            return False
        return True

    def _single(self, tok, prev_word, next_is_word, categories, include_words) -> Entry | None:
        key = tok.upper().replace("’", "'")
        cands = [key]
        if ELONGATION_RE.search(key):
            cands += [ELONGATION_RE.sub(lambda m, k=k: m.group(1) * k, key) for k in (1, 2, 3)]
        for cand in cands:
            e = self.entries.get(cand)
            if e is None or e.kind == "phrase" or not self._allowed(e, categories, include_words):
                continue
            if e.kind == "strict" and tok != cand:
                continue
            if e.kind == "lower" and not tok.islower():
                continue
            if e.kind == "letter" and not (tok.islower() and next_is_word):
                continue
            if e.kind == "word" and prev_word in DETERMINERS:
                continue
            return e
        return None

    def _phrase(self, toks, i, categories, include_words):
        for n in range(MAX_PHRASE, 1, -1):
            idx = self._word_run(toks, i, n)
            if idx:
                key = " ".join(toks[k][0] for k in idx).upper().replace("’", "'")
                e = self.entries.get(key)
                if e and e.kind == "phrase" and self._allowed(e, categories, include_words):
                    return e, idx[-1]
        return None

    @staticmethod
    def _format(e: Entry, sentence_start: bool, trim_q: bool = False) -> str:
        m = e.meaning.rstrip("!?. " if trim_q else "!. ")
        if e.category in KEEP_CASE_CATEGORIES or e.key in KEEP_CASE_KEYS:
            s = m
        elif _is_title_case(m):
            s = re.sub(r"\bi\b", "I", m.lower())
        else:
            s = m if re.match(r"I\b", m) else m[:1].lower() + m[1:]
        return s[:1].upper() + s[1:] if sentence_start else s

    def segments(self, text: str, annotate: bool = False, include_words: bool = True,
                 categories=None) -> list[tuple[str, Match | None]]:
        categories = set(categories) if categories else None
        toks = [(m.group(), m.start(), m.end()) for m in TOKEN_RE.finditer(text)]
        out: list[tuple[str, Match | None]] = []
        i, prev_word, last = 0, None, None
        while i < len(toks):
            tok, start, end = toks[i]
            if WORD_RE.fullmatch(tok):
                sentence_start = last is None or last in ".!?"
                hit, j = self._phrase(toks, i, categories, include_words) or (None, i)
                if hit is None:
                    nxt = i + 2 < len(toks) and toks[i + 1][0].isspace() and bool(WORD_RE.fullmatch(toks[i + 2][0]))
                    hit = self._single(tok, prev_word, nxt, categories, include_words)
                if hit is not None:
                    span_end = toks[j][2]
                    original = text[start:span_end]
                    m = Match(start, span_end, original, hit.key, hit.meaning, hit.category, hit.kind)
                    trim_q = text[span_end:span_end + 1] in ("?", "!", ".")
                    shown = (f"{original} ({hit.meaning.rstrip('!. ')})" if annotate
                             else self._format(hit, sentence_start, trim_q))
                    out.append((shown, m))
                    prev_word, last, i = original.split()[-1].lower(), original, j + 1
                    continue
                out.append((tok, None))
                prev_word, last = tok.lower(), tok
            else:
                out.append((tok, None))
                if not tok.isspace():
                    prev_word, last = None, tok
            i += 1
        return out

    def translate(self, text: str, annotate: bool = False, include_words: bool = True,
                  categories=None) -> str:
        return "".join(s for s, _ in self.segments(text, annotate, include_words, categories))

    def find(self, text: str, include_words: bool = True, categories=None) -> list[Match]:
        return [m for _, m in self.segments(text, False, include_words, categories) if m]

    def to_slang(self, text: str, categories=None) -> str:
        categories = set(categories) if categories else None
        toks = [(m.group(), m.start(), m.end()) for m in TOKEN_RE.finditer(text)]
        out, i = [], 0
        while i < len(toks):
            done = False
            if WORD_RE.fullmatch(toks[i][0]):
                for n in range(self._max_rev, 1, -1):
                    idx = self._word_run(toks, i, n)
                    if not idx:
                        continue
                    words = tuple(toks[k][0].lower().replace("’", "'") for k in idx)
                    key = self.reverse.get(words)
                    if key and (categories is None or self.entries[key].category in categories):
                        out.append(key)
                        i, done = idx[-1] + 1, True
                        break
            if not done:
                out.append(toks[i][0])
                i += 1
        return "".join(out)
