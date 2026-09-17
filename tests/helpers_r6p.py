"""Shared helpers for the round-6 deck_pack tests (MANIFEST §18.2).

Not a conftest. Test modules import it as `import helpers_r6p as h`. Nothing here imports tundlekit at module
level, so collection succeeds before `deck_pack` exists. Decks are built with deck_build (§3.2) and edited with
python-pptx through helpers_r3.
"""
from __future__ import annotations

import importlib
import re
from pathlib import Path

import helpers_r3 as r3
from helpers_r3 import by_rule, check_shape, need_pptx, open_deck, run_cli, set_frame_text, tool_error, write  # noqa: F401

SAY = r3.SAY


def call(name: str, **args):
    """Import tundlekit.deck (owner of deck_pack, §18.6), then registry.call (§1)."""
    importlib.import_module("tundlekit.deck")
    clean = {k: (str(v) if isinstance(v, Path) else v) for k, v in args.items()}
    return importlib.import_module("tundlekit.registry").call(name, clean)


def pack(pptx_path, **kw):
    return call("deck_pack", pptx_path=str(pptx_path), **kw)


def check(pptx_path, pack_path, **kw):
    res = call("deck_pack", pptx_path=str(pptx_path), check=str(pack_path), **kw)
    check_shape(res)
    return res


# ------------------------------------------------------------------------------------ spec slides (§3.1)
def notes(time_, say=SAY, asked=None):
    n = {"time": time_, "say": say}
    if asked:
        n["asked"] = list(asked)
    return n


def title(t, time_="0:20", asked=None):
    return {"type": "title", "title": t, "subtitle": "Round six", "byline": "A. Speaker",
            "notes": notes(time_, "Hello and welcome.", asked)}


def divider(t, time_="0:10", asked=None):
    return {"type": "divider", "title": t, "subtitle": "Part", "notes": notes(time_, "", asked)}


def content(t, time_="0:30", insert=False, asked=None, say=SAY):
    s = {"type": "content", "eyebrow": "Research", "title": t,
         "body": {"kind": "bullets", "items": ["first point", "second point"]},
         "notes": notes(time_, say, asked)}
    if insert:
        s["insert"] = True
    return s


STD_TITLES = ["Capsules for research", "Kept tools fail held-out tests", "The evidence", "Gates decide admission",
              "Alita-G measures other tools", "Budgets cap every run", "Next steps and owners"]
STD_KEYS = ["1", "2", "3", "4", "4a", "4b", "5"]
STD_ASKED = ["Why cap tries: the builder learns the suite", "Which model: Haiku 4.5"]


# the exact generate-mode text of std_spec() built as std.pptx (§18.2.1)
STD_TEXT = f"""# Presenter pack: {STD_TITLES[0]}

Deck: `std.pptx` · 7 slides (5 core, 2 inserts) · core 2:15 · with inserts 2:55

## Crib

- slide 1: {STD_TITLES[0]}
- slide 2: {STD_TITLES[1]}
- slide 3: {STD_TITLES[2]}
- slide 4: {STD_TITLES[3]}
- slide 4a (insert): {STD_TITLES[4]}
- slide 4b (insert): {STD_TITLES[5]}
- slide 5: {STD_TITLES[6]}

## If asked

### slide 2: {STD_TITLES[1]}

- {STD_ASKED[0]}
- {STD_ASKED[1]}

### slide 4a: {STD_TITLES[4]}

- Is 96.8% comparable: no, different tools

## Timing

| Slide | Title | Time | Core cumulative |
|---|---|---|---|
| 1 | {STD_TITLES[0]} | 0:20 | 0:20 |
| 2 | {STD_TITLES[1]} | 0:30 | 0:50 |
| 3 | {STD_TITLES[2]} | 0:10 | 1:00 |
| 4 | {STD_TITLES[3]} | 0:40 | 1:40 |
| 4a | {STD_TITLES[4]} | 0:25 |  |
| 4b | {STD_TITLES[5]} | 0:15 |  |
| 5 | {STD_TITLES[6]} | 0:35 | 2:15 |
|  | **Core total** | 2:15 |  |
|  | **Inserts** | 0:40 |  |
"""


def std_spec():
    """Keys 1, 2, 3, 4, 4a, 4b, 5 (§3.2 numbering): core 2:15, inserts 0:40, total 2:55."""
    t = STD_TITLES
    return {"meta": {"id": "std"}, "slides": [
        title(t[0], "0:20"),
        content(t[1], "0:30", asked=STD_ASKED),
        divider(t[2], "0:10"),
        content(t[3], "0:40"),
        content(t[4], "0:25", insert=True, asked=["Is 96.8% comparable: no, different tools"]),
        content(t[5], "0:15", insert=True),
        content(t[6], "0:35"),
    ]}


def build(path, spec=None, **kw) -> Path:
    need_pptx()
    path = Path(path)
    call("deck_build", spec=spec or std_spec(), out=str(path), **kw)
    return path


# ------------------------------------------------------------------------------------ python-pptx edits
def _frames(slide):
    return r3._frames(slide)


def edit(src, dst, fn) -> Path:
    """Open src, call fn(prs), save to dst."""
    prs = open_deck(src)
    fn(prs)
    prs.save(str(dst))
    return Path(dst)


def set_text(src, dst, index, old, new) -> Path:
    """Set the frame whose text is `old` on the slide at 1-based `index` to `new`."""
    def fn(prs):
        for tf in _frames(prs.slides[index - 1]):
            if tf.text == old:
                set_frame_text(tf, new)
                return
        raise AssertionError(f"no frame {old!r} on slide {index}")
    return edit(src, dst, fn)


def set_notes(src, dst, index, text) -> Path:
    def fn(prs):
        prs.slides[index - 1].notes_slide.notes_text_frame.text = text
    return edit(src, dst, fn)


def hide(src, dst, index) -> Path:
    return edit(src, dst, lambda prs: prs.slides[index - 1]._element.set("show", "0"))


def drop(src, dst, index) -> Path:
    def fn(prs):
        lst = prs.slides._sldIdLst
        el = list(lst)[index - 1]
        prs.part.drop_rel(el.rId)
        lst.remove(el)
    return edit(src, dst, fn)


# ------------------------------------------------------------------------------------ packs and findings
def lines(text):
    return text.split("\n")


def hand_pack(crib, header="Against the deck.", heading="## 2. One crib line per slide", extra=""):
    """A pack in the shape of the real hand-written ones (§18.2.2). Crib lines are given verbatim."""
    body = "\n".join(crib)
    return (f"# Presenter pack: test talk\n\n{header}\n\n## 1. The talk in 3 lines\n\n1. one\n2. two\n3. three\n\n"
            f"{heading}\n\n{body}\n\n## 3. Hard questions and answers\n\n1. **Why?** Because.\n{extra}")


def line_of(text, needle) -> int:
    """1-based number of the first line containing needle."""
    for i, ln in enumerate(lines(text), 1):
        if needle in ln:
            return i
    raise AssertionError(f"{needle!r} not in pack")


def names_key(message: str, key: str) -> bool:
    """True when `key` appears in the message as a standalone slide key (not inside a number like 0.33)."""
    return re.search(r"(?<![\w.])" + re.escape(key) + r"(?![\w.])", message) is not None


def rules(res):
    return sorted(f["rule"] for f in res["findings"])
