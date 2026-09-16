# Failure modes

What goes wrong in SWE translation, ranked by how dangerous it is. The dangerous ones are the **fluent** ones: an error that reads naturally gets past a quick review, and then an expert catches it in front of an audience.

Each mode lists **who catches it**. Scripts (`tcheck`) are reliable for mechanical failures. Meaning-level failures need the critic pass ([prompts/critic.md](prompts/critic.md)) and, for high-stakes text, a bilingual human. No script can tell that a sentence gained a promise.

| ID | Mode | Caught by |
|---|---|---|
| FM-1 | Terminology substitution | `tcheck glossary` (listed terms) · critic (unlisted) |
| FM-2 | Modal / normative drift | translator's verify pass · critic |
| FM-3 | Identifier and code-boundary damage | `tcheck spans` |
| FM-4 | Embellishment / addition | critic only |
| FM-5 | Omission | critic · `tcheck spans` for dropped literals |
| FM-6 | Scope / quantifier drift | critic |
| FM-7 | Logical-relation drift | critic |
| FM-8 | Invented actor or tense | critic |
| FM-9 | Status drift (design → shipped) | critic · evidence markers |
| FM-10 | Garbled input translated as text | `tcheck encoding` |

---

## FM-1 Terminology substitution

The biggest risk is not grammar. It's a plausible term swap: a precise term replaced by a related one that means something different in engineering.

| Source means | Drifts to | Why it matters |
|---|---|---|
| intermediary | middleware | a role vs a software layer |
| reentrant | thread-safe | different guarantees; neither implies the other |
| release | deployment | a versioned artifact vs putting it into an environment |
| response time | latency | response time includes service time; latency is often only the wait/transit |
| thread | process | shared vs separate address space |
| asynchronous consistency (异步一致) | eventual consistency (最终一致性) | a loose description gets upgraded to a named consistency model with specific guarantees |
| authorization | authentication | *what you may do* vs *who you are* |

In Chinese the pairs are often one character apart (认证 / 授权, 进程 / 线程, 发布 / 部署). A general-domain rendering can pick the wrong one and still read smoothly.

**Local case study** (`notes/07-capability-capsules.md:24-25` vs `CAPSULE_ARCHITECTURE.md:29-30`). The same slide renders the SCARE letters **S**afety - 安全性可验证 as "boundaries are verifiable", and **C**ompleteness - 完备性可验证 as "*completion* is verifiable". Completeness (the spec covers every case) and completion (the task finishes) are different properties. And the source's own English label, Safety, was right there. When a Chinese source gives its own English gloss, that gloss fixes the term.

**Prevent:** load the glossary slice *before* translating (`tcheck glossary-slice SRC`). The terms you don't notice are the ones that drift. When a term isn't in the glossary, don't pick a near-synonym; mark it pending.

## FM-2 Modal and normative drift

A requirement gets stronger or weaker:

| Source | Correct force | Dangerous tendency |
|---|---|---|
| may / 可 / 可以 | permission or possibility | must / will |
| should / 应 / 应当 | recommendation in prose; **shall** (requirement) in standards-style specs (zh-en-traps §1) | must in prose; *should* in a spec (weakening) |
| must / 必须 / 须 | hard requirement | should |
| can / 能 | capability or possibility | guarantee |
| typically / 通常 / 一般 | common, not universal | always |
| at least once / 至少一次 | delivery guarantee (duplicates possible) | "retried until it succeeds" |
| will / 会 / 将 (in a design doc) | intended behaviour | shipped fact |

This matters most in API specs, distributed-systems semantics, security documents, runbooks, and acceptance criteria.

**Prevent:** map every modal through the ladders ([zh-en](zh-en-traps.md#1-modal-ladder), [en-zh](en-zh-traps.md#1-modal-ladder)). No script does this: counting modal words gives too many false alarms in Chinese (能 in 能力, 应 in 应用, 会 in 会话). In the verify pass, list every source modal next to its rendering.

## FM-3 Identifier and code-boundary damage

Things that must stay byte-for-byte get translated, "normalised", re-cased, or re-spaced: identifiers, CLI flags, env vars, HTTP methods, status codes, headers, JSON keys, SQL, paths, URLs, regexes, versions, hashes, code blocks, inline code, and log lines that must match production output. The most common Chinese-source case is **Chinese comments inside YAML/JSON examples**, which get translated *in place*. See [RULES.md §1.1](RULES.md#11-code-blocks-with-foreign-language-comments) for the right handling.

**Prevent:** `tcheck spans SRC TGT` compares these as multisets and fails on any difference.

## FM-4 Embellishment / addition

The translation says *more* than the source. It's the most dangerous mode here, because it improves the prose: the addition sounds like what the author "obviously meant".

**Local case study** (`notes/07-capability-capsules.md`, caught in `notes/14-cross-panel-corrections.md` §A-4). An agent translated the critique table and the SCARE list from `AI4Research/docs/CAPSULE_ARCHITECTURE.md` for use as a verbatim "before" slide:

| Source (`CAPSULE_ARCHITECTURE.md`) | Literal | What was written | What went wrong |
|---|---|---|---|
| 只能靠测试覆盖 (:16) | "can only rely on test coverage" | "You can only test, never prove" | adds a claim about formal proof the source never makes |
| 出问题不知道找谁 (:14) | "when something goes wrong, you don't know who to ask" | "When it breaks, nobody owns it" | turns an *epistemic* complaint (owner unknown) into an *ownership* claim (no owner) |
| 可演进 (:33) | "can evolve" | "can evolve **under version control**" | adds a mechanism the source doesn't mention |

All three read better than the literal. All three would have been challenged by the supervising SWE.

A second lesson from the same case: the *correction* in note 14 quotes the Chinese as 只能依赖测试覆盖 and 不知道该找谁. Those are paraphrases, not the source text. When you quote the original, copy it from the file at the cited line. Never retype it from memory or from another note.

**Prevent:** in the verify pass, for every sentence ask *"is there any noun, qualifier, or clause here I can't point to in the source?"* The critic pass exists mainly for this.

## FM-5 Omission

A clause, hedge, condition, or list item disappears, usually a qualifier (一般, 部分, 在…情况下) or the second half of a compound sentence.

**Prevent:** verify clause by clause. `tcheck spans` catches dropped numbers and identifiers, and fails a zh→en target that is still mostly Chinese, but it can't see deleted prose (M13 in [exceptions-and-misuse.md](exceptions-and-misuse.md)).

## FM-6 Scope / quantifier drift

所有 (all) vs 部分 (some) vs 一些 (a few). A bare noun becomes "all X". Singular vs plural gets picked arbitrarily when the source leaves it open. Negation scope shifts: 不都 (not all) vs 都不 (none).

**Prevent:** check [zh-en-traps.md §3](zh-en-traps.md#3-scope-quantity-negation). If the number is genuinely open and it matters, write "one or more", or mark `[AMBIGUOUS]`.

## FM-7 Logical-relation drift

Chinese often puts clauses side by side without connectives. The translator supplies one, and it's often causal:

> 节点完成后，触发验收。 → ✅ "After the node completes, acceptance is triggered." ❌ "Because the node completed, it passes acceptance."

**Prevent:** use a causal connective only when the source has 因为 / 由于 / 因此 / 所以 / 导致 / 从而.

## FM-8 Invented actor or tense

English needs a subject and a tense. Chinese often gives neither. The translator invents "the system", "the user", or "the agent", or turns a design statement's implied "will" into a present-tense fact.

**Prevent:** recover the actor from the immediate context. Otherwise use the passive, or add `[TN: actor unstated]`. Take tense from explicit markers only ([zh-en-traps.md §2](zh-en-traps.md#2-tense-aspect-and-status)).

## FM-9 Status drift (design → shipped)

The source is a design doc, a roadmap, a plan, or a claim, and the translation reads like documentation of current behaviour. This is the source-level version of FM-2.

**Local case study:** `notes/11-capsule-architecture-digest-en.md` opens with a warning that `docs/CAPSULE_ARCHITECTURE.md` describes the *design* (`apiVersion: capsule/v1` with `interface / permissions / guarantees / …`), while the loaded format is `capability-capsule.v1.draft.json` with *different* sections. A faithful translation of the design doc in the present tense ("a capsule declares its guarantees") is still misleading in a report, unless it's framed as "the design specifies".

**A second, subtler case.** `AI4Research/harness/metadata/NEW-MACHINE-START-HERE.md:21` reads 目标设计是：LLM 解释语义，确定性代码校验结构…, i.e. "*The target design is*: LLMs interpret semantics; deterministic code validates structure…". Notes 00 and 09 present the sentence after the colon as "the core design thesis" and drop 目标 ("target"). The words are translated correctly; the status is lost. One dropped word turns "what we're aiming for" into "how it works".

**Prevent:** a translation never upgrades an evidence marker. Keep `[repo-claim]` / design framing on every quote. The critic checks every present-tense factual sentence against the source's genre.

## FM-10 Garbled input translated as text

Some Chinese docs in AI4Research are encoding-damaged: a UTF-8 → CP1252 round trip leaves text like `ï»¿# Phase 22 çœŸå®ž…` (`notes/04-gotchas.md` §8, `tests/journeys/phase22/journey-test-plan.md`). A model given that text may "translate" it confidently, or silently skip it.

**Prevent:** `tcheck encoding SRC` before any translation. It hard-fails on BOMs mid-file, U+FFFD, and CP1252-mojibake signatures. Repair the text with an explicit decode, or report it. Never guess.
