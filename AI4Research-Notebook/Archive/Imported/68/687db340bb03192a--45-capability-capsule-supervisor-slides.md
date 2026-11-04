# 45 — Capability Capsule: the supervisor's slides, transcribed (English, Chinese kept referenceable)

**Source:** two slide photographs in this folder, `../20260918_144422.jpg` and `../20260918_144444.jpg`,
received from the supervisor on 2026-09-18. **Read in source** — every line below was read off the images
directly, not taken from a secondary description. Two phrases were re-read at 3× crop to settle them (§0.1).

> **What these slides are.** Prior thinking, not a specification. The supervisor's own words, the same day:
> *"those two picture only shows the thoughts as of before, and don't restrict your thoughts for your new
> design."* **What binds is in [46-supervisor-answers-chat-20260918.md](46-supervisor-answers-chat-20260918.md)** —
> read that first. This note is the exact record of what the slides say, kept for two reasons: it is where the
> team's vocabulary comes from, and it is a good source of arguments to agree or disagree with.
>
> An earlier version of this note treated the slides as authoritative and drew consequences for our design from
> them. Those sections are cut. The transcription is unaffected.

> **Translation record.** Tier T2 — a full digest, and our own slides may quote it.
> `tcheck all` against a verbatim Chinese transcription of both slides: **0 hard failures, 70 warnings**,
> all explained — the span warnings are this document's own added code spans and quoted Chinese, and every
> banned-rendering warning is the term index in §7 *naming* a banned rendering in order to ban it.
> `glossary-slice` (zh-en) applied: its terms are honoured throughout, and the four places where the glossary
> and the source pull against each other are marked `[TN]` or `[AMBIGUOUS]` at the point of use. Ten new terms
> appended to `translate/glossary.tsv` as `status=pending` (kit tests pass). **Critic: not run** — the T2
> pipeline's fresh-context critic pass is outstanding, because the working rules then forbade subagents
> without asking. **Verdict: pending critic.** Treat the English as careful but unreviewed, and re-check any
> line before it goes on a slide of ours.

---

## 0. The two slides

| Handle | File | Title | What it is |
|---|---|---|---|
| **Slide ARCH** | `20260918_144444.jpg` | Agent能力胶囊（Agent Capability Capsule） | the framework: formal layer, honeycomb network, the capsule itself, runtime, governance, sources, legend |
| **Slide A4R** | `20260918_144422.jpg` | 能力胶囊：AI4Research 的可组合能力单元 | the argument, in three numbered sections: Skill → Capsule, the three attribute classes, the self-evolution loop |

Both are photographs of a monitor, in focus, fully legible at full resolution.

### 0.1 The three contested phrases, resolved

Three AI readings of these images were supplied with them and disagreed on three phrases (§9). All three are
settled here against the images themselves.

| Where | The dispute | Settled, from the image |
|---|---|---|
| A4R §01, *Context*, final clause | reading A: `避免能力现实`, flagged by A itself as broken. Reading C: `避免能力孤岛` ("capability islands") | **The slide reads `避免能力现实`.** Verified at 3× crop. Reading A transcribed correctly; **reading C's `孤岛` is not on the slide** — a fluent repair of a defective source, invented. See §3 for what the clause can mean |
| A4R §01, closing line | reading A: `可问责` (accountable). Reading C: `可信` (trustworthy) | **`可复用、可上线、可问责的能力单元`.** Verified at 3× crop. **Accountable.** Reading A correct |
| A4R §02, *Verifiable* | reading A: `前置/后置条件`. Reading C: `前置条件` only | **The slide reads `前后置条件`** — pre- *and* post-conditions. Reading A correct in substance |

### 0.2 Two defects in the slide itself

Neither changes the meaning; both should be mentioned if we ever quote the slide as an image.

1. **A4R §01 heading**, `相对 Skills：从"会做"升级为"可上线"`, has an overlapping text box: `上线"` is drawn
   a second time on the line beneath.
2. **A4R §03 Execute box** reads `在 Action Contract Contract 内行动` — `Contract` is duplicated across the
   line break.

A third item is arguably a defect rather than a typo: `避免能力现实` (§3).

---

## 1. The definition

> **Agent能力胶囊（Agent Capability Capsule）**
> 面向AI Agent的可组合知识与能力封装框架
> "A composable knowledge-and-capability encapsulation framework for AI agents."
> — translated from Slide ARCH, subtitle

> 将 Skill 与规则、边界、数据、接口、验证与治理共同封装，形成可安全调用的能力单元
> "Encapsulate a Skill together with rules, boundaries, data, interfaces, verification and governance,
> forming a capability unit that can be invoked safely."
> — translated from Slide A4R, subtitle

**The formula, printed at the bottom right of Slide ARCH:**

> **Capsule = Skill + Rules + Boundary + Assets + Data + Interfaces + Eval + Governance**

**The four adjectives**, printed under the capsule on Slide ARCH:

> 自包含、可组合、可验证、可治理 — **self-contained, composable, verifiable, governable.**

> **One discrepancy between the slides.** The capsule drawn inside Slide A4R §01 carries a six-term formula —
> `Skill + Rules + Boundary + Data + Eval + Governance` — dropping **Assets** and **Interfaces**. The
> eight-term version is canonical: it is on the definitional slide, it is the stack drawn in A4R §02, and the
> A4R subtitle itself names 接口 (interfaces). Read the six-term version as an abbreviation for space.

---

## 2. The eight components

The English names are the slide's own — both slides label every component bilingually, so nothing here is
a translation choice.

| # | English | 中文 | What it holds |
|---|---|---|---|
| 1 | **Rules** | 规则 | the policy and logic constraints the capability runs under |
| 2 | **Boundary** | 边界 | permissions, scope, approvals, the Action Contract — the limits of what it may touch |
| 3 | **Skills** | 能力 | the executable body: prompt, code, or tool call |
| 4 | **Assets** | 资产 | the assets the capability depends on |
| 5 | **Data** | 数据 | the data it depends on |
| 6 | **Interfaces** | 接口 | the declared input/output surface others bind to |
| 7 | **Eval** | 评估 | the evaluation carried with the capability |
| 8 | **Governance** | 治理 | governance: logging, authorisation, lifecycle, version |

Order is the slide's own, top to bottom. **Rules is first and Governance last on both slides.**

> **[TN] 能力 is rendered "Skills" here** because that is the slide's own English label on that row, even
> though 能力胶囊 as a whole is **Capability** Capsule and 可行动空间 etc. read 能力 as capability. Both
> slides use 能力 in both senses; the slide's own pairing is kept rather than regularised.

**The slides gloss none of the eight.** The "what it holds" column above is the narrowest reading the labels
support. Every richer gloss offered by the three AI readings — *Assets* as "prompts, templates, static domain
knowledge", *Eval* as "unit tests, rubric metrics and evaluation harnesses" — is **not on the slide** and is
quarantined in §9.

---

## 3. Slide A4R §01 — from "can do" to "can go live"

> **01 相对 Skills：从"会做"升级为"可上线"**
> "01 Against Skills: an upgrade from 'can do it' to 'can go live'."

> **[TN]** 上线 is rendered **"go live"** per `translate/glossary.tsv` (approved; `deploy` and `deployment`
> are banned renderings of it). "Deployable" and "production-ready", used by two of the three AI readings,
> are therefore not used here.

```
  SKILL                    ──▶   CAPABILITY CAPSULE
  提示词 / 代码 / 工具调用          Skill + Rules + Boundary + Data + Eval + Governance
  prompt / code / tool call       可交付单元  (deliverable unit)
```

A **Skill** is a 执行片段, an **execution fragment**: prompt, code, or tool call. A **Capability Capsule** is
a 可交付单元, a **deliverable unit** — the badge is printed inside the capsule.

Three principles carry the upgrade. Each is a labelled row on the slide:

**上下文 · Context**
> 胶囊携带业务语义、数据与资产依赖，避免能力现实。
> "The capsule carries business semantics and its data and asset dependencies, 避免能力现实."
> — translated from Slide A4R §01

> **[AMBIGUOUS: the source clause is defective.]** `避免能力现实` does not parse — literally "avoid
> capability reality". The sentence is missing a word, and the two natural repairs give different meanings:
> **(a)** `避免能力脱离现实` — keep capabilities from **drifting away from reality**, which follows from the
> first clause (a capsule that carries its own data and asset dependencies cannot go stale against the world);
> **(b)** `避免能力孤岛` — avoid **capability islands**, which also follows (a capsule that carries its
> dependencies is not stranded). **Do not pick one silently.** This is a question for the supervisor, and it
> is cheap to ask. Note that reading (b) is exactly the text one AI reading claimed to see and that is not
> there, so it should carry no extra weight for having been "read".

**边界 · Boundary**
> 权限、规则、审批和 Action Contract 被固化为机器可执行约束。
> "Permissions, rules, approvals and the Action Contract are frozen into machine-enforceable constraints."

The load-bearing word is 固化 — *frozen/solidified into*, not *documented as*.

**可信 · Trustworthy**
> 以证据、验证器、审计和版本为交付标准，而非"工具调用成功"。
> "Evidence, verifiers, audit and version are the delivery standard — not 'the tool call succeeded'."

And the section's conclusion, in the box at the bottom:

> Skill 是"执行片段"；能力胶囊是可复用、可上线、可问责的能力单元
> "A Skill is an 'execution fragment'; a Capability Capsule is a capability unit that is reusable, can go
> live, and is **accountable**."

**可问责 — accountable — is the strongest word on either slide**, and it is the one an AI reading softened to
"trustworthy". Accountability is a claim about who answers for a failure. Keep it.

---

## 4. Slide A4R §02 — the three classes of attribute

> **02 胶囊的三类属性** — "The three classes of capsule attribute."

The eight-component stack is drawn in the middle; three badges surround it, each with its own colour.

| Badge | 中文 | As printed | English |
|---|---|---|---|
| **G**, green | 可治理 | 策略 \| 权限 \| 审计 \| 版本 | **Governable** — policy, permission, audit, version |
| hexagon, blue | 可组合 | Typed I/O \| 依赖声明 \| Action Contract \| 可替换 | **Composable** — typed I/O, dependency declaration, Action Contract, replaceable |
| check, purple | 可验证 | 前后置条件 \| Verifier \| Evidence \| Benchmark | **Verifiable** — pre- and post-conditions, verifier, evidence, benchmark |

The architectural rule the section exists to state, printed across the bottom:

> 统一契约让编排器只需理解接口、约束与验收标准，无需理解胶囊内部实现。
> **"A unified contract lets the orchestrator understand only the interface, the constraints and the
> acceptance criteria, with no need to understand the capsule's internal implementation."**
> — translated from Slide A4R §02

That sentence is the most load-bearing on either slide. It is the opacity rule, and it is what makes a capsule
affordable at any size: a layer that never looks inside does not care how big the inside is.

> **[TN] 验收 is rendered "acceptance", never "admission".** The glossary marks `admission` a banned rendering
> of 验收 and reserves it for 准入; 验收 is sign-off by a real run. The distinction matters: **the word 准入
> appears nowhere on either slide** (§8).

---

## 5. Slide A4R §03 — the autonomous runtime substrate

> **03 为什么它支撑自主运行底座的自我演进**
> "03 Why it underpins the self-evolution of the autonomous runtime substrate."

> **[TN]** 自主运行底座 is rendered **autonomous runtime substrate**. 底座 is literally a base or pedestal;
> "foundation" and "operating base" are equally defensible. Pick one rendering for the team and keep it —
> this note uses *substrate* throughout.
>
> **[TN] Ground Truth is kept as printed.** The slides write it in English, so it is the source's own gloss,
> which outranks the glossary's pending row `research truth ← 研究真值` (banned_en: `ground truth`) under
> authority rule A1. That row is about translating 研究真值 *into* English and does not reach a term the
> source already prints in English. Do not "correct" Ground Truth to research truth anywhere it quotes these
> slides.
>
> **[TN]** 自我演进 is rendered **self-evolution**, although the glossary bans `self-evolution` as a rendering
> of bare 演进|可演进 (FM-4, strengthening). The ban is against *adding* "self-"; here the source writes 自我
> explicitly, in both the section heading and the bottom banner. Bare 演进 is rendered "evolution".

`自主运行底座` sits in a blue circle at the centre; four boxes cycle around it, and **the arrows between them
are labelled** — the labels are on the arrows, not inside the boxes:

```
   Ground Truth  ──读取现实──▶  Plan & Compose
   当前事实 / 制度边界            按状态选择与组合胶囊
        ▲                              │
     验证更新      ( 自主运行底座 )      组合胶囊
        │                              ▼
      Verify    ◀──受控行动──      Execute
   证据/验收/状态对账              在 Action Contract 内行动
```

| Node / arrow | 中文 | English |
|---|---|---|
| Ground Truth | 当前事实 / 制度边界 | current facts / institutional boundaries |
| → | 读取现实 | read reality |
| Plan & Compose | 按状态选择与组合胶囊 | select and compose capsules according to state |
| → | 组合胶囊 | **[AMBIGUOUS: compose capsules \| composite capsule]** — as an arrow label it can be the act or the thing produced. The glossary notes 组合胶囊 = *composite capsule* as a noun; the neighbouring box uses 组合 as a verb |
| Execute | 在 Action Contract 内行动 | act within the Action Contract |
| → | 受控行动 | controlled action |
| Verify | 证据 / 验收 / 状态对账 | evidence / acceptance / **state reconciliation** |
| → | 验证更新 | verified update |

**状态对账** is an accounting word: 对账 is reconciling two ledgers against each other. The step is not
"check the output" but "reconcile the state we believe against the state that is", and the arrow leaving it
is labelled 验证更新 — the update that goes back into Ground Truth is a *verified* one.

Three checkmarks state the mechanism:

1. 每次执行沉淀 状态差异、轨迹、证据与效果
   **"Every execution deposits state differences, trajectories, evidence and outcomes."**
   沉淀 is sedimentation — it settles out of the run, it is not written by an author.
2. 通过新增 / 替换 / 调优胶囊扩展 可行动空间
   **"The actionable space is expanded by adding, replacing and tuning capsules."**
3. 演进对象从"模型参数"转为 可审计能力库 + 已验证状态
   **"The object of evolution shifts from 'model parameters' to an auditable capability library plus
   verified state."**

The third is the thesis of the deck: learning is moved out of the weights and into two things that can be
audited — a library and a state history.

### The bottom banner

> **AI4Research 的自我演进 = Ground Truth 的可验证更新 + Capability Capsule 的版本化演化**
> **"AI4Research's self-evolution = verifiable updates to Ground Truth + versioned evolution of Capability
> Capsules."**

Three chevrons beneath it, then a badge on the right:

| | 中文 | English |
|---|---|---|
| 1 | 看见现实 — 现实由 Ground Truth 定义 | **See reality** — reality is defined by Ground Truth |
| 2 | 在边界内行动 — 行动由 Capsule 约束 | **Act within the boundary** — action is constrained by the Capsule |
| 3 | 用证据学习 — 演进由 Evidence / Verifier 驱动 | **Learn from evidence** — evolution is driven by Evidence / Verifier |
| badge | 最小可学习行动单元 | **the minimum learnable action unit** |

---

## 6. Slide ARCH — the framework

The capsule sits in the centre. Four blocks surround it, and the legend types every arrow.

### 6.1 图例 · Legend — four relations, not one

Printed across the bottom of the slide. It is worth reading before the diagram, because the slide is making
four distinct claims about how the blocks relate:

| Arrow | 中文 | English |
|---|---|---|
| solid, dark blue | 组成 | **Composition** |
| solid, light blue | 消费 | **Consumption** |
| solid, green | 治理 | **Governance** |
| dashed, blue | 数据流 | **Data Flow** |
| blue dot | 核心胶囊 | **Core Capsule** |

Read off the arrows as drawn: the **honeycomb composes into** the capsule, the **formal layer composes into**
it from above, the **runtime consumes** it, **governance acts on** it (the green arrow points *at* the capsule,
from the governance panel), and **sources flow data** into it, dashed, from below.

### 6.2 形式化表达层 · Formal Layer

> SysML v2 → TypeScript → JSON Schema → Knowledge Graph

Four boxes, three arrows, then one composition arrow down into the capsule. **The slide gives the names and
the order and nothing else** — no box is glossed. The order is itself the claim: system model, then types,
then payload schema, then semantics.

### 6.3 蜂巢式胶囊网络 · Honeycomb Capsule Network

> 模块化组合，灵活复用 — **"modular composition, flexible reuse."**

Five hexagons, each with its own icon and colour, each with an arrow into the capsule:

| 中文 | English |
|---|---|
| 研究胶囊 | Research Capsule |
| 合规胶囊 | Compliance Capsule |
| 数据胶囊 | Data Capsule |
| 报告胶囊 | Report Capsule |
| 工具胶囊 | Tool Capsule |

None is glossed. They are named kinds, not a taxonomy with rules attached.

### 6.4 运行与消费层 · Runtime & Consumption

> Agent Runtime → Skills → MCP Tools → Apps / Services

A chain, left to right, fed by one consumption arrow out of the capsule. No product or framework is named on
the slide. A further arrow drops from this panel into the governance panel below it.

### 6.5 治理与验证 · Governance & Verification

Six tiles, two rows of three, with one green governance arrow pointing back at the capsule:

| 中文 | English |
|---|---|
| 合规 | Compliance |
| 安全 | Safety |
| 验证 | Verification |
| 基准测试 | Benchmark |
| 审计 | Audit |
| 版本 | Versioning |

### 6.6 来源与证据 · Source & Evidence

Six icons in one row, with dashed data-flow arrows rising into the capsule:

> **Web · Research · Reports · Internal Docs · APIs · Evidence**

**Evidence is the sixth item in the row**, drawn with a scales icon — it is one of the sources, not the
product of the other five. (One AI reading had it as the output of the flow. It is not.)

---

## 7. Bilingual term index

The reference list for our own documents and slides. Rows marked **[G]** are fixed by
`translate/glossary.tsv` and must not be varied.

| 中文 | English | Note |
|---|---|---|
| 能力胶囊 / Agent 能力胶囊 | Capability Capsule / Agent Capability Capsule | **[G]** banned: capsule module, capsule pill |
| 规则 · 边界 · 能力 · 资产 | Rules · Boundary · Skills · Assets | the slide's own labels |
| 数据 · 接口 · 评估 · 治理 | Data · Interfaces · Eval · Governance | **[G]** 接口 = interface, never UI |
| 自包含 | self-contained | |
| 可组合 / 组合 | composable / composition | **[G]** |
| 可验证 / 验证 | verifiable / verification | **[G]** banned: validation |
| 可治理 | governable | |
| 可上线 | can go live | **[G]** banned: deploy, deployment |
| 可问责 | accountable | the §01 claim; do not soften |
| 可复用 | reusable | |
| 可交付单元 | deliverable unit | |
| 执行片段 | execution fragment | what a Skill is |
| 机器可执行约束 | machine-enforceable constraint | |
| 固化 | frozen into | not "documented as" |
| Action Contract | Action Contract | untranslated on the slide; keep it so |
| 依赖声明 | dependency declaration | **[G]** 声明 = declare/declaration |
| 可替换 | replaceable | |
| 前后置条件 | pre- and post-conditions | |
| 验证器 / Verifier | verifier | |
| 证据 / Evidence | evidence | **[G]** banned: proof |
| 验收 | acceptance | **[G]** banned: admission (= 准入) |
| 验收标准 | acceptance criteria | |
| 基准测试 | benchmark | |
| 审计 | audit | **[G]** |
| 权限 | permission | **[G]** banned: effects |
| 策略 | policy | |
| 版本 / 版本化演化 | version / versioned evolution | |
| 统一契约 | unified contract | |
| 编排器 | orchestrator | **[G]** banned: scheduler |
| 自主运行底座 | autonomous runtime substrate | pick one rendering, keep it |
| 当前事实 | current facts | |
| 制度边界 | institutional boundary | |
| 读取现实 | read reality | |
| 受控行动 | controlled action | |
| 状态对账 | state reconciliation | an accounting word: balancing two ledgers |
| 验证更新 | verified update | |
| 沉淀 | deposit | as sediment; not "write" |
| 状态差异 | state difference | |
| 轨迹 | trajectory | |
| 效果 | outcome | **[G]** banned: effects (the manifest field) |
| 可行动空间 | actionable space | |
| 可审计能力库 | auditable capability library | |
| 已验证状态 | verified state | |
| 演进 | evolution | **[G]** banned: self-evolution, under version control |
| 自我演进 | self-evolution | source writes 自我 explicitly; see §5 [TN] |
| 最小可学习行动单元 | minimum learnable action unit | |
| 蜂巢式胶囊网络 | honeycomb capsule network | |
| 模块化组合，灵活复用 | modular composition, flexible reuse | |
| 形式化表达层 | formal layer | the slide's own English is "Formal Layer" |
| 运行与消费层 | runtime and consumption layer | |
| 来源与证据 | source and evidence | |
| 研究 / 数据 / 合规 / 报告 / 工具胶囊 | Research / Data / Compliance / Report / Tool Capsule | |
| 组成 · 消费 · 治理 · 数据流 · 核心胶囊 | composition · consumption · governance · data flow · core capsule | the legend |

---

## 8. How to use this record

- **For vocabulary.** §7 is the reference list; use those renderings in our documents and slides so we and the
  supervisor are using one set of words. The glossary constraints marked **[G]** are binding regardless.
- **For arguments, not requirements.** Assets as a first-class component, the SysML v2 → TypeScript → JSON
  Schema → Knowledge Graph chain, Ground Truth as a named component of the loop, and the five capsule kinds are
  all things the slides have and our design does not. None of them is an obligation. Each is worth a sentence of
  agreement or disagreement at the workshop.
- **The best line on either slide**, and worth quoting verbatim: §4's rule that a unified contract lets the
  orchestrator understand only the interface, the constraints and the acceptance criteria, never the capsule's
  internals. §5's third checkmark — evolution moves from model parameters to an auditable capability library
  plus verified state — is the second best.
- **One thing the slides do not have.** They say 验收 (acceptance) and never 准入 (admission). Nothing on either
  slide says a capsule is admitted to a library, by whom, or against what threshold. That absence is where our
  piece sits.

## 9. A warning about the three AI readings

Three model readings of these images were supplied with them, and were used to cross-check this transcription.
**One of them invented text**: `避免能力孤岛` ("capability islands") for the defective clause in §3, which is
not on the slide and reads more fluently than what is. The same reading weakened `可问责` (accountable) to
`可信` (trustworthy) and dropped half of `前后置条件`. All three errors run the same way — toward the more
plausible sentence.

They also supplied confident glosses for boxes the slides do not gloss (Agent Runtime as "LangGraph, AutoGen",
Versioning as SemVer, Eval as "unit tests, rubric metrics", the formal-layer boxes, the five capsule kinds), and
two comparison tables of their own composition. None of that is the supervisor's. If we use any of it, it is
ours and ours to defend.
