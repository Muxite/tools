# 26 — Where this actually runs, and what that makes the gate

Written 2026-09-10 by the capability-capsule panel (pts/9), from the user's
design brief. This note is **goal-driven**: it describes what the system should
be, per the user's instruction that "the most important thing is our goal and
not what code we currently have." Repo references appear only where they
support a design claim.

---

## 1. The deployment picture, as stated

> "I think AI4Research is gonna end up heavily using **API-based non-local
> models**. I remember they said **macOS was priority, then Linux, then
> Windows** — that might change. This makes me think it just runs on the user's
> computer. IMO the very idea of **long-running AI4Research should be running on
> a server** somewhere on a university or company server, or even cloud, if it's
> gonna run for days. **Security is a concern in this case.**"

Three separable facts, and they pull in different directions:

| | Implication |
|---|---|
| **API-based models** | Local compute stops being the binding constraint. Cost and egress become binding instead |
| **Desktop OS priority** | The *interactive* product is a workstation tool |
| **Multi-day runs belong on a server** | The *autonomous* product is a service, and it is the one this design targets |

**The resolution is that these are two deployment modes of one system, not a
contradiction** — and the capsule design should say which mode it is designed
for. The short-session interactive mode is where a human is present to approve
things. The multi-day autonomous mode is where nobody is. **The admission gate
exists for the second mode.** That is the framing to carry into the report.

## 2. Why this upgrades the thesis rather than complicating it

The single most useful sentence to come out of this conversation:

> **On a single-user workstation, "what will this capability do to me" is a
> hygiene question. On a shared server, running unattended for days, holding API
> credentials with network egress, it is an access-control question.**

Everything the capsule declares — `effects` (read / write / execute / network),
the effect ceiling, `trust_class`, `operator_compatibility`, `provenance` —
reads as engineering tidiness on a laptop. On shared infrastructure the same
declarations are a **security control**, and a fail-closed admission gate is an
authorization decision.

This matters for the report because it changes who the argument has to convince.
"We check our generated tools conform to their specs" is a quality argument a
supervisor can take or leave. "**No capability runs on this server unless it has
declared what it will touch, and the declaration was checked**" is an argument
whoever administers the server has to care about. It is much harder to wave
away, and it is the same mechanism either way.

**Report placement:** this belongs *before* the two gates, as the motivation for
them, not after as a consideration.

## 3. What is different about multi-day autonomous operation

Four properties, none of which apply to an interactive session, and each of
which independently argues for admission control:

1. **No human is in the loop at the moment of use.** The existing
   `effect_escalation_requires_human` policy assumes someone is there to
   escalate to. Over a multi-day run, either escalation blocks the run for hours
   or it is pre-authorized — and pre-authorization is exactly a declared effect
   ceiling checked at admission.
2. **Duration multiplies blast radius.** A capability with an undeclared write
   or network effect, invoked once interactively, is a bug. The same capability
   invoked on a loop for three days is an incident.
3. **The system is generating its own capabilities while unattended.** This is
   the property nothing else in the deployment story has. Every other server
   workload runs code that a human wrote and someone reviewed. This one writes
   code, admits it, and runs it, with no human between those steps.
4. **Credentials are resident.** API-based models mean provider keys are in the
   environment for the whole run. Any generated capability with `network` effect
   is, by construction, in reach of them unless something prevents it.

Point 3 is the one to lead with. **It is not a variation on ordinary server
security; it is a workload class that ordinary server security has no story
for.** That is the gap the capsule fills, and saying so plainly is the strongest
version of the pitch.

## 4. The threat model, stated plainly

Worth writing out, because a supervisor deciding whether this may run on a
university machine will construct it anyway, and it is better to have done it
first.

| # | Threat | Mechanism | What the capsule contributes |
|---|---|---|---|
| T1 | **Credential exfiltration** | generated capability with undeclared `network` effect reads env/keyring and posts outward | `EFFECT_UNDECLARED` at admission; effects are compared against statically-observed behaviour |
| T2 | **Unintended write / destruction** | undeclared `write` effect outside the run's scope | declared write scope + effect ceiling inherited from the authorizing task |
| T3 | **Effect escalation over time** | a capability admitted narrowly is later invoked in a wider context | the ceiling is a property of the *task*, not the capability, so it re-applies at each use |
| T4 | **Supply-chain via generated dependencies** | generated code pulls a package at run time | `execute` + `network` declaration; a capability that installs things must say so |
| T5 | **Prompt injection through retrieved content** | research content steers generation toward a malicious capability | admission is a *mechanical* check, not a model judgement — this is the reason the referee must not be model-driven |
| T6 | **Cross-tenant blast radius** | shared server, several users or projects | provenance + applicability scoping; a capability harvested in one context is not automatically admissible in another (`23-` §6) |
| T7 | **Resource exhaustion** | unbounded generation or invocation over days | generation rate limits; the cost meter that the design specifies |

**T5 deserves its own line in the report.** A self-extending system that reads
untrusted documents to decide what capability to build has an injection surface
that no benchmark measures. It is also the cleanest argument for the rule in
`25-` §3 — *the actor may improve, the referee may not*. If the referee were
itself a model reading the same content, the check would be compromised by the
same input it is meant to defend against. **Determinism in the gate is a
security property, not just a reproducibility one.**

## 5. The honest limit: a capsule is admission, not containment

The design documents specify an **Execution Sandbox** with four parts —
resource limiter, network filter, time guard, cost meter — and it is **not
built** (`11-` §11). More importantly, `11-` records the conceptual boundary
directly: *capsules constrain who may run; they do not themselves sandbox.*

That distinction must survive into the report, because conflating them is the
easiest way to lose credibility with anyone who does security for a living:

- **Admission** decides whether a capability is *allowed* to run, based on what
  it declared and what was checked. It is a policy decision, made once.
- **Containment** limits what a running capability *can* do regardless of what
  it declared. It is an enforcement mechanism, active throughout execution.

**Admission without containment is a system that trusts its own analysis.** For
T1 and T4 in particular — where the threat is precisely that the static analysis
missed something — the honest statement is that admission raises the cost of the
attack and does not eliminate it.

So the position to take:

> The admission contract is necessary and not sufficient. It is what makes
> containment *tractable* — a sandbox that knows a capability declared no
> network effect can deny network unconditionally, which is a far easier policy
> to write than one that must infer intent. **Declared effects are what turn a
> sandbox from a guess into a policy.**

That is a genuinely good argument, it is honest about the gap, and it makes the
unbuilt sandbox a **roadmap item with a clear specification** rather than an
embarrassment. Pair the two in the report and neither looks weak.

## 6. What the survey already says

2507.21046's safety section names *"unconstrained generation of code risks
creating tools with exploitable vulnerabilities"* and identifies **automated
verification and sandboxing** as critical open problems (`17-` §2.6).

Those are exactly the two halves of §5. The field has named the problem and not
solved it; this design proposes the verification half and specifies the
containment half. **Being able to say "the survey names two open problems and we
address one and specify the other" is a strong, checkable positioning claim** —
much better than claiming novelty outright.

## 7. What changes in the compute argument

Note `24-` was written assuming local-first. With API-based generation:

- **The generation model no longer competes for local resources.** The GPU
  contention argument in `24-` §4 largely dissolves, and §4's warning about a
  large local encoder becomes much cheaper to ignore.
- **The cold-path / hot-path asymmetry survives and improves.** A server has
  idle capacity between runs; conformance checking is exactly the kind of work
  that fits there. `24-` §3 gets *stronger* under server deployment.
- **Token cost becomes money.** Alita-G's ~15% mean-token reduction is a
  latency footnote on a workstation and a line item on an API bill over a
  multi-day run. Cite it as an efficiency result with a commercial reading.
- **Egress replaces compute as the binding constraint.** What the system may
  *reach* matters more than what it can compute — which points back at effect
  declaration.

`24-` is amended to mark its local-first framing as conditional rather than
assumed.

## 8. Open questions this adds

- **Q22 — Which deployment mode is the design target?** Interactive workstation,
  autonomous server, or both with different admission policies? *Recommendation:
  both, with the gate strict by default and relaxable only interactively.*
- **Q23 — Who owns the credentials, and what is their scope?** Per-run,
  per-user, or a shared service identity? This decides how bad T1 is.
- **Q24 — What egress is permitted by default?** Deny-by-default with declared
  allowances is the design that matches the effect vocabulary; anything else
  makes `network` declarations advisory.
- **Q25 — Is the run multi-tenant?** If several users or projects share the
  server, T6 becomes primary and provenance scoping becomes mandatory rather
  than desirable.
- **Q26 — Does the sandbox get built?** If not, the report must say plainly that
  admission is the only control, and what that leaves open.
- **Q27 — Who approves a deployment?** Whoever administers a university or
  company server is a second audience for this argument, with different
  standards from the supervisor.
