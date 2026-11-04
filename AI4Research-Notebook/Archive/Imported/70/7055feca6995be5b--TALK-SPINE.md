# Short Talk — Minimal Spine

For a short slot (~8 minutes speaking, leaving room for Q&A, which is where the
supervising engineer will actually spend attention).

Source documents: `VARIANT-1-brief-overview.md` (the read),
`VARIANT-3-full-report.md` (backing material for questions).

---

## The seven beats

| # | Beat | Content | Time |
|---|---|---|---|
| 1 | **The one idea** | The freeze. *"The model interprets meaning; deterministic code freezes and executes a contract."* State it as the one sentence to remember. | 60s |
| 2 | **What it is for** | Local workstation tool. Two workloads: code delivery and research. Research must emit **structured evidence, not prose**. | 30s |
| 3 | **One request, end to end** | Narrate — do **not** read the table row by row. Pick four: intake → intent, **the freeze**, dispatch, delivery. Gesture at the rest. | 2.5 min |
| 4 | **Capsules, briefly** | *"A capsule is a typed function signature that also declares its side effects and who may call it."* Then the invariant quote — the best line in the material: **"admit what you do not know, and do not grade your own work."** | 60s |
| 5 | **Honest status** | 606 passed / 34 failed / 8 skipped. One demonstrated 15-node run, with a mid-run fix. Release-candidate. **Not yet unattended.** Say this plainly, and *here* — not at the end. | 90s |
| 6 | **Real vs aspirational** | One line: two design documents describe a marketplace, signing, and trust scores that **are not built**; "verification" here means schema checks, not formal proof. | 45s |
| 7 | **Close** | See below. | 45s |

**~7–8 minutes.** Everything else is backup.

---

## The closer

The deadlock story is the best material, but it is **too long to tell in full**
in a short slot, and it ends on a hedge (the pattern still exists elsewhere).

Use the **self-retraction** instead — shorter, lands harder, and ends on
something true and finished:

> "In September, a run executed all fourteen nodes, delivered all eight files,
> and the system recorded it as passed. Then someone read the files. The run's
> own manifest said its evidence gate had failed. **They retracted their own
> passing run** and changed the gate so it can never happen again.
>
> That is the whole design philosophy in one incident: the system refuses to
> treat an attempt as an outcome — even its own."

Keep the deadlock story in your pocket for Q&A.

---

## Backup only — surface if asked

1. **The capsule inventory and binding chain** — 80 capsules, 45 logical / 102
   physical operators, routing conditions. Detail for a question, not the line.
2. **The deadlock bug in full** (`VARIANT-3` §32) — including that the pattern
   persists on the legacy path.
3. **Challenges and the intrinsic/incidental split** (`VARIANT-3` §31) — the
   best answer to "what did you learn that generalises?"

---

## Cut from the spoken version

- §5 operator routing (logical → physical, candidate lists, conditions)
- Two of the three items in "Three things worth noticing" — keep only the
  self-retraction
- The nine-row stage table read aloud; narrate four stages instead

---

## Questions to expect, and where the answer lives

| Question | Where |
|---|---|
| "Is this just a workflow engine with LLMs bolted on?" | V3 §36 |
| "Does the freeze make it inflexible?" | V3 §36 — adaptation happens *before* the freeze, by design |
| "Has it actually worked end to end?" | V3 §33 — once, with a mid-run fix |
| "What is formally verified?" | **Nothing**, in the formal-methods sense. V3 §20 |
| "Trust classes — rank or exact match?" | **Concede it.** Unresolved, ledger item 9. Do not defend |
| "What does a run cost?" | Not measured. Say so |
| "Are declared effects actually enforced?" | Partly unknown — a genuine weakness. V3 §36 |
| "What is the weakest part?" | Discovery semantic-scope defect; unwired capability tokens; aspirational docs |

**The two strongest moves in Q&A:** concede the trust-class discrepancy
immediately rather than defending it, and answer "we did not measure that"
plainly where it is true. The supervising engineer is testing calibration, not
recall.
