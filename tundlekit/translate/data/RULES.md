# Translation rules

Binding rules for any agent (or human) translating software-engineering text between Chinese and English in this workspace. Rule levels follow RFC 2119: **MUST** / **MUST NOT** block the output; **SHOULD** needs a stated reason to deviate; **MAY** is discretionary.

Scope: text going *into our notes, reports, and slides*, and reading Chinese sources for understanding. For `foo.md ↔ foo.zh.md` pairs inside `deepseek-harness/`, that repo's `docs/i18n/translation-rules.md` and `docs/i18n/terminology.md` take precedence.

Failure-mode IDs (`FM-n`) refer to [failure-modes.md](failure-modes.md). When a rule seems not to fit (polysemy, a wrong source, product strings, summaries), read [exceptions-and-misuse.md](exceptions-and-misuse.md) §A before deviating. Deviate visibly, never silently.

---

## 1. Shared rules (both directions)

### Faithfulness

- **MUST** say exactly what the source says. Nothing added, nothing dropped: no extra guarantees, prerequisites, warnings, examples, or qualifiers, and no lost clauses. Fluency never justifies either. (FM-4, FM-5)
- **MUST** preserve the source's force: requirement, recommendation, permission, possibility, prediction, observation. See the modal ladders in [zh-en-traps.md](zh-en-traps.md#1-modal-ladder) and [en-zh-traps.md](en-zh-traps.md#1-modal-ladder). (FM-2)
- **MUST** preserve quantifier scope (all / some / one / none, singular vs plural where the source fixes it) and negation scope. (FM-6)
- **MUST NOT** turn a sequence into a cause, or a correlation into a guarantee. (FM-7)
- **MUST** preserve the source's *status*: design, plan, aspiration, or claim stays that way. "The design specifies X" never becomes "the system does X". (FM-9)
- **SHOULD** read as natural technical writing in the target language, not word-by-word gloss. Restructure sentences freely; keep every clause.

### Terminology

- **MUST** use [glossary.tsv](glossary.tsv) exactly where a row applies (`status=approved`). **MUST NOT** use any rendering in that row's `banned_*` columns.
- **MUST NOT** swap a technical term for a related-sounding one (FM-1). "Reentrant" is not "thread-safe"; "authorization" is not "authentication".
- **MUST NOT** invent a rendering inline for an unlisted term that has no established equivalent. Keep the source term with a short gloss, e.g. `自闭环 (self-contained closed loop)`, list it under *Pending terms* in your translator notes, and append a `status=pending` row to `glossary.tsv`.
- **SHOULD** keep one rendering per term for the whole document. If context forces a different rendering, say so in a `[TN: …]`.

### Protected spans (never translated, never reformatted)

These **MUST** survive byte-for-byte (FM-3). `tcheck spans` enforces this.

- fenced code blocks, including comments (see §1.1),
- inline code (anything in backticks),
- class / function / variable / package names, CLI commands and flags, environment variables,
- HTTP methods, status codes, headers, JSON / YAML keys, SQL,
- file paths, URLs, regexes, version strings, commit hashes,
- numbers and units, dates, counts, and log lines that must match real output (value-preserving format changes are allowed: 三 → 3, 2026年9月10日 → 2026-09-10, full-width １２ → 12, 130万 → 1.3 million; see exceptions A10),
- product and project names: Solar, OpenSolar, AI4Research, Cordis, DeepSeek, GitHub.

If an identifier appears *un-backticked* in source prose, keep it verbatim anyway, and **MAY** add backticks.

#### 1.1 Code blocks with foreign-language comments

Keep the block byte-identical. Directly beneath it, add:

```markdown
*Translated comments:*
- line 3 `# 能力版本` → capability version
- line 7 `# 失败时回滚` → roll back on failure
```

Don't edit the comments inside the block. The span checker compares blocks exactly, and a reader may need to match the block against the real file.

### Structure

- **MUST** preserve heading levels and order, list kinds and item counts, table rows and columns, and emphasis spans. Heading and cell *text* gets translated.
- **SHOULD** keep paragraph boundaries. You **MAY** split an overlong source paragraph by semantic unit.

### Ambiguity

- When the source is ambiguous and the ambiguity matters (who acts, what is required, what is guaranteed, what the scope is), **MUST NOT** resolve it by guessing. Either
  - translate so the ambiguity survives, or
  - pick the most literal reading and mark `[AMBIGUOUS: <the readings>]` right after the span.
- Use `[TN: …]` (translator's note) for context a target reader needs that the source assumes, e.g. `[TN: 合同 here is the repo's term for a frozen interface contract, not a legal document]`. A TN is clearly yours, never merged into the source's voice.

### Input integrity

- **MUST** run `tcheck encoding` on the source before translating. Mojibake (`ï»¿`, `çœŸå®ž`, `Ã…`) or U+FFFD means the text is damaged. **MUST NOT** translate damaged text as if it were meaningful (FM-10). Repair a copy first (`tcheck encoding SRC --repair OUT`, then re-check OUT), or report it.

### Process (write, then verify)

1. **Write**: take one semantic unit at a time and restate it as a native technical author would.
2. **Verify clause by clause** against the source: added? dropped? force changed? scope changed? term per the glossary? spans intact?
3. **Read the translation alone**, without the source, and fix phrasing that only looks wrong in isolation. Don't add content while doing this.
4. Run `tcheck all`. Fix every hard failure, and explain or fix every warning. Passing means no *mechanical* damage, not faithful (M1).

---

## 2. Chinese → English (primary direction)

Chinese technical writing often leaves the subject, tense, number, modality, and logical connectives unstated. English grammar forces you to pick them. **Every one of those picks is a place to add meaning by accident.**

- **MUST NOT** state a stronger guarantee, a causal relation, an actor, a tense, or a requirement than the source states.
- **Subject-less sentences**: if the actor is recoverable from the immediate context, use it. Otherwise use the passive or an impersonal construction, or add `[TN: actor unstated]`. **MUST NOT** invent "the system", "the user", or "the operator" (FM-8).
- **Tense and aspect**: 了 / 已 / 完成 mark a completed action *in the narrative*, not "this is shipped". 将 / 会 in a design doc usually means "is intended to", not a factual future. Check §2 of [zh-en-traps.md](zh-en-traps.md).
- **Plural**: Chinese nouns aren't marked for number. Choose singular or plural from the context; if it's genuinely open and it matters, use "one or more", or mark it.
- **Connectives**: 然后 / 再 / 之后 are sequential. Render them as causal ("so", "therefore", "because") **only** when the source uses a causal connective: 因为 / 由于 / 因此 / 所以 / 从而 / 导致 (zh-en-traps §5).
- **Hedges survive**: 一般 / 通常 / 基本 / 大多 / 原则上 are not dropped and are not strengthened to "always".
- **Rhetorical force**: a Chinese design doc's slogan ("可验证、可组合、可演进") is translated as a slogan, flat and without gloss. Don't expand it into promises ("verifiable *by construction*", "evolvable *under version control*").
- **Established English**: use the established English SWE term, not a calque. Chinese category nouns that are really English jargon (智能体 = agent, 算子 = operator, 门禁 = gate) get the English term. The glossary decides.

---

## 3. English → Chinese

- **MUST** keep the English modal force (see the ladder in [en-zh-traps.md](en-zh-traps.md)). The typical failures are may→必须, should→必须, typically→总是, can→保证.
- **SHOULD** write natural institutional technical Chinese (系统、门禁、评审人 as explicit actors instead of vague passives).
- Typography **MUST** follow `deepseek-harness/docs/i18n/translation-rules.md` §Typography: a half-width space between CJK and Latin/digits, full-width punctuation in Chinese prose, 顿号 for enumerations, 你 not 您.
- **SHOULD** keep the English term on first occurrence for jargon without a settled Chinese rendering: `背压（backpressure）`. After that, use the Chinese form only.
- Unlisted terms: use a rendering established by a major Chinese OSS or vendor documentation set (Kubernetes / MDN / Vue zh docs, Microsoft zh style guide), and name the precedent in your translator notes. With no precedent, keep the English and mark it pending.

---

## 4. Done means

A bilingual engineer reading only the translation gets the same facts, the same caveats, the same force, and the same status as a reader of the source, and nothing extra. All `tcheck` hard failures are fixed, every warning is explained, every `[AMBIGUOUS]` is either resolved by a human or left visible, and every pending term is recorded.
