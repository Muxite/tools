# Exceptions, misuse, and edge cases

The rules in [RULES.md](RULES.md) are written for the common case. This file covers three other kinds of situation:

- **A. Exceptions**: when a rule should give way, and how to record that it did.
- **B. Misuse**: ways to follow the letter of the rules and still produce a bad translation. The critic checks for these (M-IDs).
- **C. Checker limits**: what `tcheck` gets wrong, so nobody trusts it past what it can actually see.

The general principle for exceptions: **deviate visibly, never silently.** Every exception leaves a trace a reviewer can see: a `[TN]`, a translator note, or a pending glossary row.

---

## A. Exceptions

### A1. Which authority wins for a term

When sources disagree, use the higher one and flag the lower one:

1. **A code identifier or schema key** for the same concept (`trust_class`, `logical_operator`, `effects`).
2. **The source's own English gloss**, e.g. `**S**afety - 安全性可验证`, `权限规约 (Permission Contract)`.
3. **An approved glossary row.**
4. **The established industry term.**
5. **A pending gloss** (keep the Chinese, add an English gloss, add a pending row).

If 1 or 2 contradicts the glossary, follow 1 or 2 and say so in *Pending terms*, so a human can fix the row. Don't change the row yourself.

### A2. The glossary row doesn't fit this sense

Many rows are polysemous. 进程 can mean the course of events (历史进程), not an OS process. 判定 is also a verb ("determine"). In review logs 降级 means "downgraded to a warning". 冻结模式 is the `/freeze` skill. 需求 can mean "need". 发布 can mean "publish".

Use the correct rendering, and put `[TN: 进程 here means "course of events", not an OS process]` at the first occurrence. `tcheck glossary` accepts a `[TN]` that names the source term and reports the override, and the critic judges whether it's justified. **Never bend the translation to satisfy a row**, and never skip the TN.

### A3. The source is wrong or inconsistent

The source says 认证 where the context clearly means authorization, or a number conflicts with a table, or two sections contradict each other. **Translate what the source says**, and add `[TN: source says "authentication"; context suggests authorization]`. Don't silently fix the source: the reader needs to know the original is wrong. The only exception is a typo that doesn't change meaning (的 / 得 / 地, an obvious character slip), which you **may** fix silently.

### A4. Product strings, log lines, error messages

If Chinese text in prose is literal product output (an error message, a log line, a UI label), readers may grep for it. Keep the original in backticks and put the translation after it: `验收失败` ("acceptance failed"). Don't replace it.

### A5. Chinese identifiers

File names, keys, enum values, or branch names written in Chinese are identifiers. Keep them verbatim and backticked, with a gloss: `` `冻结模式` (freeze mode) ``.

### A6. Quotes where the code comments are the point

A YAML example whose Chinese comments carry the meaning keeps the byte-identical block plus a *Translated comments* list ([RULES.md §1.1](RULES.md#11-code-blocks-with-foreign-language-comments)). On a slide you **may** show a version with English comments, but only if it's labelled "comments translated; original at `path:line`". Never present it as the file.

### A7. Summaries are not translations

A digest may summarise, but a summary in quotation marks is a misquote. Label paraphrase "Summary of §X" and translation "Translated from `path:line`". Anything inside quotation marks or a blockquote attributed to the source must be a translation of *that* text, clause for clause. This doesn't apply to the source's *own* punctuation. Chinese scare quotes (所谓“闭环”) become English scare quotes or italics, and 《》 titles become italics or the work's official English title. Those aren't quotations of the source.

### A8. Source already contains English

"Capsule（胶囊）", "IntentIR", `Closure closed`: embedded English stays exactly as the author wrote it, casing included. Don't "improve" it, and don't translate the Chinese gloss back into a second English term.

### A9. The source is deliberately vague

Design docs hedge. Keep the hedge. If you know from code what the vague sentence actually does, that's *analysis*, not translation. Put it in the note body with an evidence marker (`[verified]`, `file:line`), outside the quote.

### A10. Chinese numerals and approximations

三个 → "three" or "3" (either is fine). Convert Chinese magnitude units exactly: 万 = 10⁴ (130万 → 1.3 million, *not* 130 thousand), 亿 = 10⁸ (1000 亿 → 100 billion). Where the exact figure matters, keep the original in a `[TN]`. Dates may go to ISO format (2026年9月10日 → 2026-09-10), and full-width digits (１２) become ASCII. Keep approximations: 十余 = "more than ten" (not "10"), 约 / ~ = "about", 数十 = "dozens". `tcheck spans` may warn "number added" when 三 becomes 3. Explain the warning; don't avoid digits just to silence it.

### A11. Line ranges that cut structure

If `path:START-END` cuts a table, list, or code fence in half, widen the range to include the whole structure. `tcheck spans` warns on unbalanced fences.

### A12. Tiny T1 quotes

A few words with no glossary hit and no protected spans still fall under the rules. If the quote carries a guarantee, a requirement, a number, or a status claim, run the critic on it anyway (T2-lite). Those are exactly the quotes that get challenged.

### A13. deepseek-harness doc pairs

For `foo.md ↔ foo.zh.md` inside `deepseek-harness/`, that repo's `docs/i18n/` rules, its terminology table, and its `dsh-translate-docs` workflow win outright. Don't apply this kit's glossary there.

### A14. Subagents aren't allowed

Some contexts forbid spawning subagents without explicit permission (`notes/HANDOFF.md` rule 5). The T2 pipeline's translator and critic subagents then need that permission. **Ask for it first.** If it's refused or can't be asked, do the critic pass yourself as a *separate, cold* step:

1. Finish the translation and put it aside.
2. Reread the **source** alone, and list its claims, one line per clause, with the force, scope, and status of each.
3. Only then read the translation, and tick each claim against it. Then list every English clause that has no source claim (FM-4).
4. Run the critic prompt's checklist (§ "Check, in this order") and record its output format.
5. Label the result `critic: self (no subagent)`, so a reader knows the review wasn't independent.

A self-critic is weaker than a fresh one (M11). It's a fallback, not an equivalent.

### A15. Link targets and heading anchors

Link targets stay verbatim, including Chinese heading anchors (`[定义](#胶囊定义)` → `[the definition](#胶囊定义)`). Translating the anchor breaks the link into the source document. Link *text* gets translated. `tcheck spans` treats link targets as protected.

### A16. Strings and values inside code blocks, and commit messages

§1.1's rule for comments covers *all* Chinese inside a block: YAML values, string literals, and log-format strings (`[Scanner] 发现 … 个活跃会话`). The block stays byte-identical, and the translations go in a list beneath it (call it *Translated strings:* when there are values as well as comments). For commit messages, keep conventional-commit prefixes (`fix(scope):`), trailers (`Co-Authored-By:`), refs, and hashes verbatim, and translate the subject and body.

---

## B. Misuse (for translators to avoid and critics to flag)

| ID | Misuse | Why it's wrong | Tell |
|---|---|---|---|
| M1 | Treating "tcheck OK" as "faithful" | the scripts can't see FM-2 or FM-4..9 | no critic pass on T2 text |
| M2 | Gaming the checker: copying Chinese into the target, backticking prose so it's "protected", adding a `[TN]` just to silence a banned-term failure, rephrasing to dodge a banned word while keeping the wrong meaning ("safe across threads" for 可重入) | passes the check and keeps the error | TNs that don't explain a real sense difference; oddly backticked prose |
| M3 | `[AMBIGUOUS]` inflation | pushes decisions onto the reader | markers where context decides; roughly more than 1 per 300 source words |
| M4 | `[TN]` editorialising ("[TN: this was never built]") | analysis dressed up as translation | a TN that evaluates instead of explaining a term or a sense |
| M5 | Over-literalism for the sake of fidelity | fidelity is about meaning, force, and status, not word order | calques, unidiomatic coinages ("self-closing") |
| M6 | Over-hedging: adding "may", "reportedly", "is intended to" where the source states shipped fact, or applying design framing to a doc about shipped behaviour | FM-2 and FM-9 in reverse | hedges with no source marker; genre misread |
| M7 | Glossary over-reach: applying a row in the wrong sense, filing a pending row for every word, flipping pending→approved, editing a row to fit your translation | corrupts the shared source of truth | glossary diffs that aren't append-only |
| M8 | Retyping the original from memory or from another note | notes/14 quoted 只能依赖测试覆盖; the source says 只能靠测试覆盖 | a quoted original with no `path:line`, or one that doesn't match the file |
| M9 | Paraphrase inside quotation marks | a misquote (A7) | a quote that's shorter or smoother than a clause-by-clause rendering |
| M10 | Protected-span over-reach: leaving Chinese prose untranslated because it's bold, in a table, or a UI label | only code and identifiers are protected | Chinese left in the prose with no gloss |
| M11 | The translator reviewing itself | it reads what it meant, not what it wrote | critic run in the translator's context |
| M12 | Tier-dodging: calling a slide quote "T0 reading" | anything that leaves your context is at least T1 | quotes in deliverables with no check record |
| M13 | Silent partial translation: dropping the rows, footnotes, or clauses you didn't understand | FM-5; the untranslated-text check can't see deletions | counts of rows, list items, or clauses differ from the source |

---

## C. Checker limits (so nobody over-trusts `tcheck`)

- **Encoding.** Mojibake inside backticks or code fences is ignored on purpose, because documents about encoding damage quote it that way. A genuinely damaged inline code span won't be flagged.
- **Chinese substring matching.** Chinese has no word boundaries, so a term can match across two words (回合 inside 返回合理). The longest term wins, which removes most of these, but not all. A spurious hit shows up as a warning. Override it with a `[TN]`, or add a longer row.
- **English inflection.** Only -s, -es, -d, -ed, and -ing are handled. List irregular forms as alternatives in the row (`freeze|frozen`).
- **Paths.** Only rooted paths (`/a`, `./a`, `~/a`) and relative paths ending in an extension are detected. `docs/i18n` in bare prose isn't. Backtick it.
- **Numbers.** Chinese numerals aren't parsed, so 三 → 3 produces a warning (A10). Missing numbers only *warn*, because list numbering and restructuring move them around legitimately.
- **Untranslated text** (zh→en only). The ratio weights one CJK character as about 2.5 Latin letters, and ignores inline code, `[TN]` / `[AMBIGUOUS]`, and short parenthesised glosses ("capsule (胶囊)"). Above 5% it warns, above 30% it fails. It can't see *deleted* text (M13).
- **Code blocks** are compared whole. A single changed space fails. That's intended.
- **Banned renderings** (any inflection) **fail only when no approved rendering of that row is present.** That's the "wrong term instead of the right one" case. When both appear, it's a warning, because the banned word may translate something else. Correct renderings are masked before the search ("side effects" can't trip a ban on "effects"), and a correct rendering found only inside a banned phrase ("trust" in "trust class") doesn't count.
- **Domains.** Rows apply only to the domains passed with `--domains` (default `general,ai4research`). For text unrelated to AI4Research, pass `--domains general`, so repo conventions (合同 for contract, 算子 for operator) don't apply.
- **Pending rows** are never enforced. When a longer pending term hides every occurrence of an approved term (信任等级 over 信任), the approved row is reported as *not enforced here*, never dropped silently. Only a human settles the pending row.
- **A `[TN]` override covers the whole document.** The critic checks every other occurrence of the overridden term.
- **Link targets** are protected, but a *new* link a translator adds only warns.
- **Scripts can't judge meaning.** Passing `tcheck` means *no mechanical damage*. Modal force, additions, omissions, scope, causality, actors, and status belong to the critic.
