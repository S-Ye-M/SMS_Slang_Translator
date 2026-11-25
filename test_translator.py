import csv
from pathlib import Path

import pytest

from translator import KINDS, SlangTranslator

t = SlangTranslator()


@pytest.mark.parametrize("src,expected", [
    ("brb", "Be right back"),
    ("BRB, omw", "Be right back, on my way"),
    ("cul8r", "See you later"),
    ("lolll that was gr8!", "Laughing out loud that was great!"),
    ("ilysm", "I love you so much"),
    ("zzzz", "Sleeping, bored, tired"),
    ("I got a W", "I got a win"),
    ("hello world", "hello world"),
    ("it is time to kiss the goat", "it is time to kiss the goat"),
    ("l", "l"),
    ("no cap fr", "No lie; for real for real"),
    ("that slaps", "that is excellent (usually music)"),
    ("this is fire", "this is excellent"),
    ("I love the fire", "I love the fire"),
    ("r u ok", "Are you ok"),
    ("R&B", "R&B"),
    ("bc i said so", "Because i said so"),
    ("BC", "BC"),
    ("pm", "pm"),
    ("send a PM", "send a private message"),
    ("gonna touch grass tmrw", "Going to go outside and take a break from the internet tomorrow"),
    ("I can’t even", "I'm overwhelmed"),
    ("wyd? idk tbh", "What you doing? I don't know to be honest"),
])
def test_forward(src, expected):
    assert t.translate(src) == expected


def test_annotate():
    assert t.translate("BRB", annotate=True) == "BRB (Be Right Back)"


def test_no_words_toggle():
    assert t.translate("that slaps", include_words=False) == "that slaps"
    assert t.translate("brb", include_words=False) == "Be right back"


def test_category_filter():
    assert t.translate("brb ai", categories={"Tech & AI"}) == "brb Artificial Intelligence"


def test_find_and_segments():
    m = t.find("ok btw idk no cap")
    assert [x.abbreviation for x in m] == ["BTW", "IDK", "NO CAP"]
    assert m[2].original == "no cap" and m[2].category == "Phrases"


def test_reverse():
    assert t.to_slang("talk to you later") == "TTYL"
    assert t.to_slang("let me know, in my opinion") == "LMK, IMO"
    assert t.to_slang("see you later") == "CUL8R"


def test_dictionary_integrity():
    rows = list(csv.DictReader(open(Path("data/slang_dict.csv"), encoding="utf-8")))
    keys = [r["abbreviation"] for r in rows]
    assert len(keys) == len(set(keys)), "duplicate keys"
    assert len(rows) >= 500
    assert {r["kind"] for r in rows} <= KINDS
    assert all(r["meaning"] and r["category"] for r in rows)


def test_embedded_data_matches_csv():
    from slang_data import ROWS
    from translator import read_csv_rows
    assert [tuple(r) for r in ROWS] == read_csv_rows("data/slang_dict.csv")
