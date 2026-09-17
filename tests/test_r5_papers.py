"""MANIFEST §17.4 papers_summary (round 5): banner lines, 1-2-word title lines, author and name lines,
affiliations and URLs, small caps with a common-word list, ALL-CAPS titles to title case, cleaned authors.
Page-1 texts are synthetic, modelled on real papers in tundle/ai4research/papers (read-only).
"""
from __future__ import annotations

import re

import pytest

import helpers_r5b as h

LATER = "Abstract\nWe study agents. Large language model (LLM) agents call tools.\n"


# ------------------------------------------------------------------------------------ banners
def test_lre_manuscript_banner_skipped(tmp_path):
    """§17.4: `Language Resources and Evaluation manuscript No.` and `(will be inserted by the editor)` are
    skipped (modelled on 2606.19819 CREDENCE)."""
    p1 = ("Language Resources and Evaluation manuscript No.\n"
          "(will be inserted by the editor)\n"
          "CREDENCE: Claim Reduction for Decomposition &\n"
          "Enhanced Credibility\n\n"
          "Phuong Huu Vu Tran · Thuan Duc Mai ·\nBach Xuan Le\n"
          "Received: April, 2026 / Accepted: —\n" + LATER)
    res = h.summarise(tmp_path, "2606.19819", p1)
    title = h.title_of(res)
    assert title.startswith("CREDENCE: Claim Reduction for Decomposition"), title
    assert "manuscript" not in title and "editor" not in title
    assert h.slash(res["path"]).endswith("summaries/2606.19819 - CREDENCE.md")


def test_tmlr_published_in_skipped(tmp_path):
    """§17.4: `Published in Transactions on Machine Learning Research (01/2026)` is a banner
    (modelled on 2507.21046)."""
    p1 = ("Published in Transactions on Machine Learning Research (01/2026)\n\n\n"
          "A Survey of Self-Evolving Agents\n\n"
          "Huan-ang Gao1, Jiayi Geng2, Wenyue Hua3\n" + LATER)
    res = h.summarise(tmp_path, "2507.21046", p1)
    assert h.title_of(res) == "A Survey of Self-Evolving Agents"
    assert h.authors_of(res) == "Huan-ang Gao, Jiayi Geng, Wenyue Hua"


# ------------------------------------------------------------------------------------ title lines
def test_one_word_lines_joined_dspy(tmp_path):
    """§17.4: a run of 1-2-word lines is joined into the title (modelled on 2310.03714 DSPy); `Preprint` is
    skipped; the ALL-CAPS result is title-cased; `,1` marks leave the authors."""
    p1 = ("Preprint\nDSPY:\nCOMPILING\nDECLARATIVE\nLANGUAGE\n"
          "MODEL CALLS INTO SELF-IMPROVING PIPELINES\n"
          "Omar Khattab,1 Arnav Singhvi,2\n"
          "Paridhi Maheshwari,4 Zhiyuan Zhang,1\n"
          "1Stanford University, 2UC Berkeley\n"
          "okhattab@cs.stanford.edu\n"
          "ABSTRACT\nThe ML community is exploring prompting language models (LMs). We introduce DSPy.\n")
    res = h.summarise(tmp_path, "2310.03714", p1, short="DSPy")
    title = h.title_of(res)
    assert title.lower() == "dspy: compiling declarative language model calls into self-improving pipelines"
    assert "Compiling Declarative Language Model Calls" in title
    authors = h.authors_of(res)
    assert authors.startswith("Omar Khattab"), authors
    assert not re.search(r"\d", authors)
    assert not authors.rstrip().endswith(",")


def test_name_line_and_affiliation_stop_title(tmp_path):
    """§17.4: a 2-word name line stops the title; `Independent Researcher` and `github.com` are not part of it
    (modelled on 2604.13092 PlanCompiler)."""
    p1 = ("PlanCompiler: A Deterministic Compilation\n"
          "Architecture for Structured Multi-Step LLM Pipelines\n"
          "Pranav Harikumar\nIndependent Researcher\ngithub.com/prnvh/plancompiler\n" + LATER)
    res = h.summarise(tmp_path, "2604.13092", p1)
    assert h.title_of(res) == ("PlanCompiler: A Deterministic Compilation Architecture for Structured "
                               "Multi-Step LLM Pipelines")
    assert h.authors_of(res) == "Pranav Harikumar"


def test_one_line_author_and_affiliation_cut(tmp_path):
    """§17.4: a line with `github.com` stops the title; authors are cut at the first affiliation word."""
    p1 = ("Contract Checking of Tool Calls\nin Multi-Agent Pipelines\n"
          "Pranav Harikumar Independent Researcher github.com/prnvh/plancompiler\n" + LATER)
    res = h.summarise(tmp_path, "2604.13093", p1, short="Contracts")
    assert h.title_of(res) == "Contract Checking of Tool Calls in Multi-Agent Pipelines"
    assert h.authors_of(res) == "Pranav Harikumar"


def test_single_digit_mark_stops_title(tmp_path):
    """§17.4: 1 digit mark after a capitalised word (`Doe1`) makes an author line; the mark is stripped."""
    p1 = "Contract Checking of Tool Calls\nin Multi-Agent Pipelines\nJane Doe1\nAcme Lab\n" + LATER
    res = h.summarise(tmp_path, "2601.10001", p1, short="Contracts")
    assert h.title_of(res) == "Contract Checking of Tool Calls in Multi-Agent Pipelines"
    assert h.authors_of(res) == "Jane Doe"


def test_star_marks_stripped_from_authors(tmp_path):
    """§17.4: `∗1`, `∗1,3` and dangling commas are stripped (modelled on 2510.23601)."""
    p1 = ("Self-Evolving Agents via Tool Generation and Reuse\n"
          "Jiahao Qiu∗1 , Xuan Qi∗2 , Hongru Wang∗1,3 , Xinzhe Juan4,5\n"
          "1 Princeton University 2 Tsinghua University\n" + LATER)
    res = h.summarise(tmp_path, "2510.23602", p1, short="Evolving")
    authors = re.sub(r"\s+,", ",", h.authors_of(res))
    assert authors == "Jiahao Qiu, Xuan Qi, Hongru Wang, Xinzhe Juan"


# ------------------------------------------------------------------------------------ small caps
@pytest.mark.parametrize("raw,expected", [
    ("D EEP R ESEARCH: Agents That Read Papers", "DEEP RESEARCH: Agents That Read Papers"),
    ("A S YSTEMATIC Study of Agents That Read Papers", "A SYSTEMATIC Study of Agents That Read Papers"),
    ("A SURVEY of Agents That Read Papers", "A SURVEY of Agents That Read Papers"),
    ("I AM A MODEL: Agents That Read Papers", "I AM A MODEL: Agents That Read Papers"),
    ("Planning FOR A MULTI-AGENT Team of Readers", "Planning FOR A MULTI-AGENT Team of Readers"),
    ("Part B RL: Agents That Read Papers", "Part B RL: Agents That Read Papers"),
])
def test_small_caps_common_words(tmp_path, raw, expected):
    """§17.4: `X R` joins only when R (3+ capitals) is not a common word; for A/I/O, R needs 4+ letters."""
    p1 = f"{raw}\nAnn Lee, Bo Chen, Cy Diaz\n" + LATER
    res = h.summarise(tmp_path, "2601.20002", p1, short="Caps")
    assert h.title_of(res) == expected


def test_alita_g_small_caps_then_title_case(tmp_path):
    """§17.4: `A LITA -G: S ELF -E VOLVING G ENERATIVE AGENT FOR AGENT G ENERATION` rejoins to an ALL-CAPS title,
    which becomes title case keeping `ALITA-G` (used in the later text)."""
    p1 = ("A LITA -G: S ELF -E VOLVING G ENERATIVE AGENT FOR AGENT G ENERATION\n"
          "Jiahao Qiu∗1 , Xuan Qi∗2 , Hongru Wang∗1,3\n"
          "A BSTRACT\nWe present ALITA-G, a framework that turns a general agent into a domain expert.\n")
    res = h.summarise(tmp_path, "2510.23601", p1)
    title = h.title_of(res)
    assert title.lower() == "alita-g: self-evolving generative agent for agent generation"
    assert title.startswith("ALITA-G: Self-Evolving Generative Agent"), title
    assert title.endswith("Agent Generation")
    assert h.slash(res["path"]).endswith("summaries/2510.23601 - ALITA-G.md")


# ------------------------------------------------------------------------------------ ALL-CAPS titles
def test_all_caps_title_case_keeps_acronyms(tmp_path):
    """§17.4: a fully upper-case title becomes title case; `LLM` (in the later text) stays, `TOOL` does not."""
    p1 = "SAFE LLM AGENTS FOR TOOL USE IN PRODUCTION\nAnn Lee1, Bo Chen2\n" + LATER
    res = h.summarise(tmp_path, "2601.30003", p1, short="Safe")
    title = h.title_of(res)
    assert title.lower() == "safe llm agents for tool use in production"
    assert title.startswith("Safe LLM Agents") and "Tool" in title and title.endswith("Production")


def test_all_caps_two_lines_paperqa2(tmp_path):
    """§17.4: modelled on 2409.13740; one name per line with digit marks ends the title."""
    p1 = ("LANGUAGE AGENTS ACHIEVE SUPERHUMAN SYNTHESIS OF\nSCIENTIFIC KNOWLEDGE\n"
          "Michael D. Skarlinski1\nSam Cox1,2\nJon M. Laurent1\n"
          "1FutureHouse Inc., San Francisco, CA\n"
          "ABSTRACT\nLanguage models are known to hallucinate. PaperQA2 matches experts.\n")
    res = h.summarise(tmp_path, "2409.13740", p1, short="PaperQA2")
    assert h.title_of(res) == "Language Agents Achieve Superhuman Synthesis of Scientific Knowledge"
    assert h.authors_of(res) == "Michael D. Skarlinski"


def test_mixed_case_title_unchanged(tmp_path):
    """§17.4: a title that is not fully upper-case keeps its case."""
    p1 = "LEDGER: A Provenance Ledger for Auditing Agents\nAlice Smith1, Bob Jones2\n" + LATER
    res = h.summarise(tmp_path, "2601.40004", p1)
    assert h.title_of(res) == "LEDGER: A Provenance Ledger for Auditing Agents"
    assert h.authors_of(res) == "Alice Smith, Bob Jones"
