# Translation drift in a zh-en-zh-en-zh round trip

## 1. Summary

Two fixtures (~230 combined source lines, one architecture passage, one README), one model family, one night. Across four translation hops each, 16 meaning-level drifts were logged, none caught by the mechanical checks except one that collided by coincidence with an unrelated glossary rule. Terminology substitution (FM-1) was the largest class at 9 of 16. Only one case was a clean, unambiguous can/must-style modal escalation, and it appeared at the very last hop. Most drift (7 of 16 rows) entered at the very first Chinese re-rendering (hop 2) and then persisted unchanged through hop 4; none of the 16 rows self-corrected back to the zh0 meaning. Where an independent human-authored English README existed (fixture B), 3 of 5 spot-checked drifts were absent from that pairing, so they look like chain artifacts rather than pre-existing looseness, though one had a seed already in the source's own bilingual gloss. This is a small, single-family, single-night sample; treat the direction of the finding as more solid than its magnitude.

## 2. Method

Read `translate/prompts/critic.md`, `translate/failure-modes.md`, `translate/RULES.md` first, then all ten fixture files plus the eight `*-tcheck.txt` outputs and the official README. For each fixture, aligned zh0/en1/zh2/en3/zh4 heading-by-heading and list-item-by-list-item, comparing zh0-zh2, zh2-zh4, zh0-zh4, and en1-en3 line by line. Logged every difference that changes what a reader would act on or repeat (force, scope, actor, status, added or dropped mechanism, term substitution); skipped pure synonym, punctuation, and word-order variance. For fixture B, five drifted sentences were checked against `B-official-en.md`, the project's own independently authored English README, to see whether the drift already existed in that human pairing. Each `*-tcheck.txt` was read to separate what the mechanical span/glossary checks flagged from what only a meaning-level read caught.

## 3. Drift table

| Fixture | Unit (zh0 line) | Hops compared | zh0 (short) | Drifted to (short) | Class | Direction | Entered at |
|---|---|---|---|---|---|---|---|
| A | §3 Planning, capsule list (:63) | zh0→zh2→zh4 | "capability capsule" | "capsule" (dropped qualifier) | FM-5 omission | weaker/narrower | hop2, persists |
| A | §5 item 1, actor runtime (:88) | en1→en3 | "safety boundary" | "security boundary" | FM-1 term | changed | hop3 |
| A | §4/§5, component name (:97) | zh0→zh2→zh4 | "Execution Broker" | "执行代理" / "execution agent" | FM-1 term | changed | hop2, persists |
| A | §6 gate-consumability (:121) | zh0→zh2→zh4 | "被消费" (consumed) | "被采纳"/"accepted"/"admissible" | FM-1 term | changed | hop2, persists |
| A | §6 repair budget (:123) | zh2→zh4 | "不允许" (is not allowed) | "不得" (must not) | FM-2 modal | stronger | hop4 |
| A | §6 default-gate sentence (:122) | zh2→zh4 | (no universal quantifier) | added "都" (all of these) | FM-6 scope | stronger | hop4 |
| A | §2 artifact list (:59) | en1→en3 | "contract manifest" | "a contract list" | FM-1 term | changed (narrowed) | hop3, hidden at hop4 |
| A | §5 item 4 (:91-ish) | en1→en3 | "context packet" | "context package" | FM-1 term | changed (low sev.) | hop3, hidden at hop4 |
| A | §6 repair budget (:123) | en3→zh4 | "受限"/"bounded" (restricted) | "有界" (mathematically bounded) | FM-1 term | changed (register) | hop4 |
| A | §6 repair budget (:123) | zh2→en3→zh4 | "转为" (turns into) | "is converted to" / "被转换为" | FM-8 actor | changed | hop3, reinforced hop4 |
| B | Line 1 tagline (:9) | zh0→zh2→zh4 | "agent harness" | "智能体框架" / "agent framework" | FM-1 term | changed | hop2 (seed in zh0 gloss), persists |
| B | Architecture line (:11) | zh0→zh2→zh4 | "an architecture in which X" | "architecture is based on the X philosophy" | FM-4 embellish | stronger/added claim | hop2, persists |
| B | Preview warning (:17) | zh0→en1 | "破坏兼容性的变更" (compatibility-breaking changes) | "Breaking changes" | FM-5 omission | weaker/narrower | hop1, persists |
| B | Preview warning (:19) | zh0→zh2→zh4 | "安全说明" (safety notes) | "安全须知" (safety must-know) | FM-2 register | stronger | hop2 |
| B | Preview warning (:19) | zh2→en3 | "安全须知"/safety | "security notice" | FM-1 term | changed | hop3 |
| B | npm run section (:33) | zh0→zh2→zh4 | "Web UI" | "Web 界面" / "web interface" | FM-1 term | changed (genericized) | hop2, persists |

## 4. Five clearest examples

**1. Modal escalation, can/must (Fixture A §6, zh0 line 123).**
zh0: "…不允许无限自循环。" en1: "…unlimited self-looping is not allowed." zh2: "…不允许无限自循环。" en3: "…infinite self-looping is not allowed." zh4: "…不得无限自循环。"
"不允许" (is not permitted, describes a rule/state) survives three hops unchanged, then at the last hop becomes "不得" (shall not/must not), a more formal, imperative prohibition. The English never wavered ("is not allowed" in both en1 and en3); the escalation appeared only in the final Chinese rendering, invisible to anyone reading only the English hops.

**2. Terminology substitution, safety/security (Fixture A §5 item 1, zh0 line 88; corroborated in Fixture B, zh0 line 19).**
A: zh0 "safety boundary" (English term already in source). en1: "safety boundary." zh2: "安全边界." en3: "security boundary." zh4: "安全边界" (ambiguous, masks the drift). B: zh0 "安全说明." en1: "safety notes." zh2: "安全须知." en3: "security notice." zh4: "安全须知." In both fixtures, independently, the drift from safety to security entered at the same structural point: the second English rendering of a Chinese "安全" term. Chinese "安全" covers both senses, so the ambiguity is latent until an English hop must pick one, and it picked wrong twice.

**3. Terminology substitution, broker/agent (Fixture A §4/§5, zh0 line 97).**
zh0: "Execution Broker" (named component, English in source). en1: "the Execution Broker." zh2: "执行代理." en3: "the execution agent." zh4: "执行代理." A broker (a component that mediates and dispatches) is not an agent (an autonomous actor); the document already uses "actor" elsewhere for that other role. The substitution entered at hop2 and never wavered again.

**4. Omission, dropped qualifier (Fixture A §3, zh0 line 63).**
zh0: "…节点、依赖、logical operator、capability capsule、read/write scope…" en1: "…capability capsules…" zh2: "…胶囊…" en3: "…capsules…" zh4: "…胶囊…" "Capability" is dropped at the first Chinese hop and never returns; "capsule" alone is a broader, less specific term used elsewhere in the same document for a different granularity of object.

**5. Embellishment, description upgraded to philosophy (Fixture B, zh0 line 11; confirmed against `B-official-en.md`).**
zh0: "它构建于**一切皆插件**的架构之上…" en1: "It is built on an architecture in which **everything is a plugin**…" zh2: "其架构基于**一切皆插件**的理念…" en3: "Its architecture is based on the **everything is a plugin** philosophy…" zh4: "其架构基于 **万物皆插件** 理念…" The official English README (not part of the chain) says "built on an **everything-is-a-plugin** architecture," matching en1 exactly. The word "理念"/"philosophy," an added framing the source never makes, entered only at hop2 and was never removed.

## 5. Counts

By class: FM-1 terminology substitution 9, FM-2 modal/register 2, FM-5 omission 2, FM-6 scope/quantifier 1, FM-8 invented actor/tense 1, FM-4 embellishment 1. Total 16.

By hop of entry: hop1, 1; hop2, 7; hop3, 5; hop4, 3.

By fixture: A, 10; B, 6.

**Accumulation vs. self-correction.** Comparing zh0→zh2 (hop1+hop2 entries: 8 of 16) against zh0→zh4 (all 16), the drift count roughly doubles over the second half of the round trip. No row in this table reverted to the zh0 meaning at a later hop; every drift that entered was still present, in some form, at hop4. Drift accumulated; it did not self-correct.

## 6. Implication for an English-only-from-Chinese pipeline

In this sample, a reader who only ever sees the English hops (en1 and en3) and never the Chinese in between would still encounter drift, since several rows changed between en1 and en3 directly (contract manifest/list, context packet/package, safety/security twice, harness/framework, architecture/philosophy) without needing to see a Chinese intermediate to notice something moved. Most drift entered at the very first re-rendering back into Chinese and then was carried forward unchanged rather than washing out, so a pipeline that performs even one or two automated round trips before a human reads the final English is not obviously safer than one that translates once: the same 9-of-16 terminology substitutions and the single clean modal escalation found here would, on this evidence, still be present, and would look exactly as fluent and confident as the faithful two-thirds of the text around them.

## 7. Limits

Two fixtures, ~230 combined source lines, one architecture-heavy technical passage and one project README, translated and reviewed inside a single night by one family of translator/critic agents (this one included, so the critique itself is a single, non-independently-verified read, not a panel). No repeated trials, so nothing here speaks to variance across runs, only to what happened once. The official-English comparison (step 3) was available for fixture B only, and even there it covered content that partly overlaps by design (a project README rewritten for a different audience, e.g. the WeCom/Discord community section, which is a deliberate content difference, not translation drift, and was excluded from the comparison for that reason) rather than a strict phrase-for-phrase gold pairing. Severity judgments (what a reader would "act on") are this critic's own reading, not a survey of the target expert audience. `tcheck` is mechanical by design and was never expected to catch modal or embellishment drift; its one relevant catch here (the banned "界面" rendering) triggered through a coincidental collision with an unrelated glossary row (interface→接口), not because it understood "Web UI" as a distinct product term.
