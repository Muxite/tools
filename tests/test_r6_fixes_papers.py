"""Round 6 fixes: papers_summary real-paper rules (MANIFEST §19.7, on top of §15.8, §16.6, §17.4 and §17.8).

Page-1 texts are synthetic, modelled on the reviewers' real papers (ids in each docstring). The summary's first
line is `# <id> · <title>`, its third line starts with the authors (§15.8).
"""
from __future__ import annotations

import re

import helpers_r6f as h

ABSTRACT = ("Abstract\nWe study agents that write research reports and check their claims against the sources.\n"
            "Our method improves accuracy on three benchmarks.\n")


def summary(tmp_path, pid, page1):
    res = h.summarise(tmp_path, pid, page1)
    return h.title_of(res), h.authors_of(res)


def squash(s: str) -> str:
    return re.sub(r"\s+([:,])", r"\1", " ".join(s.split()))


# ------------------------------------------------------------------------------------ skipped before the title
def test_running_header_removed(tmp_path):
    """§19.7, modelled on 2411.14199: `Asai et al. (2024)` before the title is not part of it."""
    page1 = ("Asai et al. (2024)\nOPENSCHOLAR: SYNTHESIZING SCIENTIFIC\nLITERATURE WITH RETRIEVAL-AUGMENTED LMS\n"
             "Akari Asai1,5 Jacqueline He1∗ Rulin Shao1,5∗\n1University of Washington\n"
             "ABSTRACT\nWe introduce OPENSCHOLAR, a retrieval-augmented LM for scientific queries.\n")
    title, authors = summary(tmp_path, "2411.14199", page1)
    assert "et al" not in title and "2024" not in title
    assert title.lower().startswith("openscholar: synthesizing scientific literature with retrieval-augmented")
    assert authors.startswith("Akari Asai")


def test_date_line_skipped(tmp_path):
    """§19.7, modelled on 2506.11763: a date-only line (`June 16, 2025`) before the title is skipped."""
    page1 = ("arXiv:2506.11763v1  [cs.CL]  13 Jun 2025\nJune 16, 2025\n"
             "DeepResearch Bench: A Comprehensive Benchmark for\nDeep Research Agents\n"
             "Mingxuan Du1∗, Benfeng Xu1,2, Chiwei Zhu1\n1University of Science and Technology of China\n"
             + ABSTRACT)
    title, authors = summary(tmp_path, "2506.11763", page1)
    assert title == "DeepResearch Bench: A Comprehensive Benchmark for Deep Research Agents"
    assert authors.startswith("Mingxuan Du")


# ------------------------------------------------------------------------------------ title clean-up
def test_spaced_hyphen_break_rejoined(tmp_path):
    """§19.7, modelled on 2604.03173: `Com- mercial` is rejoined."""
    page1 = ("Preprint. Under review.\nDetecting and Correcting Reference Hallucinations in Com-\n"
             "mercial LLMs and Deep Research Agents\nDelip Rao∗\nUniversity of Pennsylvania\n"
             "delip@seas.upenn.edu\n" + ABSTRACT)
    title, _ = summary(tmp_path, "2604.03173", page1)
    assert title == "Detecting and Correcting Reference Hallucinations in Commercial LLMs and Deep Research Agents"


def test_trailing_full_and_star_removed(tmp_path):
    """§19.7, modelled on 2601.08815: a trailing `(Full)⋆` is removed."""
    page1 = ("Agent Contracts: A Formal Framework for\nResource-Bounded Autonomous AI Systems\n(Full)⋆\n"
             "Qing Ye1 and Jing Tan2\n1 Independent Researcher yeqi519@gmail.com\n" + ABSTRACT)
    title, authors = summary(tmp_path, "2601.08815", page1)
    assert title == "Agent Contracts: A Formal Framework for Resource-Bounded Autonomous AI Systems"
    assert authors.startswith("Qing Ye")


# ------------------------------------------------------------------------------------ small caps
def test_small_caps_with_non_ascii_capital(tmp_path):
    """§19.7, modelled on 2505.22954: `G ÖDEL` joins (non-ASCII capital); `O PEN` joins (OPEN is common)."""
    page1 = ("Published as a conference paper at ICLR 2026\n"
             "DARWIN G ÖDEL M ACHINE : O PEN -E NDED E VOLUTION\nOF S ELF -I MPROVING AGENTS\n"
             "Jenny Zhang*,1,2 Shengran Hu*,1,2,3 Cong Lu1,2,3\n1 University of British Columbia\n"
             "A BSTRACT\nMost of today's AI systems are constrained by fixed architectures.\n")
    title, _ = summary(tmp_path, "2505.22954", page1)
    low = squash(title).lower()
    assert "darwin gödel machine:" in low
    assert "open-ended evolution of self-improving agents" in low
    assert not re.search(r"\b[A-ZÖ] [A-ZÖ]", title), title


def test_common_word_small_caps_join(tmp_path):
    """§19.7: `U SING`, `T HE` (2-letter run), `W EB` and `S HOW` join because the joined word is common."""
    page1 = ("U SING T HE W EB TO S HOW A GENTS WHAT W ORKS\n"
             "Ana Lopez1 Ben Okafor2\n1 Acme University\n" + ABSTRACT)
    title, _ = summary(tmp_path, "2609.00001", page1)
    assert title.lower() == "using the web to show agents what works"


# ------------------------------------------------------------------------------------ ALL-CAPS titles
def test_all_caps_title_takes_mixed_casing_from_later_text(tmp_path):
    """§19.7, modelled on 2308.00352: `METAGPT` becomes `MetaGPT` (its casing later); `META` is title-cased."""
    page1 = ("Published as a conference paper at ICLR 2024\nMETAGPT: META PROGRAMMING FOR A\n"
             "MULTI-AGENT COLLABORATIVE FRAMEWORK\nSirui Hong1∗, Mingchen Zhuge2∗, Jiaqi Chen1\n"
             "1DeepWisdom, 2AI Initiative\nABSTRACT\nWe introduce MetaGPT, which encodes SOPs into prompts. "
             "MetaGPT uses an assembly line.\n")
    title, _ = summary(tmp_path, "2308.00352", page1)
    assert title == "MetaGPT: Meta Programming for a Multi-Agent Collaborative Framework"


def test_all_caps_one_word_lines_and_dspy_casing(tmp_path):
    """§19.7, modelled on 2310.03714: `DSPY:` / one-word lines join, and `DSPY` takes the later `DSPy`."""
    page1 = ("Preprint\nDSPY:\nCOMPILING\nDECLARATIVE\nLANGUAGE\nMODEL CALLS INTO SELF-IMPROVING PIPELINES\n"
             "Omar Khattab,1 Arnav Singhvi,2\n1Stanford University, 2UC Berkeley\n"
             "okhattab@cs.stanford.edu\nABSTRACT\nWe introduce DSPy, a programming model for LM pipelines. "
             "DSPy modules are parameterized.\n")
    title, _ = summary(tmp_path, "2310.03714", page1)
    assert title == "DSPy: Compiling Declarative Language Model Calls into Self-Improving Pipelines"


# ------------------------------------------------------------------------------------ author lines
def test_middle_dot_author_list_ends_title(tmp_path):
    """§19.7, modelled on 2606.19819: a `·`-separated name line is an author line."""
    page1 = ("Language Resources and Evaluation manuscript No.\n(will be inserted by the editor)\n"
             "CREDENCE: Claim Reduction for Decomposition &\nEnhanced Credibility\n"
             "Semantic Metrics and Convergence Analysis\nPhuong Huu Vu Tran · Thuan Duc Mai ·\nBach Xuan Le\n"
             "Received: April, 2026 / Accepted: —\n" + ABSTRACT)
    title, authors = summary(tmp_path, "2606.19819", page1)
    assert title.endswith("Enhanced Credibility Semantic Metrics and Convergence Analysis")
    assert "·" not in title and "Phuong" not in title
    assert authors.startswith("Phuong Huu Vu Tran")


def test_team_line_ends_title(tmp_path):
    """§19.7, modelled on 2608.27969: `openJiuwen Team` is an author line."""
    page1 = ("openJiuwen: Beyond Static Harnesses for\nLong-Horizon Coding Agents\nopenJiuwen Team\n"
             "Huawei Technologies Co., Ltd.\n§ Source Code: https://github.com/openJiuwen-ai/jiuwenswarm\n"
             + ABSTRACT)
    title, authors = summary(tmp_path, "2608.27969", page1)
    assert title == "openJiuwen: Beyond Static Harnesses for Long-Horizon Coding Agents"
    assert "Team" not in title and "openJiuwen Team" in authors


def test_authors_skip_email_line_before_name(tmp_path):
    """§19.7, modelled on 2602.21045: an email-only line ends the title; `authors` skips it for the name
    line that follows."""
    page1 = ("PaperTrail: A Claim-Evidence Interface for\nGrounding Provenance in LLM-based Scholarly Q&A\n"
             "mart5877@umn.edu\nAnna Martin-Boyle\nUniversity of Minnesota\nMinneapolis, Minnesota, USA\n"
             + ABSTRACT)
    title, authors = summary(tmp_path, "2602.21045", page1)
    assert title == "PaperTrail: A Claim-Evidence Interface for Grounding Provenance in LLM-based Scholarly Q&A"
    assert "@" not in authors and authors.startswith("Anna Martin-Boyle")


def test_authors_never_abstract(tmp_path):
    """§19.7, modelled on 2606.26924: a `Technologies` line ends the title; `June 2026` and `Abstract` are
    never the authors."""
    page1 = ("A Deterministic Control Plane for LLM Coding\nAgents\n"
             "Padmaraj Madatha \\ Happiest Minds Technologies (AIP Centre of Excellence)\nJune 2026\n" + ABSTRACT)
    title, authors = summary(tmp_path, "2606.26924", page1)
    assert title == "A Deterministic Control Plane for LLM Coding Agents"
    assert authors.strip() not in ("Abstract", "June 2026", "")
    assert authors.startswith("Padmaraj Madatha")
