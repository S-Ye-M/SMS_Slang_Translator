import html

import pandas as pd
import streamlit as st

from translator import SlangTranslator

st.set_page_config(page_title="SMS Slang Translator", page_icon="💬", layout="wide")


@st.cache_resource
def load_translator() -> SlangTranslator:
    return SlangTranslator()


t = load_translator()
stats = t.stats()

KIND_LABEL = {
    "abbr": "Abbreviation", "strict": "Abbreviation (CAPS only)", "lower": "Abbreviation (lowercase)",
    "letter": "Letter shorthand", "word": "Slang word", "phrase": "Phrase", "informal": "Informal spelling",
}
EXAMPLES = [
    "omg ngl that was gr8, brb lolll. cul8r!",
    "idk tbh, no cap that fit is fire. hmu tmrw?",
    "gonna touch grass 2day, ttyl. ily bestie 💜",
    "r u coming rn? wyd? omw g2g, ty!",
]

st.markdown("""
<style>
#MainMenu, footer, header [data-testid="stToolbar"] {visibility: hidden;}
.block-container {padding-top: 2.2rem; max-width: 1100px;}
.hero {padding: 1.6rem 1.8rem; border-radius: 22px; margin-bottom: 1.2rem;
  background: radial-gradient(1200px 300px at 0% 0%, rgba(139,92,246,.35), transparent 60%),
              radial-gradient(900px 300px at 100% 100%, rgba(56,189,248,.28), transparent 60%), #121829;
  border: 1px solid rgba(255,255,255,.08);}
.hero h1 {margin: 0; font-size: 2.3rem; font-weight: 800; letter-spacing: -.5px;
  background: linear-gradient(90deg, #c4b5fd, #7dd3fc); -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;}
.hero p {margin: .35rem 0 0; color: #aab2c8; font-size: 1.02rem;}
.tiles {display: grid; grid-template-columns: repeat(4, 1fr); gap: .8rem; margin-bottom: 1.2rem;}
.tile {padding: .9rem 1.1rem; border-radius: 16px; background: #121829; border: 1px solid rgba(255,255,255,.07);}
.tile b {display: block; font-size: 1.6rem; color: #e9d5ff;}
.tile span {color: #8f98b3; font-size: .82rem; text-transform: uppercase; letter-spacing: .08em;}
.chat {display: flex; flex-direction: column; gap: .35rem; padding: .4rem 0 .8rem;}
.label {font-size: .72rem; color: #7f89a6; text-transform: uppercase; letter-spacing: .09em; margin: .5rem .4rem 0;}
.label.right {text-align: right;}
.bubble {max-width: 82%; padding: .85rem 1.1rem; font-size: 1.04rem; line-height: 1.6; word-wrap: break-word;}
.bubble.sent {align-self: flex-end; color: #fff; border-radius: 20px 20px 4px 20px;
  background: linear-gradient(135deg, #7c3aed, #2563eb); box-shadow: 0 8px 24px rgba(79,70,229,.35);}
.bubble.recv {align-self: flex-start; background: #1a2238; color: #e6e9f2;
  border: 1px solid rgba(255,255,255,.08); border-radius: 20px 20px 20px 4px;}
.bubble.sent mark {background: rgba(255,255,255,.22); color: #fff; padding: 0 .3rem; border-radius: 6px;}
.chip {background: rgba(139,92,246,.22); color: #ddd6fe; padding: 0 .35rem; border-radius: 7px;
  border-bottom: 2px solid #a78bfa; cursor: help;}
.pill {display: inline-block; margin: 0 .35rem .4rem 0; padding: .22rem .7rem; border-radius: 999px;
  background: rgba(139,92,246,.14); border: 1px solid rgba(167,139,250,.35); color: #ddd6fe; font-size: .82rem;}
.pill i {font-style: normal; color: #7dd3fc; margin-left: .35rem;}
.step {padding: 1rem 1.2rem; border-radius: 16px; background: #121829; border: 1px solid rgba(255,255,255,.07);
  margin-bottom: .7rem;}
.step b {color: #c4b5fd;}
div[data-baseweb="tab-list"] {gap: .4rem;}
button[data-baseweb="tab"] {border-radius: 12px 12px 0 0; padding: .55rem 1.1rem;}
.stButton > button {border-radius: 999px; border: 1px solid rgba(167,139,250,.4); background: #151c30;}
.stButton > button:hover {border-color: #a78bfa; color: #ddd6fe;}
textarea {border-radius: 14px !important; font-size: 1.02rem !important;}
@media (max-width: 760px) {.tiles {grid-template-columns: repeat(2, 1fr);} .bubble {max-width: 94%;}}
</style>
""", unsafe_allow_html=True)


def esc(text: str) -> str:
    return html.escape(text).replace("\n", "<br>")


def output_html(segs) -> str:
    parts = []
    for text, m in segs:
        if m:
            tip = html.escape(f"{m.original} · {m.category}")
            parts.append(f'<span class="chip" title="{tip}">{esc(text)}</span>')
        else:
            parts.append(esc(text))
    return "".join(parts)


def input_html(text: str, matches) -> str:
    out, pos = [], 0
    for m in matches:
        out.append(esc(text[pos:m.start]))
        out.append(f"<mark>{esc(text[m.start:m.end])}</mark>")
        pos = m.end
    out.append(esc(text[pos:]))
    return "".join(out)


def chat(left_label, left_html, right_label, right_html):
    st.markdown(
        f'<div class="chat"><div class="label right">{left_label}</div>'
        f'<div class="bubble sent">{left_html or "&nbsp;"}</div>'
        f'<div class="label">{right_label}</div>'
        f'<div class="bubble recv">{right_html or "&nbsp;"}</div></div>',
        unsafe_allow_html=True,
    )


with st.sidebar:
    st.markdown("### ⚙️ Settings")
    annotate = st.toggle("Show abbreviation + meaning", value=False,
                         help="BRB → BRB (Be Right Back)")
    include_words = st.toggle("Translate slang words", value=True,
                              help="fire, tea, slay, cap ... (real English words, uses a context rule)")
    chosen = st.multiselect("Categories", t.categories, default=t.categories,
                            help="Leave empty to use all categories")
    categories = set(chosen) or None
    st.divider()
    st.caption("💡 Hover over a highlighted word in the result to see the original slang and its category.")

st.markdown(
    '<div class="hero"><h1>💬 SMS Slang Translator</h1>'
    "<p>Decode chat abbreviations, internet slang and Gen&nbsp;Z phrases into plain English — and back.</p></div>",
    unsafe_allow_html=True,
)

if "src" not in st.session_state:
    st.session_state.src = EXAMPLES[0]


def use_example(text: str):
    st.session_state.src = text


tab_tr, tab_rev, tab_dict, tab_about = st.tabs(["🔤 Slang → English", "✍️ English → Slang", "📚 Dictionary", "🧠 How it works"])

with tab_tr:
    st.caption("Try an example")
    cols = st.columns(len(EXAMPLES))
    for c, ex in zip(cols, EXAMPLES):
        c.button(ex[:26] + "…", key=f"ex_{ex}", on_click=use_example, args=(ex,), use_container_width=True)

    text = st.text_area("Message", key="src", height=110, label_visibility="collapsed",
                        placeholder="Paste an SMS or chat message…")
    segs = t.segments(text, annotate, include_words, categories)
    matches = [m for _, m in segs if m]
    translated = "".join(s for s, _ in segs)

    st.markdown(
        f'<div class="tiles">'
        f'<div class="tile"><b>{stats["total"]}</b><span>Dictionary entries</span></div>'
        f'<div class="tile"><b>{len(t.categories)}</b><span>Categories</span></div>'
        f'<div class="tile"><b>{len(text.split())}</b><span>Words typed</span></div>'
        f'<div class="tile"><b>{len(matches)}</b><span>Slang detected</span></div></div>',
        unsafe_allow_html=True,
    )
    if text.strip():
        chat("You · SMS", input_html(text, matches), "Plain English", output_html(segs))
        if matches:
            pills = "".join(f'<span class="pill">{esc(m.original)}<i>{esc(m.category)}</i></span>' for m in matches)
            st.markdown(pills, unsafe_allow_html=True)
            with st.expander("Details"):
                st.dataframe(pd.DataFrame([{
                    "Slang": m.original, "Meaning": m.meaning.rstrip("!. "),
                    "Category": m.category, "Type": KIND_LABEL[m.kind]} for m in matches]), hide_index=True)
        else:
            st.info("No slang detected in this message.")
        with st.expander("Copy plain text"):
            st.code(translated, language=None)

with tab_rev:
    st.caption("Phrases of two or more words are shortened to their abbreviation (talk to you later → TTYL).")
    src2 = st.text_area("Plain English", "talk to you later, let me know what you think. thank you so much!",
                        height=110, key="src2", label_visibility="collapsed")
    res2 = t.to_slang(src2, categories)
    chat("Plain English", esc(src2), "SMS style", esc(res2))
    with st.expander("Copy SMS text"):
        st.code(res2, language=None)

with tab_dict:
    pills = "".join(f'<span class="pill">{esc(c)}<i>{n}</i></span>'
                    for c, n in sorted(stats["by_category"].items(), key=lambda x: -x[1]))
    st.markdown(pills, unsafe_allow_html=True)
    c1, c2, c3 = st.columns([2, 1.4, 1.4])
    q = c1.text_input("Search", placeholder="e.g. brb, gossip, laughing…")
    cat = c2.selectbox("Category", ["All"] + t.categories)
    kind = c3.selectbox("Type", ["All"] + sorted(KIND_LABEL.values()))
    df = pd.DataFrame([{"Slang": e.key.lower() if e.kind in ("word", "phrase", "informal", "letter") else e.key,
                        "Meaning": e.meaning.rstrip("!. "), "Category": e.category, "Type": KIND_LABEL[e.kind]}
                       for e in t.entries.values()])
    if q:
        ql = q.lower()
        df = df[df["Slang"].str.lower().str.contains(ql, regex=False) | df["Meaning"].str.lower().str.contains(ql, regex=False)]
    if cat != "All":
        df = df[df["Category"] == cat]
    if kind != "All":
        df = df[df["Type"] == kind]
    st.caption(f"{len(df)} result(s)")
    st.dataframe(df, hide_index=True, height=440)
    st.download_button("⬇️ Download as CSV", df.to_csv(index=False).encode("utf-8"),
                       "slang_dictionary.csv", "text/csv")

with tab_about:
    steps = [
        ("1 · Tokenization", "Regex splits text into words, spaces and punctuation. CUL8R, B4N and y'all stay as single tokens."),
        ("2 · Normalization", "Case-insensitive lookup and elongation fix: <code>lolll → LOL</code>, <code>zzzz → ZZZ</code>."),
        ("3 · Phrase matching", "Longest-match search finds multi-word slang first (<code>no cap</code>, <code>touch grass</code>)."),
        ("4 · Ambiguity rules", "L, W, PM, RAM only count in UPPERCASE; <code>bc</code>, <code>gl</code> only in lowercase; "
                                "slang words like <i>fire</i> are skipped after a determiner (<i>the fire</i>)."),
        ("5 · Detokenization", "Punctuation is preserved, sentence starts are capitalised and <code>I</code> is fixed."),
        ("6 · Reverse translation", "Plain-English phrases map back to their shortest abbreviation."),
    ]
    for title, body in steps:
        st.markdown(f'<div class="step"><b>{title}</b><br>{body}</div>', unsafe_allow_html=True)
    st.caption("Rule-based NLP: unknown slang is not detected. Extend data/slang_dict.csv to teach it new words.")
