# Chinese → English traps

Chinese words and constructions whose English rendering needs a *decision*. Each row gives the possible readings, how to choose, and the **default when you can't tell**. The default is always the *weaker* claim. Under-claiming is recoverable; over-claiming is what gets challenged.

No script checks modal force; the translator's verify pass and the critic apply §1 by hand.

---

## 1. Modal ladder

| Class | Chinese markers | English | Watch for |
|---|---|---|---|
| **requirement** | 必须、务必、须、一定要、强制 | must / is required to | 需要 is *not* automatically "must" (see below) |
| **prohibition** | 不得、禁止、严禁、不能、不可、不允许 | must not / is not allowed to | 不能 can also be incapability ("cannot"); decide from context |
| **recommendation** | 应、应当、应该、宜、建议、推荐、最好 | should / is recommended | **except in standards-style specs**, where 应 = shall (see below) |
| **discouragement** | 不应、不宜、不建议、避免、尽量不要 | should not / is not recommended | |
| **permission** | 可、可以、允许、能够（ability）| may / can | 可以 ≠ "will"; 可 before a verb is "can be X-ed", not "is X-ed" |
| **possibility** | 可能、或许、也许、有可能 | may / might / could | never "will" or "is likely" unless 很可能 |
| **prediction / intent** | 会、将、将会 | will; in design docs often "is intended to" / "is designed to" | FM-9: 将 in a roadmap is a plan, not a fact |
| **no-need** | 无需、不必、不需要、不用 | need not / does not have to | not "must not" |
| **best-effort** | 尽量、尽可能、力求 | where possible / as far as possible / aims to | never drop it; never "always" |
| **hedge** | 一般、通常、基本上、大多、原则上、默认 | typically / usually / in principle / by default | never "always"; 原则上 implies exceptions exist |

**Genre switch: standards-style specs.** Chinese standards and documents written in their style (GB/T 1.1 conventions: numbered requirement clauses, acceptance criteria, 「应…」 lists, or a doc that defines its keywords) use a fixed scale. 应 / 不应 = **shall / shall not** (requirement), 宜 / 不宜 = should / should not, 可 / 不必 = may / need not, 能 / 不能 = can / cannot. Rendering that 应 as "should" *weakens a requirement* (FM-2 in reverse). Decide the genre first. In ordinary prose (design discussion, logs, chat), 应 / 应该 = "should". If you can't tell and it matters, `[AMBIGUOUS: shall | should]`.

**需要**: this one really is ambiguous. "需要 X" can be a requirement ("X is required"), a need ("needs X"), or a precondition ("requires X to be present"). If you can't decide, use "requires" / "needs", which is weaker than "must", and don't write "must".

---

## 2. Tense, aspect, and status

| Marker | Tempting rendering | Usually means | Default |
|---|---|---|---|
| 了 | "has been done" (shipped) | completed *within the narrative* | past tense in narrative only; no status claim |
| 已、已经 | "is already implemented" | completed at the time of writing | "had been / was already", and tie it to the doc's date if known |
| 完成 | "is complete" | a step or process finishing, or a stated goal being met | keep it concrete: "the node completes" |
| 将、将会 | "will" (fact) | plan / design intent | "is to", "is intended to", "the design has X" |
| 正在 | "is doing" | in progress at time of writing | "was in progress (as of <date>)" |
| 实现 | "implements" | *realises / achieves* a goal as often as *code implements* | pick from context; in design docs, often "achieve" |
| 支持 | "supports" | see §4 | |

Design docs in AI4Research are often written in the present tense about unbuilt things. The Chinese present tense carries no status, so the English present tense mustn't add one (FM-9).

---

## 3. Scope, quantity, negation

| Chinese | Risk | Rule |
|---|---|---|
| bare noun (能力、节点) | arbitrary singular/plural; "all X" | pick by context; "one or more" if open and it matters |
| 所有、全部、一切 | fine | "all" |
| 部分、一些、某些 | upgraded to "the" / "all" | "some", "certain" |
| 各、每个 | "all" | "each" (distributive) |
| 都 | ignored | reinforces "all"; with a negation, read the scope carefully |
| 不都 vs 都不 | swapped | 不都 = "not all"; 都不 = "none" |
| 只、仅、只能 | dropped | keep "only". Its scope is the thing right after it: 只能靠测试覆盖 = "can only rely on test coverage" |
| 至少 / 最多 | swapped or dropped | "at least" / "at most"; keep them with the number |
| 以上 / 以下 | inclusive? | usually inclusive in technical text ("≥" / "≤"); mark `[AMBIGUOUS]` if a boundary matters |

---

## 4. Words with several technical readings

| Chinese | Possible readings | How to decide | Default |
|---|---|---|---|
| **安全 / 安全性 / 安全风险** | security (against attackers, access control) · safety (no harm from normal operation) | an attacker / resource access → security; failure or harm → safety; the source's own English gloss wins (`**S**afety - 安全性可验证`) | if the source doesn't settle it, `[AMBIGUOUS: security \| safety]`. Don't pick silently |
| **支持** | supports (implemented feature) · is compatible with · can be used with · is designed to allow | Is there evidence it's built? A test, a code path? | "supports" only for built features; otherwise "is designed to support" / "can be used with" |
| **兼容** | compatible with · backward-compatible · tolerated | which direction? what version? | "compatible with", with the stated scope; don't add "fully" |
| **可能** | possibility | always possibility | "may / might"; **never** a prediction |
| **默认** | configured default value · implicit behaviour when unset · the usual deployment choice | Is there a config key? | "by default" + name the key if known; otherwise `[AMBIGUOUS]` |
| **实时** | hard real-time · near-real-time · promptly / live | Is there a latency bound? | "live" / "near-real-time"; "real-time" only with a stated bound |
| **保证 / 确保** | guarantee (invariant) · ensure (best effort, a goal) | Is there a mechanism that enforces it? | "ensure" / "aims to ensure"; "guarantee" only for enforced invariants |
| **一致性** | consistency (a named model: strong / eventual / causal) · agreement between two artifacts · uniformity | distributed-systems context? | "consistency" plus the model only if the source names it; "agreement / matches" for artifacts |
| **同步 / 异步** | synchronous/asynchronous (execution) · synchronise (to sync data) | a verb or an adjective? | 同步 as a verb = "sync / synchronise" |
| **自动** | fully automatic · automated with a human trigger · by default | who triggers it? | "automatically", but don't add "without human involvement" |
| **发布 / 部署 / 上线** | release (artifact) / deploy (to an environment) / go live (user-visible) | three different things | keep them distinct; see the glossary |
| **回滚** | roll back (a deployment / a transaction) · revert (a commit) | what's being undone? | "roll back"; "revert" only for VCS |
| **调度 / 编排** | schedule (when / where to run) / orchestrate (coordinate many) | | keep them distinct |
| **任务 / 作业** | task / job | in AI4Research, 任务图 = task graph | glossary |
| **接口** | interface (abstract) · API (endpoint) · port | code-level or network? | "interface" unless it's clearly an HTTP/RPC endpoint |
| **服务** | service (a running process / a Cordis Service) · a service offering | | "service"; check the glossary in DSH contexts |
| **能力** | capability (a system concept) · ability (a general word) | in AI4Research, a technical term | "capability" when it's the system concept |
| **合同 / 契约** | contract (a software interface agreement) | in this repo, 冻结合同 = "freeze the contract" | "contract" (software); `[TN]` on first use if a reader might think "legal" |
| **冻结** | freeze (lock a contract/spec; lockfile-like) | | "freeze / frozen", never "suspend" or "block" |
| **验收** | acceptance (testing / criteria) | | "acceptance", never "approval" |
| **门禁** | gate (CI / quality gate) | | "gate", never "access control" |
| **闭环** | closed loop (a process that feeds back) | 闭合 is "closure" (sprint closure); keep the two apart | "closed loop"; never "closure" or "complete" |
| **可 + verb (可验证、可组合、可演进)** | -able adjectives | this is slogan register | "verifiable, composable, evolvable": flat, **no added mechanism** (FM-4) |

---

## 5. Logical connectives

| Chinese | Relation | English |
|---|---|---|
| 然后、再、之后、接着 | sequence | then, after that |
| 因为、由于 | cause | because, since |
| 因此、所以、从而、导致 | consequence | therefore, so, which causes |
| 以便、为了 | purpose | so that, in order to |
| 如果、若、当…时 | condition | if, when |
| 而、但、却、然而 | contrast | while, but, however |
| 并且、同时 | conjunction / simultaneity | and, at the same time (**not** "atomically") |
| juxtaposed clauses with no connective | unspecified | keep them juxtaposed, or use "and". **Don't** supply a cause (FM-7) |

---

## 6. Register

- Chinese design docs use four-character slogans and parallel lists (可验证、可组合、可演进). Translate them as slogans. Don't turn a slogan into a specification.
- 我们 in a design doc is the author team. Keep "we"; don't convert it to "the system".
- Rhetorical questions (为什么…？) often introduce the author's answer. Keep them as questions or turn them into a heading; don't turn them into claims.
