Decisions and directives from **after** the 2026-09-23 workshop presentation. The deck as presented is
frozen at `merged/presented-2026-09-23/`; everything here applies to what follows it.

## How it went

Presented 2026-09-23. Ran **1 hour 40 minutes** including questions, against 39:20 of planned speaking.
Muk: "very good and answered questions well." Much of the sharper conceptual material below was delivered live rather than from the slides, which is why it is only now being written down.

**The schema page showing what verification reads and what RSI reads was supported live, in the room, by
the RSI owner and the verification owner, for both the hot path and the cold path.** That makes it
agreed design rather than a proposal, and the deck now says so in the speaker notes. See
[[Declared vs Observed]] and [[Self-Improvement]].

**The verification presentation independently reached for Kubernetes admission control as its example**,
the same one already on our agreement slide. Corroboration from another team in the same workshop is the
strongest form of the argument in [[Inspiration from Other Software]].

## Decisions

| Question | Decision |
|---|---|
| Does a capsule hold code? | **No. It points, always.** `identity.code_id {ref, sha256}` is the id of the code plus the hash that id must resolve to. This closes what SCHEMA.md 0.2 held open that morning. The schema implements it as `identity.carrier` plus `identity.body[].sha256`; the name `code_id` is a naming mismatch, see [[Open Questions]] |
| Leaf or composite | **Either, never both.** A leaf carries `code_id`; a composite carries `members[]` and a DAG. Now enforced in `capsule.schema.json`. |
| What the external gate is built from | **Both, at different times.** Admission's suite is bound to the declaration via `contract_hash`. The step gate reads the declaration as a floor but also tests what the request needs, which is why 4.6 says it is not redundant with admission. |
| The one industry example for importing capability | **MCP.** A server declares its tools and schemas, any client imports them. |
| Where the two reasons for the layer live | A new opening slide for requirement a, ahead of the four verbs. |

## The model, as Muk stated it

- **A hat on a head.** The capsule is the hat, the code is the head, and the hash is how a changed head
  is noticed rather than trusted.
- **Capsules contain capsules.** Unless a capsule is one skill or function, it holds an optional DAG of
  other capsules, or the id of the code that performs what it guarantees.
- **Some sections of the workflow are handled by capsules, and each handled section is many capsules
  connected** — not one capsule per stage, which is what the figure used to draw.
- **No capsule is its own final judge.** Internal checks are allowed but are never evidence, and
  someone else's gate always applies. See [[The Ceiling]].
- **Tests and gates carry IDs.** The space cost is accepted, because provenance and RSI need it.
- **Why the workflow can never be a capsule, compositionally:** a composite is made of capsules and
  nothing else can be a member; gates and deciders can never be capsules, or RSI would be editing its
  own guards and checks; the workflow contains gates and deciders. So it would need members that cannot
  be members. It is not that the workflow is too big, it is that it cannot be composed at all.
- **What cannot be a capsule**, stated plainly: the modules that control the workflow, the gates, and
  the planner and library that act on and verify capsules.
- **Parentage is a tree, not a chain.** GitHub repositories branch and fork, and the latest commit is
  not always the best one. See [[Versioning and A-prime]].
- **Why spatiotemporal composability is last.** Across software, authors do not write code that undoes
  itself: RAII hands cleanup to the destructor, a collector reclaims what nobody holds. Making every
  author write undo adds work against the grain, and a poisoned context never truly reverses. So the
  author declares *whether* it can be undone, not how. See [[Capability Capsule]].
- **Why declaring matters, in its deepest form: value does not exist without a goal.** Better, correct
  and improved are not properties of code, they are relations between code and something stated. With
  no declaration there is nothing to measure against, so there is no verification and no
  self-improvement either. The shorter version for the room is **we cannot check something that claims
  nothing**.

## Supervisor's method note, for future work

> Make targets clear, see what others did, then copy it. It is the easiest way to convince others and so
> much easier to explain. "I want to make GPT-6 but better" against "I am going to put TensorRT as the
> structure for my CC optimizer."

With the honest qualifier that goes with it: **CC itself is not already done. Its components exist and
have backing.** The assembly is what is ours. That line now closes the agreement slide.

Related: **staged items are good, but the target must exist and be clear.** Staging is appended
information about when each part starts being enforced. It is never what we present as the goal.

## Two artifact bugs found and fixed

Both are the same class as the `wiring` omission found earlier that day: `SCHEMA.md` specified
something the normative artifact did not implement, so a conforming declaration was rejected.

1. **`guarantees.checks[]` was missing eight of the fields 3.1 specifies** (`anchor`, `over`, `author`,
   `written_before_body`, `held_out`, `signal_source`, `owner`, `assurance`) while setting
   `additionalProperties: false`. A check written to spec was rejected. These are exactly the provenance
   fields the IDs decision depends on.
2. **Leaf-or-composite was unenforced.** `body`, `remote`, `members`, `structure` and `wiring` were all
   optional siblings, so a capsule could be both shapes at once.

Also fixed, in the position figure: `planning` appeared both as a stage drawing from a capsule and in
the control band that is never a capsule, and `delivery` was missing entirely.
