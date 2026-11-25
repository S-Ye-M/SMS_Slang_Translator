# SMS_Slang_Translator


# 💬 SMS Slang Translator

> Decode SMS abbreviations, internet slang and Gen Z phrases into plain English, and turn plain English back into texting shorthand.

![Python](https://img.shields.io/badge/Python-3.9%2B-3776AB?logo=python&logoColor=white)
![Streamlit](https://img.shields.io/badge/UI-Streamlit-FF4B4B?logo=streamlit&logoColor=white)
![NLP](https://img.shields.io/badge/NLP-rule--based-8b5cf6)
![Tests](https://img.shields.io/badge/tests-29%20passing-brightgreen)
![License](https://img.shields.io/badge/license-MIT-blue)

A rule-based NLP project with a 678-entry slang dictionary, a command-line tool and a Streamlit web app styled like a chat conversation.

## Demo

```text
$ python cli.py "omg ngl that was gr8, brb lolll. cul8r!"
Oh my god not gonna lie that was great, be right back laughing out loud. See you later!

$ python cli.py --annotate "idk tbh, ttyl"
idk (I Don't Know) tbh (To Be Honest), ttyl (Talk To You Later)

$ python cli.py "no cap that slaps, gonna touch grass 2day"
No lie; for real that is excellent (usually music), going to go outside and take a break from the internet today

$ python cli.py --reverse "talk to you later, let me know what you think"
TTYL, LMK what you think
```

## Features

- **678 dictionary entries** across 11 categories
- **Phrase matching** for multi-word slang (`no cap`, `touch grass`, `spill the tea`)
- **Typo and elongation handling**: `lolll` becomes `LOL`, `zzzz` becomes `ZZZ`
- **Ambiguity rules** so normal words are not translated by mistake (`L`, `PM`, `RAM`, `the fire`)
- **Reverse translation** from English phrases to abbreviations
- **Annotate mode**: `BRB (Be Right Back)`
- **Category filter** and a toggle for slang words
- **Streamlit UI** with chat bubbles, highlighted slang, searchable dictionary and CSV export
- **CLI** with interactive mode
- **29 pytest tests**, including dictionary integrity checks

## Getting started

```bash
git clone https://github.com/S-Ye-M/sms-slang-translator.git
cd sms-slang-translator
pip install -r requirements.txt
```

### Web app

```bash
streamlit run app.py
```

### Command line

```bash
python cli.py "brb, omw"                  # slang -> English
python cli.py --annotate "idk tbh"        # show abbreviation + meaning
python cli.py --no-words "that slaps"     # skip slang words like fire, tea, slay
python cli.py --reverse "talk to you later"
python cli.py --stats                     # dictionary statistics
python cli.py                             # interactive mode
```

### Python API

```python
from translator import SlangTranslator

t = SlangTranslator()

t.translate("cul8r, ttyl")                          # 'See you later, talk to you later'
t.translate("BRB", annotate=True)                   # 'BRB (Be Right Back)'
t.translate("brb ai", categories={"Tech & AI"})     # 'brb Artificial Intelligence'
t.to_slang("let me know")                           # 'LMK'
t.find("ok btw idk no cap")                         # list of Match objects with position and category
```

### Tests

```bash
pytest
```

## How it works

| Step | What happens |
|---|---|
| 1. Tokenization | A regex splits text into words, spaces and punctuation. `CUL8R`, `B4N` and `y'all` stay as single tokens. |
| 2. Normalization | Lookup is case-insensitive, and repeated letters are collapsed (`lolll` to `LOL`). |
| 3. Phrase matching | Longest-match search finds multi-word slang before single tokens. |
| 4. Ambiguity rules | Each entry has a `kind` that controls when it may be translated (see below). |
| 5. Detokenization | Punctuation is preserved, sentence starts are capitalised and `I` is fixed. |
| 6. Reverse translation | English phrases of two or more words map back to their shortest abbreviation. |

### Entry kinds

| Kind | Behaviour | Example |
|---|---|---|
| `abbr` | Safe shorthand, any case | `BRB`, `brb` |
| `strict` | Also a real word, so UPPERCASE only | `L`, `W`, `PM`, `RAM` |
| `lower` | Also an uppercase acronym, so lowercase only | `bc`, `gl`, `np` |
| `letter` | Single-letter shorthand, lowercase and followed by a word | `r u ok` |
| `word` | Real English word with a slang meaning. Skipped after a determiner. | `fire`, `tea`, `slay` |
| `phrase` | Multi-word slang | `no cap`, `touch grass` |
| `informal` | Casual spellings | `gonna`, `tho`, `2day` |

## Dictionary

| Category | Entries |
|---|---|
| Texting & Chat | 228 |
| Gen Z Slang | 87 |
| Informal Words | 66 |
| Tech & AI | 61 |
| Gaming | 48 |
| Phrases | 43 |
| Greetings & Farewells | 40 |
| Reactions & Laughter | 33 |
| Work & School | 27 |
| Love & Dating | 24 |
| Social Media | 21 |

The data lives in `data/slang_dict.csv` with the columns `abbreviation`, `meaning`, `category`, `kind`. To add a new entry, append a row. If the CSV is not found, the app falls back to the identical copy in `slang_data.py`.

## Project structure

```text
.
├── app.py                  # Streamlit web app
├── cli.py                  # command-line interface
├── translator.py           # core NLP pipeline
├── slang_data.py           # same dictionary embedded as Python (fallback if the CSV is missing)
├── data/
│   └── slang_dict.csv      # slang dictionary
├── test_translator.py      # pytest suite
├── requirements.txt
└── .streamlit/
    └── config.toml         # dark theme
```

## Limitations

- The translator is dictionary-based, so slang that is not in the CSV is not detected.
- The context rule for slang words is simple (determiner check). A sentence like "I need some fire wood" can still be misread.
- English only.

## Roadmap

- [ ] Fuzzy matching for typos (`rapidfuzz`)
- [ ] POS-based disambiguation with spaCy
- [ ] Fine-tuned seq2seq model (T5 or BART) for context-aware translation
- [ ] Banglish and regional slang support
- [ ] Deploy on Streamlit Community Cloud

## Author

**Sayem Mahmud** · [GitHub](https://github.com/S-Ye-M) · [LinkedIn](https://linkedin.com/in/sayem-mahmud-228852298)

## License

Released under the [MIT License](LICENSE).
