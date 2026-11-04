# 20-Minute Talk — Who Else Is Doing This, and What We Need (draft script)

Written 2026-09-11. Panel: capability capsules. Slot: 20 min total, ~3 min Q&A.

**This is a speaking script, not a document.** Read it aloud, not silently — the
register is deliberately spoken. If a line feels odd on the page, say it out
loud before changing it.

Order of movements is as directed by the user: goal → MCP (what it is *and what
it was*) → A2A → Alita-G → Beyond Task Completion → adversarial review → what we
need.

---

## Word budget — the arithmetic

| Quantity | Value | Reasoning |
|---|---|---|
| Slot | 20 min | 1,200 s |
| Q&A | −3 min | separate |
| **Presentation** | **17 min** | 1,020 s |
| Slide transitions | ~30 s | 9 figures + title, ~3 s each |
| Diagram parse silence | ~60 s | 6 figures the room must read, ~10 s each |
| Deliberate pauses | ~24 s | 6 claims worth landing, ~4 s each |
| Stumble / breath buffer | ~71 s | ~7% of slot |
| **Non-speaking total** | **~185 s** | **≈ 3.1 min** |
| **Actual speaking time** | **~13.9 min** | 1,020 − 185 |
| Delivery rate | 130 wpm | prepared technical talk with diagrams |
| **Word budget** | **~1,800 words** | 13.9 × 130 |
| Hard ceiling | 2,000 words | beyond this you overrun |

Cross-check against the one measured script this project has
(`report/TALK-15MIN-WORKFLOW-SCRIPT.md`): 1,435 words delivered in ~13.5 min is
an *effective* 106 wpm once silence is counted. 1,800 words at that effective
rate is ~17.0 min. Both methods agree.

⚠ The common "140 wpm × 20 min = 2,800 words" figure would overrun this slot by
about seven minutes. Do not use it.

### Calibrate against your own rate before trusting this

130 wpm is a planning figure, not yours. Time yourself reading §3 aloud at
presentation pace — it is 226 words.

```
your wpm = 226 / (seconds taken / 60)
```

- **Under 115 wpm** — cut ~200 words. Cut list at the bottom.
- **115–145 wpm** — the script fits as written.
- **Over 145 wpm** — you are rushing. Do not add words; add pauses.

Do not calibrate by reading silently. Silent reading runs 2–3× faster than
speech and will tell you the script is short when it is not.

---

## Audience note

Five people. One supervisor who knows the system deeply and will check numbers.
One peer onboarded the same week. Two onboarded the day before.

- **Assume** LLMs, tool calling, agents, DAGs, JSON Schema — everyone was hired
  to build agentic systems.
- **Do not assume** this codebase, these papers, or our internal vocabulary.
- This is why MCP and A2A get real time rather than a passing mention. For three
  of the five, that background is load-bearing.

---

# ACT I — WHAT IS MEASURED

## §0 — The goal *(180 words · 1.4 min)*

> **[FIGURE 1 — the self-extension loop]**
> A ring: *hits a gap → finds or writes a capability → checks it → installs it →
> keeps going*. Keep it abstract; no repo names. This shape is referenced five
> more times, so it must be legible in one look. **~8 s of silence.**

Here's what we're trying to build.

A system that runs on its own for days. It hits something it can't do. So it
finds a capability — writes one, or picks one up — and plugs that capability
into itself. Then it keeps going. Next time it needs that thing, it has it.

That loop isn't hypothetical. There's a paper called Alita-G that does exactly
this, and does it well. I'll get to it.

The difference is the word "days".

Alita-G specialises an agent for a fixed set of tasks. Harvest tools, keep the
successful runs, get better at that set. That works, because the set doesn't
move.

Ours moves. A week-long research run is non-stationary by design — a discovery
changes what the system should do next, and so does a failure.

[PAUSE]

So: specialisation is a bet that the task distribution won't move. Long-horizon
autonomy is the case where that bet is guaranteed to lose.

That's the talk. Everything else is me showing you what other people built, what
they measured, and what I think it means we need.

## §1 — MCP: what it is, and what it was *(256 words · 2.0 min)*

Before the research, two protocols. Most of you have been here four days, so I'm
not assuming these.

MCP, Model Context Protocol. Anthropic shipped it in November 2024. The problem
it solves is arithmetic. If you have N models and M data sources, you were
writing N times M custom integrations. MCP makes that N plus M. One protocol,
everyone speaks it.

It was donated to the Linux Foundation in December 2025. Anthropic, Block and
OpenAI co-founded the body that owns it now. It isn't one vendor's protocol any
more.

Now the part worth your attention, and the reason I said "what it was".

> **[FIGURE 2 — MCP, legacy vs modern]**
> Two panels side by side. Left: client → `initialize` → server, capabilities
> negotiated once, state living in the session. Right: no handshake; three
> independent requests, each carrying its own version and capabilities. Label
> them **≤ 2025-11-25** and **≥ 2026-07-28**. **~10 s of silence.**

MCP used to be stateful. You opened a connection, ran an initialize handshake,
negotiated what each side could do, and that negotiated state lived in the
session.

As of the July 2026 revision, that's gone. No handshake. MCP is stateless now —
every request carries its own protocol version and capabilities, and the server
accepts or rejects each request independently.

If you learned MCP before this year, you learned the old one. Most deployed
servers still speak it.

Why that matters to us. A standards committee looked at negotiated session state
and concluded that capability metadata belongs *with the request* — declared,
and re-checked every time. We reached the same conclusion from a completely
different direction. Hold that thought.

One more thing MCP says about itself. It is a transport and description
protocol. Safety is the host's job, not the protocol's. Its own spec says tool
descriptions should be treated as untrusted.

## §2 — A2A, short *(131 words · 1.0 min)*

A2A, quicker. Google, April 2025. Also Linux Foundation now.

MCP is how an agent calls a tool. A2A is how an agent talks to another agent.
The design assumption is the whole point: you delegate to a peer "without
needing access to each other's internal state, memory, or tools". The other
agent is opaque, deliberately.

> **[FIGURE 3 — the layers]**
> Three stacked bands with arrow direction encoded. **A2A** sideways, agent ⇄
> agent, marked *opaque*. **MCP** downward, agent → tool, marked *transparent*.
> Between them, **the capability contract** — agent → its own future
> capabilities, arrow pointing *inward and forward*. **~10 s of silence.**

And here's the honest version of where we are. Our A2A connection today is a
third-party skill that posts to a public relay — someone else's server, on
fly.dev — and picks peers by matching free-text tags. No declared effects. No
contract. No typing. No record of what the peer did.

So: MCP standardises access. A2A standardises delegation. Neither says anything
about where a capability comes from, or what must be true before you trust it.

## §3 — Alita-G, the closest thing to our goal *(226 words · 1.7 min)*

Now the research. Alita-G first, because it's closest to what we want.

> **[FIGURE 4 — Alita-G's loop, with the gate highlighted]**
> Reuse F1's ring so the parallel is visual. Overlay their three steps: harvest →
> abstract → retrieve by similarity. Then put one small box on the admission
> edge reading **"Eq. 5: did the task succeed?"** — and make it visibly the only
> gate on the diagram. That contrast is the slide's whole job. **~10 s.**

Three steps. Run the agent over a set of tasks. When a run succeeds, keep the
tools it built along the way. Clean them up with a language model — generalise
hard-coded values, strip task-specific references, standardise the interface,
improve the docs. Four transformations, one LLM call. Then at inference,
retrieve by embedding similarity.

The results are good. GAIA: 83 percent pass-at-one, up from 75. About 15 percent
fewer tokens, because a specialised tool beats reasoning it out each time. And
it compounds — 80 percent after one harvest, 83 after three.

So the loop works. I don't want to undersell that, because the rest of this is
going to sound like criticism and it isn't.

Here's the structural thing.

What decides whether a tool is kept? One signal. Equation 5: did the final
answer come out right.

That's it. So if a run produces five tools and the answer is correct, all five
are kept. Including the ones never called. Including the ones called and failed.
There's no per-tool measurement anywhere in the system. Not correctness, not
quality, nothing.

And their fix for tool quality is that LLM rewrite. Nothing checks the rewrite.

[PAUSE]

Which raises the obvious question. If you keep tools on that rule, what actually
ends up in your library?

Somebody measured that.

## §4 — Beyond Task Completion: the measurement *(230 words · 1.8 min)*

This paper. "Beyond Task Completion".

What they did is clean. Take a tool-evolving harness, patch it to preserve the
source of every tool it synthesises, run it. Then — this is the move — replay
each tool against a held-out test suite for the capability *that tool claimed to
implement*. Not the task it happened to solve. The capability it advertised.

> **[FIGURE 5 — the silent-rot bar]**
> Share of preserved tools scoring exactly zero, by protocol: One-Shot 100%
> (n=119), ToolMaker-style 100% (n=19), CREATOR-style 91.7% (n=84), total 96.8%
> (n=222). Annotate every n on its bar. Caption carries the honest caveat: *these
> are `-style` reimplementations, not the original systems.* **~10 s.**

222 tools. 215 scored zero.

Ninety-six point eight percent. Zero correctness on held-out inputs.

And I want to be precise about what zero means, because it isn't what you'd
guess. These tools don't crash. Their mean robustness is about 0.5. They run,
they return values — the values are just wrong for the capability they claim.
Syntactically fine. Silently wrong.

The paper calls this silent rot. And the sentence that matters is this one.

[PAUSE]

"The rot is silent because no in-session signal flags it: the verifier scores
task outputs, not tools."

Now put that next to Alita-G. "The verifier scores task outputs, not tools" —
that is Alita-G's Equation 5. The same rule.

So the rule the closest prior system curates on is the same *class* of rule that
was measured admitting broken artifacts at scale. I say class deliberately.
Alita-G's own tools weren't the ones replayed. Nobody has run that experiment.

The line I'd leave you with: task completion certifies the answer. It does not
certify the library.

## §5 — Adversarial review *(443 words · 3.4 min)*

Right. Let me attack both of those, because if I don't, one of you will, and I'd
rather do it properly.

Alita-G first, the fair criticisms. There's no limitations section. The tool
library is harvested from the same GAIA validation set it then reports scores on
— they disclose that, and it's defensible for a "become a domain expert" claim,
but it bounds what the number shows. And they measure their own library filling
with near-duplicates: effective coverage falls from 1.0 to 0.51 as the library
grows from 26 tools to 128. Their response is to stop generating at three
iterations.

Now the *unfair* criticisms, which I'm naming so we don't make them. They did
not ignore tool quality — their curation rule *is* the rule that got measured.
They did not forget library management — they decline it explicitly, and they
give a reason: preserving diversity to maximise coverage. Argue with that; don't
pretend it's absent. And they report their own regressions, which most papers
don't.

One number of theirs I wouldn't lean on. Their retrieval-threshold sweep swings
end-task accuracy by 16 points. That sounds damning. It's 25 questions. A
16-point swing is four questions. The instability is real; the effect size isn't
estimated.

Now the silent rot paper — our load-bearing citation, so this matters more.

One model, Haiku. Three seeds, eight sessions, 51 graded tasks out of 99. The
three protocols are reimplementations, not the original systems; the authors
deliberately say "style". And the originals of two of them assume reference test
suites this harness doesn't supply. So the hostile reading is: they removed the
guardrail, then measured the absence of the guardrail.

I'd concede all of it. 96.8 isn't "the rate". It's the rate in the one regime
anyone has measured.

What survives is enough. Hand-written reference implementations score a perfect
1.0 on all sixteen suites, so the suites are passable. And there's a matched pair
— same protocol, same model, same harness — where one tool scores 0.0 and
another scores 1.0, and that 1.0 reproduces identically across all three seeds.
The measurement discriminates. The failure is a property of unverified synthesis, not of the
measuring stick.

One more limit, and it's the one that constrains me most. That harness resets
between sessions. Libraries don't persist. So the paper measures tools that are
born broken. It does not measure a library rotting over a week.

> **[FIGURE 6 — the two-row thesis table]**
> The slide to photograph. Two rows only:
> **Born broken** — 96.8% of 222 tools at zero — *2604.00392, Table 5*
> **Decays as it grows** — effective coverage 1.00 → 0.51 — *Alita-G, Table 4*
> Footer, set large: **neither is caught by "did the task succeed".**
> **~12 s of silence. Do not talk over this one.**

Which splits the problem in two, and I think this is the actual conclusion.
Capabilities are born broken — that's the 96.8. And libraries decay as they grow
— that's Alita-G's own table. Different failure modes, different evidence.
Neither one is caught by asking "did the task succeed".

---

# ACT II — WHAT IS PROPOSED

## Act boundary *(43 words · 0.3 min)*

> **[FIGURE 7 — the wall]**
> A hard full-bleed divider. Above: *measured, published, by other people.*
> Below: *proposed. Not measured. Some not built.* No other content. This is the
> one slide whose entire job is to stop the two acts blurring. **~5 s.**

Everything so far is measured and published by other people.

Everything after this slide is what I think we should do about it. It is not
measured. Some of it isn't built yet. Please hold me to that line — including in
questions.

## §6 — What we need *(164 words · 1.3 min)*

> **[FIGURE 8 — the admission gate]**
> F1's ring again, with a gate dropped onto the *install* edge. Three labels
> feeding it: **declares what it needs · produces · touches**. One arrow out
> marked *rejected: declared ≠ observed*. Shows exactly where the contribution
> sits in a loop they've now seen three times. **~10 s.**

What we need is a check between "the system built a capability" and "the
capability is in the library". Right now there is nothing in that gap. Not in
any of these systems.

Three things, concretely. A capability declares what it needs, what it produces,
and what it touches — reads, writes, execution, network. That declaration is
checked mechanically before admission, not by a model. And if what it does
diverges from what it declared, it doesn't get in.

Two honest limits.

First, declaring isn't the novel part. Some systems already declare what a tool
requires and affects. The open part is fine-grained effects, checked
mechanically, before admission, and then actually used by the scheduler.

Second — and this matters if it ever runs on a shared machine — this is
admission, not containment. A contract decides what gets in. It doesn't sandbox
anything. What it buys you is that containment becomes tractable: declared
effects turn a sandbox from a guess into a policy.

## §7 — Certain what, uncertain how *(62 words · 0.5 min)*

> **[FIGURE 9 — open questions, grouped by who decides]**
> Three columns: **us** (is the contract a layer or a socket; what the check
> costs) · **supervisor** (scope, what we commit to) · **whoever runs the server**
> (credentials, egress, who approves a deployment). Turns Q&A toward the ask.
> **~8 s.**

So where I actually am.

High confidence on the *what*. Verification has to happen at the artifact, or
the library fills with things that run and are wrong. Three papers, three
levels, same answer.

Low confidence on the *how*. What the check is, where it sits, what it costs,
who signs off — all open.

That's what I'd like to talk about.

---

# Apparatus

## Allocation — measured, not estimated

| Movement | Words | Speaking | Figure |
|---|---|---|---|
| §0 The goal | 180 | 1.4 min | F1 self-extension loop |
| §1 MCP: is, and was | 256 | 2.0 min | F2 legacy vs modern |
| §2 A2A, short | 131 | 1.0 min | F3 the layers |
| §3 Alita-G | 226 | 1.7 min | F4 loop + Eq. 5 gate |
| §4 Beyond Task Completion | 230 | 1.8 min | F5 the 96.8% bar |
| §5 Adversarial review | 443 | 3.4 min | F6 two-row thesis |
| Act boundary | 43 | 0.3 min | F7 the wall |
| §6 What we need | 164 | 1.3 min | F8 admission gate |
| §7 Certain what, uncertain how | 62 | 0.5 min | F9 open questions |
| **Total** | **1,735** | **13.3 min** | 9 figures |
| **+ ~3.1 min staging** | | **~16.4 min** | ~90 s under the 17-min slot |

Being ~35 s under is the safe direction. §5 is deliberately the largest movement
— it is the one the supervisor will engage with, and the one that earns the
right to Act II.

## ⚠ Numbers said aloud — verify each against `DATA.md` before presenting

| Said | Value | Source | ✓ |
|---|---|---|---|
| MCP introduced | Nov 2024, Anthropic | **web, not our notes** | ☐ |
| MCP to Linux Foundation | Dec 2025 (AAIF; Anthropic/Block/OpenAI) | **web, not our notes** | ☐ |
| MCP became stateless | revision 2026-07-28 | `15-` §1 (live-fetched spec) | ☐ |
| A2A launched | Apr 2025, Google | **web, not our notes** | ☐ |
| A2A to Linux Foundation | Jun 2025 | **web, not our notes** | ☐ |
| Alita-G GAIA | 83.03 pass@1, from 75.15 | `DATA.md` §4 | ☐ |
| Alita-G tokens | ~15% fewer (12,305 → 10,394) | `DATA.md` §4 | ☐ |
| Effective coverage | 1.00 → 0.51; 26 → 128 tools | Alita-G Table 4 | ☐ |
| Retrieval swing | 16 points — **and n=25** | `21-` §4 | ☐ |
| Silent rot | 215 of 222 = 96.8% at C=0.00 | `DATA.md` §2, Table 5 | ☐ |
| Mean robustness | 0.52–0.54 | `DATA.md` §2 | ☐ |
| Reference implementations | C=1.00 on all 16 suites | `DATA.md` §2 | ☐ |
| Scope of the pilot | 1 model, 3 seeds, 8 sessions, 51/99 tasks | `DATA.md` §2 | ☐ |

⚠ The five **web** rows are the only facts in this talk not drawn from a paper
or the repo. Note `15-` covers MCP's *spec revisions* and never names Anthropic
or Google. Cite them as web sources if asked; do not attribute them to our notes.

## ⚠ Claims this talk must not make

Checked against `OUTLINE.md`'s 20-row guardrail table. The ones live in this
script:

- **Not** "capsules vs MCP" — a category error; the capsule schema *consumes*
  MCP (`bindings.mcp_capabilities`). §2 is written as layering, not rivalry.
- **Not** "we're more secure than MCP/A2A" — both ship threat models; we ship
  none. We secure a different layer: semantics and blast radius.
- **Not** "Alita-G ignores tool quality" / "forgot library management" — §5
  states both as explicitly-declined design positions.
- **Not** "96.8% is the rate" — it is the rate in one measured regime.
- **Not** "the immutable referee is ours" — DGM freezes its meta-loop and names
  an unmodifiable evaluator as future work. Not claimed anywhere in this script.
- **Not** "GAIA is directly comparable" — §3 says "their benchmark", never ours.
- **Never** the phrases *specification drift*, *hidden dependencies*, *interface
  violations*, *incomplete validation*. Zero occurrences in **both** papers.
- **Not** "Alita-G transfers to weaker agents" — ⚠ caught in adversarial review
  2026-09-11, after this script was drafted. Alita-G runs no such experiment and
  explicitly *distances* itself from AgentDistill's weaker-agent framing. The
  +54.3% weaker-agent lift is **SkillWeaver's**. Was spoken in §3; now removed.
- **Not** "tools violate their own specifications" — the synthesised tools carry
  no specification of their own. Say: zero on the held-out conformance suite for
  the capability they were built for.

## Cut list — in order, if you are running long

| Cut | Saves | Cost |
|---|---|---|
| §5 retrieval-threshold paragraph (16 points / n=25) | 38 w · 18 s | Loses a fair-minded aside; the argument holds |
| §1 Linux Foundation paragraph | 28 w · 13 s | Loses governance context; keep the dates |
| §6 second honest limit (admission ≠ containment) | 49 w · 23 s | Only if nobody from the server side is present |
| §4 "precise about what zero means" paragraph | 46 w · 21 s | **Expensive** — this is what makes rot *silent*. Cut last, if ever |

Total available: 161 words ≈ 75 s. Counts measured, not estimated.

You are unlikely to need this — the script runs ~35 s under the slot as written.
It is here for the case where the room interrupts, which with this supervisor is
the likely failure mode rather than overrunning prose.

## Expansion block — if Q&A is dropped and you have the full 20

Two inserts, ~180 words ≈ 80 s, taking the talk to ~18.5 min:

1. **After §4** — CoEvoSkills as the third level of the evidence chain: no
   skills 30.6% → unverified self-generated skills 30.7–34.1% (i.e. *the
   baseline*) → human-curated 53.5% → verified 71.1%. The line: unverified
   self-generation buys you nothing at all; verification is the entire delta.
   ⚠ 71.1%, not 75%. And the claim only holds *with* the verification loop —
   never say "agents beat human curation" unqualified.
2. **After §5** — DGM's node 114, which scored 2.0 by deleting the tool-use
   markers the *evaluator's* detector reads — and it did so with those checking
   functions hidden from it. Three levels, one finding: outcome-gated tools are broken,
   unverified skills are worthless, and an outcome-gated *agent* breaks its own
   gate.

## Backup slides — do not present; hold for Q&A

- **"Where did your numbers come from?"** — the citation map: which paper does
  which job (`who-checks-the-tools.html` §8).
- **"Has anyone checked these claims?"** — the corrections story. Two claims in
  our own notes were wrong and were caught on 2026-09-10: a fabricated
  failure-mode list attributed to 2604.00392 (and, found 2026-09-11, re-attributed
  to Alita-G as well), and an overclaim of novelty on the immutable referee. Both
  came from second-hand summaries; all nine papers are now read from source.
  ⚠ **Not in the main flow, deliberately** — these were never published and
  nobody in the room has read the documents containing them. The one transferable
  lesson, if asked: an adversarial review had already re-derived every claim in
  those notes and found seven errors, but it checked *repo* claims against the
  repo and never checked *paper* claims against the papers.
- **The full six-system scrutiny spectrum** — DGM → Alita-G → SkillWeaver →
  CoEvoSkills → SkillDAG, ordered by how much each trusts its own artifact.
  Payload: none of them requires a capability to declare what it will touch.
- **SkillDAG's independent confirmation** for §6 — "selecting the right subset
  becomes a structural problem rather than a similarity-matching one."

## Deliberate omissions

- **No repo tour.** Per `HANDOFF.md` §1: the goal is the subject, not the
  codebase. Capsule internals, manifest anatomy, and the 80-capsule inventory are
  all absent by choice.
- **No status claims.** No route counts, no test numbers, no "we have N capsules".
  Act I is other people's measurements; Act II is proposals. Our system's status
  is neither, and belongs in the report.
- **No evaluation design.** Track A / Track B and the pre-registered headline
  experiment are report material; at 17 minutes they would crowd out §5.
